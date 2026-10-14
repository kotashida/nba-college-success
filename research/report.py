"""Publication figures, actual-result tables, and LaTeX PDF compilation."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import tempfile
import sys
import warnings

import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.inspection import permutation_importance
from sklearn.calibration import calibration_curve
from sklearn.compose import TransformedTargetRegressor

from .experiment import load_data, metrics, fit_spec, predict_spec, check_freeze

LABELS = {'vorp5': 'Five-year VORP', 'minutes5': 'Five-year minutes', 'active5': 'Years active (of five)',
          'rotation5': 'Sustained rotation', 'starter5': 'Sustained starter'}
NAMES = {'constant': 'Training mean / prevalence', 'linear': 'Regularized linear',
         'random_forest': 'Random Forest', 'extra_trees': 'Extra Trees', 'xgboost': 'XGBoost',
         'lightgbm': 'LightGBM', 'catboost': 'CatBoost', 'ensemble': 'Three-family ensemble'}
DEFAULT_SHOWWARNING = warnings.showwarning

def display_warning(message, category, filename, lineno, file=None, line=None):
    # A sklearn thread-filter warning can repeat for every diagnostic tree call.
    if str(message).startswith('`sklearn.utils.parallel.delayed` should be used with'):
        return
    DEFAULT_SHOWWARNING(message, category, filename, lineno, file=file, line=line)

def tex(value):
    return str(value).replace('_', r'\_').replace('%', r'\%').replace('&', r'\&')

def num(value, digits=3):
    return '--' if value is None or pd.isna(value) else f'{value:,.{digits}f}'

def table(path, header, rows, align):
    lines = [r'\begin{tabular}{' + align + '}', r'\toprule', ' & '.join(header) + r' \\', r'\midrule']
    lines += [' & '.join(str(x) for x in row) + r' \\' for row in rows]
    lines += [r'\bottomrule', r'\end{tabular}']
    path.write_text('\n'.join(lines), encoding='utf-8')

def report(root, config):
    warnings.showwarning = display_warning
    root = Path(root)
    out = root / 'output/experiments'
    figures = root / 'output/figures'
    generated = root / 'paper/generated'
    figures.mkdir(parents=True, exist_ok=True)
    publication_figures = root / 'paper/figures'
    publication_figures.mkdir(parents=True, exist_ok=True)
    generated.mkdir(parents=True, exist_ok=True)
    freeze = check_freeze(root)
    audit = json.loads((root / 'data/processed/audit.json').read_text())
    checks = json.loads((root / 'data/processed/independent_checks.json').read_text())
    summary = json.loads((out / 'test_summary.json').read_text())
    test = pd.read_csv(out / 'test_scores.csv')
    test_predictions = pd.read_csv(out / 'test_predictions.csv')
    nested = pd.read_csv(out / 'nested_predictions.csv')
    selection = pd.read_csv(out / 'selection_predictions.csv')
    frame, groups = load_data(root)
    development = frame[frame.draft_year + 5 <= min(config['test_years'])]
    heldout = frame[frame.draft_year.isin(config['test_years'])]
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12, 'axes.spines.top': False,
                         'axes.spines.right': False, 'pdf.fonttype': 42, 'savefig.bbox': 'tight'})
    palette = ['#007f78', '#a33b59', '#3269a8', '#595959', '#a38720']
    def save(fig, filename):
        fig.tight_layout()
        fig.savefig(figures / (filename + '.pdf'))
        fig.savefig(figures / (filename + '.png'), dpi=180)
        shutil.copyfile(figures / (filename + '.pdf'), publication_figures / (filename + '.pdf'))
        plt.close(fig)
    rows = []
    for year, group in frame.groupby('draft_year'):
        rows.append([str(year), str(len(group)), str(int(group.combine_height.notna().sum())),
                     str(int(group.outcome_link.str.startswith('no NBA').sum())),
                     'Final test' if year in config['test_years'] else 'Development / historical'])
    table(generated / 'cohorts.tex', ['Draft', '$N$', 'Height measured', 'No NBA record', 'Role'], rows, 'lrrrl')
    target_rows, macros = [], {}
    focal_skills = {}
    for target, task in config['targets'].items():
        details = freeze['targets'][target]
        focal_skills[target] = 1 - details['development_loss'] / details['baseline_loss']
        macros[target + 'Family'] = tex(NAMES[details['selected']['family']])
        s = summary[target]
        baseline = test[(test.target == target) & (test.model == 'constant') & (test.year == 'pooled')].iloc[0]
        metric = 'rmse' if task == 'regression' else 'brier'
        target_rows.append([LABELS[target], tex(NAMES[details['selected']['family']]),
                            num(s[metric], 3 if target != 'minutes5' else 0),
                            num(baseline[metric], 3 if target != 'minutes5' else 0),
                            num(s['r2'] if task == 'regression' else s['auc'])])
        for metric_name in ['rmse', 'mae', 'r2', 'brier', 'auc', 'ap']:
            if metric_name in s:
                macros[target + metric_name] = num(s[metric_name])
    table(generated / 'holdout.tex', ['Target', 'Frozen selection', 'Error', 'Constant', '$R^2$ / AUC'], target_rows, 'llrrr')
    probability_rows = []
    for target, task in config['targets'].items():
        if task != 'classification':
            continue
        for label in ['selected', 'constant', 'draft_order_benchmark']:
            score = test[(test.target == target) & (test.model == label) & (test.year == 'pooled')].iloc[0]
            probability_rows.append([LABELS[target], tex(label.replace('_', ' ')),
                                     num(score.prevalence), num(score.brier), num(score.log_loss),
                                     num(score.auc), num(score.ap)])
    table(generated / 'probability_metrics.tex',
          ['Target', 'Model', 'Prevalence', 'Brier', 'Log loss', 'AUC', 'AP'],
          probability_rows, 'llrrrrr')
    focal = max(focal_skills, key=focal_skills.get)
    macros.update({'SampleN': str(len(frame)), 'TestN': str(len(heldout)), 'DevelopmentN': str(len(development)),
                   'CollegeN': f"{audit['college_seasons']:,}", 'FocalTarget': LABELS[focal],
                   'CheckN': str(checks['checks']), 'ValidCheckN': str(checks['checks'] - checks['masked_discrepancies']),
                   'TrialN': str(sum(1 for _ in (out / 'trials.jsonl').open()))})
    (generated / 'results.tex').write_text('\n'.join('\\newcommand{\\' + key.replace('5', 'Five').replace('2', 'Two') + '}{' + value + '}' for key, value in macros.items()), encoding='utf-8')
    uncertainty_rows = []
    for target, task in config['targets'].items():
        s = summary[target]
        absolute, paired = s['loss_interval'], s['baseline_minus_model_interval']
        digits = 0 if target == 'minutes5' else 3
        uncertainty_rows.append([LABELS[target], f'[{num(absolute[0], digits)}, {num(absolute[1], digits)}]',
                                 f'[{num(paired[0], digits)}, {num(paired[1], digits)}]'])
    table(generated / 'uncertainty.tex', ['Target', 'Error interval', 'Constant minus selected'], uncertainty_rows, 'lrr')
    nested_rows = []
    for target, task in config['targets'].items():
        selected = nested[(nested.target == target) & (nested.model == 'selected')]
        constant = nested[(nested.target == target) & (nested.model == 'constant')]
        a, b = metrics(selected.truth, selected.prediction, task), metrics(constant.truth, constant.prediction, task)
        metric = 'rmse' if task == 'regression' else 'brier'
        nested_rows.append([LABELS[target], str(a['n']), num(a[metric], 0 if target == 'minutes5' else 3),
                            num(b[metric], 0 if target == 'minutes5' else 3), num(a.get('r2', a.get('auc')))])
    table(generated / 'nested.tex', ['Target', '$N$', 'Selected error', 'Constant error', '$R^2$ / AUC'], nested_rows, 'lrrrr')
    specs = []
    def formatted_params(params):
        pieces = []
        for key, value in sorted(params.items()):
            rendered = f'{value:.6g}' if isinstance(value, float) else str(value)
            pieces.append(r'\texttt{' + tex(key) + '}: ' + tex(rendered))
        return '; '.join(pieces)
    def description(specification):
        return tex(NAMES[specification['family']]) + '; ' + tex(specification['group']) + ' predictors; ' + tex(specification['transform']) + ' target.'
    for target, details in freeze['targets'].items():
        specification = details['selected']
        if specification['family'] == 'ensemble':
            specs.append(r'\paragraph{' + LABELS[target] + '} Equal-weight blend of three separately fitted finalists, averaged on the original outcome scale.')
            specs.append(r'\begin{itemize}\small\raggedright' + '\n' + '\n'.join(r'\item ' + description(member) + r'\par ' + formatted_params(member['params']) + '.' for member in specification['members']) + '\n' + r'\end{itemize}')
        else:
            specs.append(r'\paragraph{' + LABELS[target] + '} ' + description(specification) + r'\par {\small\raggedright ' + formatted_params(specification['params']) + r'.\par}')
    (generated / 'specifications.tex').write_text('\n'.join(specs), encoding='utf-8')
    perclass = []
    for target, task in config['targets'].items():
        for year in config['test_years']:
            r = test[(test.target == target) & (test.model == 'selected') & (test.year == str(year))].iloc[0]
            perclass.append([LABELS[target], str(year), str(int(r.n)), num(r.rmse if task == 'regression' else r.brier, 0 if target == 'minutes5' else 3), num(r.r2 if task == 'regression' else r.auc)])
    table(generated / 'per_class.tex', ['Target', 'Draft', '$N$', 'Error', '$R^2$ / AUC'], perclass, 'llrrr')
    models = config['families'] + ['ensemble', 'draft_order_benchmark', 'ablation_college', 'ablation_engineered', 'ablation_hybrid']
    supplementary = []
    for label in models:
        values = []
        for target, task in config['targets'].items():
            r = test[(test.target == target) & (test.model == label) & (test.year == 'pooled')].iloc[0]
            values.append(num(r.rmse if task == 'regression' else r.brier, 0 if target == 'minutes5' else 3))
        supplementary.append([tex(NAMES.get(label, label.replace('_', ' ')))] + values)
    table(generated / 'all_models.tex', ['Model', 'VORP', 'Minutes', 'Active', 'Rotation', 'Starter'], supplementary, 'lrrrrr')
    skill_rows = []
    development_matrix = []
    for target, task in config['targets'].items():
        part = selection[selection.target.eq(target)]
        base = part[part.model.eq('constant')]
        baseline_loss = np.mean((base.truth - base.prediction) ** 2)
        record = []
        for label in config['families'] + ['ensemble']:
            group = part[part.model.eq(label)]
            record.append(1 - np.mean((group.truth - group.prediction) ** 2) / baseline_loss)
        development_matrix.append(record)
        skill_rows.append([LABELS[target], num(focal_skills[target]), tex(NAMES[freeze['targets'][target]['selected']['family']])])
    table(generated / 'selection.tex', ['Target', 'Development skill', 'Frozen selection'], skill_rows, 'lrl')
    fig, ax = plt.subplots(figsize=(10.2, 3.4))
    matrix = np.array(development_matrix)
    image = ax.imshow(matrix, cmap='RdYlGn', vmin=-.3, vmax=.3, aspect='auto')
    ax.set_xticks(range(8), ['Constant', 'Linear', 'RF', 'ET', 'XGB', 'LGBM', 'CatBoost', 'Blend'])
    ax.set_yticks(range(5), [LABELS[t] for t in config['targets']])
    for i in range(5):
        for j in range(8):
            ax.text(j, i, f'{matrix[i,j]:.2f}', ha='center', va='center', fontsize=11)
    fig.colorbar(image, ax=ax, label='Squared-error skill relative to constant')
    save(fig, 'development_comparison')
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.1))
    for ax, target, color in zip(axes, ['vorp5', 'minutes5', 'active5'], palette):
        ax.hist(development[target], bins=25 if target != 'active5' else np.arange(-.5, 6.5), color=color, alpha=.8)
        ax.set_xlabel(LABELS[target]); ax.set_ylabel('Players')
    save(fig, 'outcome_distributions')
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.3))
    axes[0].scatter(development.bpm, development.vorp5, s=18, alpha=.65, color=palette[0])
    axes[0].set(xlabel='Final-season college BPM', ylabel='Five-year NBA VORP')
    values = [development[development.class_year.eq(c)].minutes5 for c in [1, 2, 3, 4]]
    axes[1].boxplot(values, tick_labels=['Freshman', 'Sophomore', 'Junior', 'Senior'], showfliers=False)
    axes[1].set_ylabel('Five-year NBA minutes')
    save(fig, 'college_relationships')
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    counts = frame.groupby('draft_year').size()
    axes[0].bar(counts.index, counts, color=[palette[1] if y in config['test_years'] else palette[0] for y in counts.index])
    axes[0].set(xlabel='Draft class', ylabel='School-confirmed college draftees')
    axes[0].set_xticks([2008, 2011, 2014, 2017, 2020, 2021])
    plt.setp(axes[0].get_xticklabels(), rotation=45, ha='right')
    missing = development[groups['hybrid']].isna().mean().sort_values(ascending=False).head(14).sort_values()
    axes[1].barh([c.replace('_', ' ') for c in missing.index], 100 * missing.values, color=palette[2])
    axes[1].set_xlabel('Missing predictors (%)'); axes[1].tick_params(axis='y', labelsize=11)
    save(fig, 'cohort_missingness')
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.4))
    for ax, target, color in zip(axes, ['vorp5', 'minutes5', 'active5'], palette):
        part = test_predictions[(test_predictions.target == target) & (test_predictions.model == 'selected')]
        ax.scatter(part.truth, part.prediction, s=24, alpha=.65, color=color)
        lo, hi = min(part.truth.min(), part.prediction.min()), max(part.truth.max(), part.prediction.max())
        ax.plot([lo, hi], [lo, hi], color='#333333', lw=1, ls='--')
        ax.set(title=LABELS[target], xlabel='Observed', ylabel='Predicted')
    save(fig, 'test_regression')
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.5))
    for ax, target in zip(axes, ['rotation5', 'starter5']):
        part = test_predictions[(test_predictions.target == target) & (test_predictions.model == 'selected')]
        observed, predicted = calibration_curve(part.truth, part.prediction, n_bins=5, strategy='quantile')
        ax.plot(predicted, observed, 'o-', color=palette[0], label='Frozen selection')
        ax.plot([0, 1], [0, 1], '--', color='#555555', lw=1)
        ax.set(title=LABELS[target], xlabel='Mean predicted probability', ylabel='Observed fraction', xlim=(0, 1), ylim=(0, 1))
        ax.legend(fontsize=8)
    save(fig, 'test_calibration')
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.4))
    part = test_predictions[(test_predictions.target == 'vorp5') & (test_predictions.model == 'selected')]
    residual = part.truth - part.prediction
    axes[0].scatter(part.prediction, residual, color=palette[1], alpha=.65, s=22)
    axes[0].axhline(0, color='#555555', lw=1)
    axes[0].set(xlabel='Predicted five-year VORP', ylabel='Observed minus predicted')
    axes[1].hist(residual, bins=20, color=palette[1], alpha=.8)
    axes[1].set(xlabel='VORP residual', ylabel='Players')
    save(fig, 'residuals')
    # Interpret an actual RF finalist, not a substitute presented as the selected model.
    import shap
    fitted = joblib.load(out / 'models/vorp5_random_forest_2020.joblib')
    model = fitted['model']
    spec = freeze['targets']['vorp5']['entries']['random_forest']
    transform = spec['transform']
    pipeline = model.regressor_ if isinstance(model, TransformedTargetRegressor) else model
    diagnostic = frame[frame.draft_year.eq(2019)]
    encoded = pipeline.named_steps['preprocess'].transform(diagnostic[fitted['columns']])
    feature_names = pipeline.named_steps['preprocess'].get_feature_names_out()
    explanations = shap.TreeExplainer(pipeline.named_steps['model'])(encoded)
    values = explanations.values
    np.savez_compressed(out / 'shap_diagnostic.npz', values=values, data=encoded, names=feature_names)
    importance = pd.DataFrame({'feature': feature_names, 'mean_abs_shap': np.abs(values).mean(axis=0)}).sort_values('mean_abs_shap', ascending=False)
    importance.to_csv(out / 'shap_importance.csv', index=False)
    chosen = importance.head(14).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8.3, 4.1))
    ax.barh(chosen.feature.str.replace('_', ' '), chosen.mean_abs_shap, color=palette[0])
    ax.set_xlabel('Mean absolute TreeSHAP contribution (' + ('VORP' if transform == 'raw' else transform + ' target scale') + ')')
    save(fig, 'shap_diagnostic')
    article = 'an ' if transform == 'asinh' else 'a '
    (generated / 'interpretability.tex').write_text('The interpretability diagnostic uses the 2020-fitted Random Forest finalist with ' + tex(spec['group']) + ' predictors and ' + article + tex(transform) + ' target, fit on draft classes through 2015. Contributions are measured on the ' + ('original VORP' if transform == 'raw' else tex(transform) + '-transformed') + ' scale. The primary VORP selection is Ridge; this forest is a separate retrospective diagnostic.', encoding='utf-8')
    # Retrospective 2020-fitted finalist on the 2019 cohort. Its fitting labels
    # are from earlier classes, but this is not a simulated 2019-origin forecast.
    perm = permutation_importance(model, diagnostic[fitted['columns']], diagnostic.vorp5,
                                   scoring='neg_mean_squared_error', n_repeats=20, random_state=config['seed'], n_jobs=1)
    ptable = pd.DataFrame({'feature': fitted['columns'], 'mse_increase': perm.importances_mean, 'sd': perm.importances_std}).sort_values('mse_increase', ascending=False)
    ptable.to_csv(out / 'permutation_importance.csv', index=False)
    chosen = ptable.head(12).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8.2, 3.7))
    ax.barh(chosen.feature.str.replace('_', ' '), chosen.mse_increase, xerr=chosen.sd, color=palette[2], error_kw={'lw': .8})
    ax.axvline(0, color='#555555', lw=1); ax.set_xlabel('Increase in original-scale VORP MSE after permutation')
    save(fig, 'permutation_diagnostic')
    metadata = {'development_focal_target': focal, 'development_relative_skills': focal_skills,
                'interpretation_model': spec, 'interpretation_fit_through': 2015, 'interpretation_cohort': 2019,
                'plots': [p.name for p in figures.glob('*.pdf')]}
    (out / 'report_metadata.json').write_text(json.dumps(metadata, indent=2))
    lines = ['# Verified Results', '', f'Independent college-to-NBA study: {len(frame)} drafted prospects, {len(heldout)} final-test prospects (2020-2021).',
             'All targets use five calendar NBA regular seasons after actual draft year.', '', '| Target | Frozen model | Selected error | Constant error |', '|---|---|---:|---:|']
    for row in target_rows:
        lines.append('| ' + ' | '.join(row[:4]) + ' |')
    lines += ['', 'Regression errors are original-scale RMSE; binary errors are Brier scores.',
              'The test is consumed. Do not choose a new winner using supplementary test scores.',
              'Only two test cohorts; bootstrap intervals are conditional and do not establish future-era guarantees.',
              'College sources are dated and school-confirmed, but fully independent verification is limited to a small sample.']
    (root / 'output/RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')
    print('Generated nine vector figures, actual-result tables, SHAP and permutation diagnostics.', flush=True)

def compile_paper(root, preview_dir=None):
    """Keep one publication PDF; discard reproducible build intermediates."""
    root = Path(root).resolve()
    output = root / 'output'
    output.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='paper-build-', dir=output) as scratch:
        destination = Path(scratch).resolve()
        if destination.parent != output.resolve():
            raise ValueError('Paper build directory must stay inside the project output directory')
        _compile_paper(root, destination)
        audit = output / 'audit'
        audit.mkdir(exist_ok=True)
        shutil.copyfile(destination / 'layout_checks.json', audit / 'paper_layout_checks.json')
        if preview_dir is not None:
            preview_dir = Path(preview_dir)
            preview_dir.mkdir(parents=True, exist_ok=True)
            for path in destination.glob('*.png'):
                shutil.copyfile(path, preview_dir / path.name)


def _compile_paper(root, destination):
    root = Path(root)
    paper_name = 'five_year_nba_outcomes'
    destination.mkdir(parents=True, exist_ok=True)
    # Compile from an isolated copy of publication inputs. A stale .aux in
    # paper/ otherwise shadows the fresh output-directory .aux on later passes.
    shutil.copyfile(root / 'paper' / (paper_name + '.tex'), destination / (paper_name + '.tex'))
    for folder in ['generated', 'figures']:
        shutil.copytree(root / 'paper' / folder, destination / folder)
    binary = os.environ.get('PDFLATEX') or shutil.which('pdflatex')
    if not binary:
        fallback = Path.home() / 'AppData/Local/Programs/MiKTeX/miktex/bin/x64/pdflatex.exe'
        if fallback.exists():
            binary = str(fallback)
    if not binary:
        raise RuntimeError('Install TeX Live or MiKTeX, or set PDFLATEX')
    for _ in range(2):
        result = subprocess.run([binary, '-interaction=nonstopmode', '-halt-on-error', '-no-shell-escape',
                                 '-jobname=' + paper_name, '-output-directory=' + str(destination), paper_name + '.tex'], cwd=destination,
                                capture_output=True, text=True)
        (destination / 'compiler_output.txt').write_text(result.stdout + result.stderr, encoding='utf-8')
        if result.returncode:
            print(result.stdout[-7000:]); raise RuntimeError('LaTeX compilation failed')
    import pymupdf as fitz
    from PIL import Image, ImageOps, ImageDraw
    pdf = fitz.open(destination / (paper_name + '.pdf'))
    page_paths, issues = [], []
    for i, page in enumerate(pdf):
        path = destination / f'page_{i+1:02d}.png'
        page.get_pixmap(matrix=fitz.Matrix(1.4, 1.4)).save(path)
        page_paths.append(path)
        for block in page.get_text('dict')['blocks']:
            if block['type'] != 0: continue
            if not page.rect.contains(fitz.Rect(block['bbox'])):
                issues.append({'page': i+1, 'bbox': block['bbox']})
    for start in range(0, len(page_paths), 6):
        contact = Image.new('RGB', (1050, 1500), 'white')
        for j, path in enumerate(page_paths[start:start+6]):
            im = Image.open(path).convert('RGB'); im.thumbnail((340, 710))
            contact.paste(im, ((j%3)*350, (j//3)*750 + 25))
            ImageDraw.Draw(contact).text(((j%3)*350+12, (j//3)*750+5), f'Page {start+j+1}', fill='black')
        contact.save(destination / f'contact_{start+1:02d}.png')
    log = (destination / (paper_name + '.log')).read_text(encoding='utf-8', errors='replace')
    warning_lines = [l for l in log.splitlines() if 'Overfull' in l or 'Underfull' in l or 'Warning' in l]
    (destination / 'layout_checks.json').write_text(json.dumps({'pages': len(pdf), 'outside_page_text': issues, 'latex_warnings': warning_lines}, indent=2))
    page_count = len(pdf)
    pdf.close()
    shutil.copyfile(destination / (paper_name + '.pdf'), root / 'paper' / (paper_name + '.pdf'))
    print(f'Compiled and rendered {page_count} pages; layout issues={len(issues)}, LaTeX warnings={len(warning_lines)}', flush=True)
