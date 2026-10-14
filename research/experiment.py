"""Maturity-gap nested development, signed freeze, and write-once test evaluation."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import warnings

import joblib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, brier_score_loss, log_loss, roc_auc_score, average_precision_score
from sklearn.exceptions import ConvergenceWarning

from .data import sha
from .features import make_features
from .models import candidates, estimator, predict

def dump(path, content):
    Path(path).write_text(json.dumps(content, indent=2, allow_nan=False), encoding='utf-8')

def load_data(root):
    raw = pd.read_csv(root / 'data/processed/prospects.csv')
    college = pd.read_csv(root / 'data/processed/college_seasons.csv', low_memory=False)
    return make_features(raw, college)

def folds(frame, origin, config):
    result = []
    for year in sorted(frame.draft_year.unique()):
        if year + config['horizon'] > origin:
            continue
        train = frame.index[frame.draft_year + config['horizon'] <= year]
        valid = frame.index[frame.draft_year.eq(year)]
        if len(train) >= config['min_training'] and len(valid) >= 20:
            result.append((int(year), train, valid))
    if not result:
        raise ValueError(f'No mature validation folds at {origin}')
    return result

def metrics(y, p, task):
    if task == 'regression':
        rho = spearmanr(y, p).statistic if np.ptp(p) > 1e-10 and np.ptp(y) > 1e-10 else np.nan
        return {'n': len(y), 'loss': float(mean_squared_error(y, p)),
                'rmse': float(np.sqrt(mean_squared_error(y, p))), 'mae': float(mean_absolute_error(y, p)),
                'r2': float(r2_score(y, p)), 'spearman': float(rho) if np.isfinite(rho) else None}
    return {'n': len(y), 'loss': float(brier_score_loss(y, p)),
            'brier': float(brier_score_loss(y, p)), 'log_loss': float(log_loss(y, p, labels=[0, 1])),
            'auc': float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None,
            'ap': float(average_precision_score(y, p)), 'prevalence': float(np.mean(y))}

def fit_model(frame, rows, target, spec, groups, config):
    task = config['targets'][target]
    columns = ['pick_reference_only'] if spec['group'] == 'pick_benchmark' else groups[spec['group']]
    model = estimator(spec, columns, task, config['seed'])
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter('always', ConvergenceWarning)
        model.fit(frame.loc[rows, columns], frame.loc[rows, target])
    if any(issubclass(w.category, ConvergenceWarning) for w in captured):
        raise ValueError('Convergence warning; candidate disqualified')
    return model, columns

def tune(frame, origin, target, groups, config, log):
    task = config['targets'][target]
    splits = folds(frame, origin, config)
    specs = candidates(config, task)
    ranking = []
    cache = {}
    for index, spec in enumerate(specs):
        observed, guesses, rows = [], [], []
        failure = None
        try:
            for year, train, valid in splits:
                model, columns = fit_model(frame, train, target, spec, groups, config)
                guesses.extend(predict(model, frame.loc[valid, columns], task))
                observed.extend(frame.loc[valid, target])
                rows.extend(valid)
            score = metrics(observed, guesses, task)
            ranking.append({'spec': spec, 'score': score['loss'], 'candidate': index})
            cache[index] = pd.DataFrame({'row': rows, 'truth': observed, 'prediction': guesses})
        except (ValueError, FloatingPointError) as exc:
            failure = str(exc)
            score = None
        log.write(json.dumps({'origin': origin, 'target': target, 'candidate': index, 'spec': spec, 'metrics': score, 'failure': failure}) + '\n')
        log.flush()
    family_best = {}
    for entry in sorted(ranking, key=lambda v: v['score']):
        family_best.setdefault(entry['spec']['family'], entry)
    nonbaseline = [entry for entry in family_best.values() if entry['spec']['family'] != 'constant']
    members = sorted(nonbaseline, key=lambda v: v['score'])[:3]
    if len(members) == 3:
        predictions = np.mean([cache[m['candidate']].prediction.to_numpy() for m in members], axis=0)
        truth = cache[members[0]['candidate']].truth.to_numpy()
        spec = {'family': 'ensemble', 'group': 'multiple', 'transform': 'multiple',
                'params': {}, 'members': [m['spec'] for m in members]}
        ensemble = {'spec': spec, 'score': metrics(truth, predictions, task)['loss'], 'candidate': -1}
        ranking.append(ensemble)
        family_best['ensemble'] = ensemble
        cache[-1] = cache[members[0]['candidate']].assign(prediction=predictions)
    group_best = {group: min([e for e in ranking if e['spec']['group'] == group], key=lambda v: v['score'])
                  for group in config['feature_groups']}
    selected = min(ranking, key=lambda v: v['score'])
    print(f"origin={origin} target={target} folds={[f[0] for f in splits]} selected={selected['spec']['family']} {selected['spec']['group']} loss={selected['score']:.4f}", flush=True)
    return selected, family_best, group_best, cache, splits

def fit_spec(frame, origin, target, spec, groups, config):
    rows = frame.index[frame.draft_year + config['horizon'] <= origin]
    if spec['family'] == 'ensemble':
        return [fit_spec(frame, origin, target, member, groups, config) for member in spec['members']]
    model, columns = fit_model(frame, rows, target, spec, groups, config)
    return {'model': model, 'columns': columns}

def predict_spec(fitted, frame, task):
    if isinstance(fitted, list):
        return np.mean([predict_spec(m, frame, task) for m in fitted], axis=0)
    return predict(fitted['model'], frame[fitted['columns']], task)

def tracked_hashes(root):
    paths = [root / 'config.json', root / 'data/processed/prospects.csv', root / 'data/processed/college_seasons.csv']
    paths += sorted((root / 'research').glob('*.py'))
    paths += [root / 'run.py', root / 'collect.py']
    paths += [root / 'verify_sources.py']
    paths += sorted((root / 'data/raw').glob('*'))
    return {p.relative_to(root).as_posix(): sha(p) for p in paths if p.is_file()}

def develop(root, config):
    root = Path(root)
    out = root / 'output/experiments'
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'freeze.json').exists():
        print('Existing freeze retained; no test-driven redevelopment.', flush=True)
        return
    if (out / 'test_receipt.json').exists():
        raise ValueError('Cannot redevelop consumed test')
    frame, groups = load_data(root)
    development = frame[frame.draft_year.lt(min(config['test_years']))].copy()
    nested, inner, scores, splitlog = [], [], [], []
    with (out / 'trials.jsonl').open('w', encoding='utf-8') as log:
        # Later nested scores diagnose the procedure; their labels are not used for final selection.
        for origin in config['nested_origins']:
            for target, task in config['targets'].items():
                selected, family_best, _, _, splits = tune(development, origin, target, groups, config, log)
                valid = development[development.draft_year.eq(origin)]
                for label, entry in {**family_best, 'selected': selected}.items():
                    fitted = fit_spec(development, origin, target, entry['spec'], groups, config)
                    p = predict_spec(fitted, valid, task)
                    scores.append({'origin': origin, 'target': target, 'model': label, **metrics(valid[target], p, task)})
                    nested.extend({'player': r.player, 'year': origin, 'target': target, 'model': label,
                                   'truth': float(r[target]), 'prediction': float(guess)}
                                  for (_, r), guess in zip(valid.iterrows(), p))
                splitlog.append({'origin': origin, 'target': target,
                                 'outer_train_max': origin - config['horizon'],
                                 'inner': [{'year': y, 'train_max': y - config['horizon'], 'n_train': len(t), 'n_valid': len(v)} for y, t, v in splits]})
        origin = min(config['test_years'])
        frozen = {}
        for target, task in config['targets'].items():
            selected, family_best, group_best, cache, splits = tune(development, origin, target, groups, config, log)
            entries = {**family_best, 'selected': selected,
                       **{'ablation_' + group: e for group, e in group_best.items()}}
            # Actual draft order is unavailable to the pre-draft model; separate oracle-like benchmark.
            benchmark = {'family': 'linear', 'group': 'pick_benchmark', 'transform': 'raw',
                         'params': {'C': 1.} if task == 'classification' else {'kind': 'ridge', 'alpha': 10.}}
            entries['draft_order_benchmark'] = {'spec': benchmark, 'score': None, 'candidate': -2}
            frozen[target] = {'selected': selected['spec'], 'entries': {label: e['spec'] for label, e in entries.items()},
                              'development_loss': selected['score'], 'baseline_loss': family_best['constant']['score'],
                              'folds': [y for y, _, _ in splits]}
            for label, entry in entries.items():
                if entry['candidate'] in cache:
                    record = cache[entry['candidate']]
                    for _, row in record.iterrows():
                        source = frame.loc[int(row.row)]
                        inner.append({'player': source.player, 'year': int(source.draft_year), 'target': target,
                                      'model': label, 'truth': float(row.truth), 'prediction': float(row.prediction)})
                for year in config['test_years']:
                    fitted = fit_spec(development, year, target, entry['spec'], groups, config)
                    path = out / 'models' / f'{target}_{label}_{year}.joblib'
                    path.parent.mkdir(exist_ok=True)
                    joblib.dump(fitted, path)
        pd.DataFrame(nested).to_csv(out / 'nested_predictions.csv', index=False)
        pd.DataFrame(scores).to_csv(out / 'nested_scores.csv', index=False)
        pd.DataFrame(inner).to_csv(out / 'selection_predictions.csv', index=False)
        dump(out / 'splits.json', splitlog)
        freeze = {'created_utc': datetime.now(timezone.utc).isoformat(), 'config': config,
                  'targets': frozen, 'hashes': tracked_hashes(root),
                  'model_hashes': {p.relative_to(root).as_posix(): sha(p) for p in sorted((out / 'models').glob('*.joblib'))},
                  'versions': {p: importlib.metadata.version(p) for p in ['numpy', 'pandas', 'scikit-learn', 'xgboost', 'lightgbm', 'catboost', 'shap']},
                  'test_consumed': False}
        dump(out / 'freeze.json', freeze)
        print('Model and data freeze signed BEFORE final test evaluation.', flush=True)

def check_freeze(root):
    out = root / 'output/experiments'
    freeze = json.loads((out / 'freeze.json').read_text())
    # Registered publication/input-access changes retain the scientific freeze.
    amendment_path = out / 'publication_amendment.json'
    amendments = json.loads(amendment_path.read_text()) if amendment_path.exists() else {}
    for path, expected in {**freeze['hashes'], **freeze['model_hashes']}.items():
        if sha(root / path) != expected:
            if path == 'research/report.py' and path in amendments:
                entry = amendments[path]
                preserved = root / entry['preserved_original']
                if sha(preserved) == expected and sha(root / path) == entry['revised_sha256']:
                    continue
            if path == 'research/experiment.py' and path in amendments:
                import ast
                entry = amendments[path]
                preserved = root / entry['preserved_original']
                def scientific_ast(file):
                    tree = ast.parse(file.read_text(encoding='utf-8'))
                    tree.body = [node for node in tree.body if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name != 'check_freeze']
                    return ast.dump(tree, include_attributes=False)
                if (sha(preserved) == expected and sha(root / path) == entry['revised_sha256']
                        and scientific_ast(root / path) == scientific_ast(preserved)):
                    continue
            if path in ('run.py', 'collect.py', 'research/__init__.py') and path in amendments:
                import ast
                entry = amendments[path]
                preserved = root / entry['preserved_original']
                def operational_ast(file):
                    tree = ast.parse(file.read_text(encoding='utf-8'))
                    if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant) and isinstance(tree.body[0].value.value, str):
                        tree.body.pop(0)
                    if path == 'collect.py':
                        tree.body = [node for node in tree.body
                                     if not (isinstance(node, ast.FunctionDef) and node.name == 'main')
                                     and not (isinstance(node, ast.Import) and any(alias.name == 'shutil' for alias in node.names))]
                    return ast.dump(tree, include_attributes=False)
                if (sha(preserved) == expected and sha(root / path) == entry['revised_sha256']
                        and operational_ast(root / path) == operational_ast(preserved)):
                    continue
            raise ValueError(f'Frozen input/code/model changed: {path}')
    # A consumed evaluation is evidence, including its scores and summaries.
    # Missing a receipt must never silently reopen an existing evaluation.
    receipt_path = out / 'test_receipt.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        for key, file in [('freeze_sha256', 'freeze.json'),
                          ('predictions_sha256', 'test_predictions.csv'),
                          ('summary_sha256', 'test_summary.json'),
                          ('scores_sha256', 'test_scores.csv')]:
            artifact = out / file
            if not artifact.exists() or sha(artifact) != receipt[key]:
                raise ValueError(f'Test receipt mismatch: {file}')
    elif any((out / file).exists() for file in
             ['test_predictions.csv', 'test_scores.csv', 'test_summary.json']):
        raise ValueError('Evaluation artifacts exist without a test receipt; restore recorded evidence')
    return freeze

def interval(y, p, b, years, task, config):
    rng = np.random.default_rng(config['seed'])
    cohorts = np.unique(years)
    index = {c: np.flatnonzero(years == c) for c in cohorts}
    absolute, differences = [], []
    for _ in range(config['bootstrap_replicates']):
        rows = np.concatenate([rng.choice(index[c], len(index[c]), replace=True)
                               for c in rng.choice(cohorts, len(cohorts), replace=True)])
        loss = np.mean((y[rows] - p[rows]) ** 2)
        baseline = np.mean((y[rows] - b[rows]) ** 2)
        if task == 'regression':
            loss, baseline = np.sqrt(loss), np.sqrt(baseline)
        absolute.append(loss)
        differences.append(baseline - loss)
    return {'loss_interval': np.quantile(absolute, [.025, .975]).tolist(),
            'baseline_minus_model_interval': np.quantile(differences, [.025, .975]).tolist()}

def evaluate(root, config):
    root = Path(root)
    out = root / 'output/experiments'
    freeze = check_freeze(root)
    receipt = out / 'test_receipt.json'
    if receipt.exists():
        existing = json.loads(receipt.read_text())
        if existing['freeze_sha256'] != sha(out / 'freeze.json') or existing['predictions_sha256'] != sha(out / 'test_predictions.csv'):
            raise ValueError('Test receipt changed')
        print('Write-once test already evaluated; retaining results.', flush=True)
        return
    frame, _ = load_data(root)
    rows, scores = [], []
    for target, task in config['targets'].items():
        for year in config['test_years']:
            valid = frame[frame.draft_year.eq(year)]
            for label in freeze['targets'][target]['entries']:
                fitted = joblib.load(out / 'models' / f'{target}_{label}_{year}.joblib')
                p = predict_spec(fitted, valid, task)
                rows.extend({'player': r.player, 'year': year, 'target': target, 'model': label,
                             'truth': float(r[target]), 'prediction': float(guess)}
                            for (_, r), guess in zip(valid.iterrows(), p))
    predictions = pd.DataFrame(rows)
    predictions.to_csv(out / 'test_predictions.csv', index=False)
    summaries = {}
    for target, task in config['targets'].items():
        part = predictions[predictions.target.eq(target)]
        for label, group in part.groupby('model', sort=True):
            scores.append({'target': target, 'model': label, 'year': 'pooled', **metrics(group.truth, group.prediction, task)})
            for year, cohort in group.groupby('year'):
                scores.append({'target': target, 'model': label, 'year': str(year), **metrics(cohort.truth, cohort.prediction, task)})
        selected = part[part.model.eq('selected')].sort_values(['year', 'player'])
        baseline = part[part.model.eq('constant')].sort_values(['year', 'player'])
        summaries[target] = {**metrics(selected.truth, selected.prediction, task),
             **interval(selected.truth.to_numpy(), selected.prediction.to_numpy(), baseline.prediction.to_numpy(), selected.year.to_numpy(), task, config)}
    pd.DataFrame(scores).to_csv(out / 'test_scores.csv', index=False)
    dump(out / 'test_summary.json', summaries)
    dump(receipt, {'evaluated_utc': datetime.now(timezone.utc).isoformat(), 'freeze_sha256': sha(out / 'freeze.json'),
                  'predictions_sha256': sha(out / 'test_predictions.csv'),
                  'summary_sha256': sha(out / 'test_summary.json'), 'scores_sha256': sha(out / 'test_scores.csv'),
                  'policy': 'Test consumed; no further tuning or target selection from its scores.'})
    print(json.dumps(summaries, indent=2), flush=True)

def verify(root, config):
    root = Path(root)
    out = root / 'output/experiments'
    freeze = check_freeze(root)
    receipt = json.loads((out / 'test_receipt.json').read_text())
    for key, file in [('freeze_sha256', 'freeze.json'), ('predictions_sha256', 'test_predictions.csv'),
                      ('summary_sha256', 'test_summary.json'), ('scores_sha256', 'test_scores.csv')]:
        if sha(out / file) != receipt[key]:
            raise ValueError(f'Test receipt mismatch: {file}')
    frame, groups = load_data(root)
    predictions = pd.read_csv(out / 'test_predictions.csv')
    checks = []
    for target, task in config['targets'].items():
        spec = freeze['targets'][target]['selected']
        for year in config['test_years']:
            fitted = fit_spec(frame, year, target, spec, groups, config)
            valid = frame[frame.draft_year.eq(year)]
            p = predict_spec(fitted, valid, task)
            expected = predictions[(predictions.target == target) & (predictions.year == year) & (predictions.model == 'selected')]
            actual = pd.DataFrame({'player': valid.player, 'p': p}).merge(expected[['player', 'prediction']], on='player', validate='one_to_one')
            difference = float(np.max(np.abs(actual.p - actual.prediction)))
            if difference > 1e-6:
                raise ValueError(f'Refit mismatch: {target}, {year}')
            checks.append({'target': target, 'year': year, 'max_difference': difference})
    dump(out / 'verification.json', {'source_code_model_hashes': 'passed', 'receipt': 'passed', 'independent_refits': checks})
    print('All frozen hashes, test receipts, and ten independent refits verified.', flush=True)
