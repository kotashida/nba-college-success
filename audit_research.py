"""Independently audit recorded research without tuning or replacing test artifacts.

Reconstructs targets directly from raw NBA rows and recalculates metrics and
paired intervals. Outputs are audit evidence only, never new selection scores.
"""
from pathlib import Path
import hashlib
import json

import joblib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score, average_precision_score

from research.experiment import check_freeze, load_data, predict_spec

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def calculate(y, p, task):
    """Explicit loss formulas independent of research.experiment.metrics."""
    y, p = np.asarray(y, float), np.asarray(p, float)
    loss = float(np.mean(np.square(y - p)))
    if task == 'regression':
        rho = spearmanr(y, p).statistic if np.ptp(p) > 1e-10 and np.ptp(y) > 1e-10 else None
        return dict(n=len(y), loss=loss, rmse=float(np.sqrt(loss)),
                    mae=float(np.mean(np.abs(y - p))),
                    r2=float(1 - np.square(y - p).sum() / np.square(y - y.mean()).sum()),
                    spearman=None if rho is None else float(rho))
    # Stored probabilities are already clipped by the frozen prediction interface.
    return dict(n=len(y), loss=loss, brier=loss,
                log_loss=float(-np.mean(y * np.log(p) + (1 - y) * np.log1p(-p))),
                auc=float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None,
                ap=float(average_precision_score(y, p)), prevalence=float(y.mean()))


def compare(actual, expected, context, rtol=1e-10, atol=1e-8):
    for key, value in actual.items():
        other = expected[key]
        if value is None:
            if other is not None and not pd.isna(other):
                raise ValueError(f'{context}: {key} null mismatch')
        elif not np.isclose(value, other, atol=atol, rtol=rtol):
            raise ValueError(f'{context}: {key}: {value} != {other}')


def main():
    out = ROOT / 'output/experiments'
    freeze = check_freeze(ROOT)
    config = freeze['config']
    protected = ['freeze.json', 'test_receipt.json', 'test_predictions.csv',
                 'test_scores.csv', 'test_summary.json']
    before = {f: digest(out / f) for f in protected}
    prospects = pd.read_csv(ROOT / 'data/processed/prospects.csv')
    nba = pd.read_csv(ROOT / 'data/raw/nba_advanced.csv')
    nba = nba[nba.lg.eq('NBA') & nba.season.ge(1995)]
    # Independent implementation of total-row precedence; no production target helpers.
    records = []
    for (pid, season), rows in nba.groupby(['player_id', 'season']):
        total = rows[rows.team.eq('TOT') | rows.team.str.fullmatch(r'\d+TM')]
        if len(total) > 1:
            raise ValueError('Duplicate season totals')
        chosen = total if len(total) else rows
        if chosen.team.duplicated().any():
            raise ValueError('Duplicate team stints')
        values = chosen[['vorp', 'mp', 'g', 'gs']].apply(pd.to_numeric, errors='raise')
        if values.isna().any().any():
            raise ValueError('Missing raw NBA target field')
        records.append(dict(nba_id=pid, season=int(season), **values.sum().to_dict()))
    canonical = pd.DataFrame(records)
    target_checks = 0
    for row in prospects.itertuples():
        window = canonical[canonical.nba_id.eq(row.nba_id) &
                           canonical.season.between(row.draft_year + 1, row.draft_year + config['horizon'])]
        reconstructed = dict(vorp5=window.vorp.sum(), minutes5=window.mp.sum(),
                             active5=window.g.gt(0).sum(),
                             rotation5=int(window.mp.ge(1000).sum() >= 3),
                             starter5=int(window.gs.ge(41).sum() >= 2))
        compare(reconstructed, row._asdict(), row.player)
        target_checks += len(reconstructed)
    # Independent appearance snapshot check; it shares the original provider.
    per_game = pd.read_csv(ROOT / 'data/raw/nba_per_game.csv')
    appearances = per_game[per_game.lg.eq('NBA') & per_game.season.between(2009, 2026)]
    missing = appearances[['player_id', 'season']].drop_duplicates().merge(
        canonical[['nba_id', 'season']], left_on=['player_id', 'season'],
        right_on=['nba_id', 'season'], how='left', indicator=True)
    if missing._merge.eq('left_only').any():
        raise ValueError('Per-game appearance missing from advanced archive')
    scores = pd.read_csv(out / 'test_scores.csv', dtype={'year': str})
    predictions = pd.read_csv(out / 'test_predictions.csv')
    if predictions.duplicated(['player', 'year', 'target', 'model']).any():
        raise ValueError('Duplicated test predictions')
    metric_checks = 0
    for score in scores.to_dict('records'):
        rows = predictions[(predictions.target == score['target']) & (predictions.model == score['model'])]
        if score['year'] != 'pooled':
            rows = rows[rows.year.eq(int(score['year']))]
        compare(calculate(rows.truth, rows.prediction, config['targets'][score['target']]), score,
                f"{score['target']}/{score['model']}/{score['year']}")
        metric_checks += 1
    summary = json.loads((out / 'test_summary.json').read_text())
    for target, task in config['targets'].items():
        selected = predictions[(predictions.target == target) & (predictions.model == 'selected')]
        baseline = predictions[(predictions.target == target) & (predictions.model == 'constant')]
        pair = selected.merge(baseline, on=['player', 'year', 'target'],
                              suffixes=('_s', '_b'), validate='one_to_one').sort_values(['year', 'player'])
        if len(pair) != len(prospects[prospects.draft_year.isin(config['test_years'])]):
            raise ValueError('Incomplete selected/baseline pairing')
        np.testing.assert_allclose(pair.truth_s, pair.truth_b)
        compare(calculate(pair.truth_s, pair.prediction_s, task), summary[target], target)
        rng = np.random.default_rng(config['seed'])
        cohorts = sorted(pair.year.unique())
        errors, gains = [], []
        for _ in range(config['bootstrap_replicates']):
            pieces = []
            for year in rng.choice(cohorts, len(cohorts), replace=True):
                indices = np.flatnonzero(pair.year.to_numpy() == year)
                pieces.append(rng.choice(indices, len(indices), replace=True))
            sampled = pair.iloc[np.concatenate(pieces)]
            a = np.mean((sampled.truth_s - sampled.prediction_s) ** 2)
            b = np.mean((sampled.truth_s - sampled.prediction_b) ** 2)
            if task == 'regression':
                a, b = np.sqrt(a), np.sqrt(b)
            errors.append(a)
            gains.append(b - a)
        np.testing.assert_allclose(np.quantile(errors, [.025, .975]), summary[target]['loss_interval'], atol=1e-8)
        np.testing.assert_allclose(np.quantile(gains, [.025, .975]), summary[target]['baseline_minus_model_interval'], atol=1e-8)
    # Check all frozen model predictions, including supplementary diagnostics.
    frame, groups = load_data(ROOT)
    prediction_checks, max_difference = 0, 0.
    for (target, label, year), rows in predictions.groupby(['target', 'model', 'year']):
        valid = frame[frame.draft_year.eq(year)]
        fitted = joblib.load(out / 'models' / f'{target}_{label}_{year}.joblib')
        p = predict_spec(fitted, valid, config['targets'][target])
        actual = pd.DataFrame({'player': valid.player, 'actual': p}).merge(rows, on='player', validate='one_to_one')
        if len(actual) != len(valid) or len(rows) != len(valid):
            raise ValueError('Incomplete prediction coverage')
        difference = float(np.max(np.abs(actual.actual - actual.prediction)))
        if difference > 1e-6:
            raise ValueError('Frozen model/prediction disagreement')
        np.testing.assert_allclose(actual.truth, actual.player.map(valid.set_index('player')[target]))
        max_difference = max(max_difference, difference)
        prediction_checks += 1
    selection = pd.read_csv(out / 'selection_predictions.csv')
    nested_predictions = pd.read_csv(out / 'nested_predictions.csv')
    nested_scores = pd.read_csv(out / 'nested_scores.csv')
    nested_differences = {}
    for score in nested_scores.to_dict('records'):
        rows = nested_predictions[(nested_predictions.target == score['target']) &
                                  (nested_predictions.model == score['model']) &
                                  (nested_predictions.year == score['origin'])]
        recalculated = calculate(rows.truth, rows.prediction, config['targets'][score['target']])
        # Nested scores were calculated directly on estimator arrays, which can
        # be float32 for XGBoost. CSV recalculation uses float64. Allow float32
        # rounding here only; final-test calculations still use strict tolerance.
        compare(recalculated, score, f"nested/{score['target']}/{score['model']}/{score['origin']}",
                rtol=2e-7, atol=1e-7)
        for metric, value in recalculated.items():
            if value is not None:
                nested_differences[metric] = max(nested_differences.get(metric, 0.), abs(value - score[metric]))
    for name, records in [('selection', selection), ('nested', nested_predictions)]:
        if records.duplicated(['player', 'year', 'target', 'model']).any():
            raise ValueError(f'Duplicated {name} records')
        for target, rows in records.groupby('target'):
            truth = rows.merge(prospects[['player', 'draft_year', target]],
                               left_on=['player', 'year'], right_on=['player', 'draft_year'],
                               validate='many_to_one')
            if len(truth) != len(rows):
                raise ValueError(f'Incomplete {name} truth coverage')
            np.testing.assert_allclose(truth.truth, truth[target])
    for target, details in freeze['targets'].items():
        for label, field in [('selected', 'development_loss'), ('constant', 'baseline_loss')]:
            rows = selection[(selection.target == target) & (selection.model == label)]
            compare({'loss': float(np.mean((rows.truth - rows.prediction) ** 2))},
                    {'loss': details[field]}, f'{target} development {label}')
            if set(rows.year.unique()) != set(details['folds']):
                raise ValueError('Development fold mismatch')
    trials = [json.loads(line) for line in (out / 'trials.jsonl').read_text().splitlines()]
    for target, details in freeze['targets'].items():
        valid = [t for t in trials if t['origin'] == 2020 and t['target'] == target and t['failure'] is None]
        candidates = [(t['metrics']['loss'], t['spec']) for t in valid]
        ensemble = details['entries'].get('ensemble')
        if ensemble:
            rows = selection[(selection.target == target) & (selection.model == 'ensemble')]
            candidates.append((float(np.mean((rows.truth - rows.prediction) ** 2)), ensemble))
        loss, spec = min(candidates, key=lambda t: t[0])
        if spec != details['selected'] or not np.isclose(loss, details['development_loss']):
            raise ValueError('Frozen selection does not match development evidence')
    for origin in config['nested_origins'] + [min(config['test_years'])]:
        years = sorted(y for y in frame.draft_year.unique()
                       if y + config['horizon'] <= origin and
                       (frame.draft_year + config['horizon'] <= y).sum() >= config['min_training'])
        if origin == 2020 and years != [2013, 2014, 2015]:
            raise ValueError('Temporal folds changed')
    if before != {f: digest(out / f) for f in protected}:
        raise ValueError('Audit changed protected evidence')
    destination = ROOT / 'output/audit'
    destination.mkdir(parents=True, exist_ok=True)
    evidence = dict(status='passed', target_field_checks=target_checks,
                    test_metric_rows=metric_checks, frozen_model_cohort_checks=prediction_checks,
                    nested_metric_rows=len(nested_scores),
                    nested_metric_max_absolute_differences=nested_differences,
                    max_prediction_difference=max_difference, bootstrap_targets=len(summary),
                    trial_evaluations=len(trials), disqualified_trials=sum(t['failure'] is not None for t in trials),
                    protected_hashes=before,
                    limitations='Recalculation from recorded snapshots verifies implementation consistency, not provider truth or historical point-in-time availability. No tuning performed.')
    (destination / 'verification.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()
