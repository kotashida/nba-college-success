"""Verify published scores and intervals using only the public review package.

Does not read provider snapshots, processed source tables, or deserialize models.
Raw-label reconstruction and refitting still require the licensed source inputs.
"""
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd

from audit_research import calculate, compare

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_results(root=ROOT):
    root = Path(root)
    folder = root / 'output/experiments'
    receipt = json.loads((folder / 'test_receipt.json').read_text())
    for key, filename in [('freeze_sha256', 'freeze.json'), ('predictions_sha256', 'test_predictions.csv'),
                          ('scores_sha256', 'test_scores.csv'), ('summary_sha256', 'test_summary.json')]:
        if digest(folder / filename) != receipt[key]:
            raise ValueError(f'Published evaluation receipt mismatch: {filename}')
    freeze = json.loads((folder / 'freeze.json').read_text())
    config = freeze['config']
    seal = json.loads((root / 'reproducibility/review_2026-10-13_evidence_seal.json').read_text())
    restricted_inputs = []
    protected_public = 0
    raw_metadata = {'manifest.json', 'source_quality_policy.json', 'college_schema_reference.R'}
    processed_evidence = {'audit.json', 'independent_checks.json', 'independent_source_checks.csv',
                          'identity_links.csv', 'exclusions.csv'}
    for relative, expected in seal['files'].items():
        path = Path(relative)
        if ((path.parts[:2] == ('data', 'raw') and path.name not in raw_metadata)
                or (path.parts[:2] == ('data', 'processed') and path.name not in processed_evidence)):
            restricted_inputs.append(relative)
            continue
        if not (root / path).is_file() or digest(root / path) != expected:
            raise ValueError(f'Public evidence seal mismatch: {relative}')
        protected_public += 1
    # Verify every frozen estimator artifact by bytes, without loading pickle data.
    for relative, expected in freeze['model_hashes'].items():
        if digest(root / relative) != expected:
            raise ValueError(f'Frozen model artifact mismatch: {relative}')
    predictions = pd.read_csv(folder / 'test_predictions.csv')
    scores = pd.read_csv(folder / 'test_scores.csv', dtype={'year': str})
    if predictions.duplicated(['player', 'year', 'target', 'model']).any():
        raise ValueError('Duplicate published prediction identity')
    metric_rows = 0
    for score in scores.to_dict('records'):
        group = predictions[predictions.target.eq(score['target']) & predictions.model.eq(score['model'])]
        if score['year'] != 'pooled':
            group = group[group.year.eq(int(score['year']))]
        compare(calculate(group.truth, group.prediction, config['targets'][score['target']]), score,
                f"public/{score['target']}/{score['model']}/{score['year']}")
        metric_rows += 1
    summary = json.loads((folder / 'test_summary.json').read_text())
    for target, task in config['targets'].items():
        selected = predictions[predictions.target.eq(target) & predictions.model.eq('selected')]
        baseline = predictions[predictions.target.eq(target) & predictions.model.eq('constant')]
        pair = selected.merge(baseline, on=['player', 'year', 'target'], suffixes=('_s', '_b'),
                              validate='one_to_one').sort_values(['year', 'player'])
        np.testing.assert_allclose(pair.truth_s, pair.truth_b)
        compare(calculate(pair.truth_s, pair.prediction_s, task), summary[target], target)
        rng = np.random.default_rng(config['seed'])
        cohorts = sorted(pair.year.unique())
        errors, gains = [], []
        for _ in range(config['bootstrap_replicates']):
            samples = []
            for year in rng.choice(cohorts, len(cohorts), replace=True):
                candidates = np.flatnonzero(pair.year.to_numpy() == year)
                samples.append(rng.choice(candidates, len(candidates), replace=True))
            sample = pair.iloc[np.concatenate(samples)]
            a = float(np.mean((sample.truth_s - sample.prediction_s) ** 2))
            b = float(np.mean((sample.truth_s - sample.prediction_b) ** 2))
            if task == 'regression':
                a, b = np.sqrt(a), np.sqrt(b)
            errors.append(a)
            gains.append(b - a)
        np.testing.assert_allclose(np.quantile(errors, [.025, .975]), summary[target]['loss_interval'], atol=1e-8)
        np.testing.assert_allclose(np.quantile(gains, [.025, .975]), summary[target]['baseline_minus_model_interval'], atol=1e-8)
    nested_predictions = pd.read_csv(folder / 'nested_predictions.csv')
    nested_scores = pd.read_csv(folder / 'nested_scores.csv')
    for score in nested_scores.to_dict('records'):
        group = nested_predictions[nested_predictions.target.eq(score['target']) &
                                   nested_predictions.model.eq(score['model']) &
                                   nested_predictions.year.eq(score['origin'])]
        compare(calculate(group.truth, group.prediction, config['targets'][score['target']]), score,
                f"public/nested/{score['target']}/{score['model']}/{score['origin']}", rtol=2e-7, atol=1e-7)
    return {'status': 'passed', 'test_metric_rows': metric_rows, 'nested_metric_rows': len(nested_scores),
            'paired_bootstrap_targets': len(summary), 'frozen_model_hashes': len(freeze['model_hashes']),
            'public_sealed_files': protected_public, 'licensed_input_files_not_read': len(restricted_inputs),
            'scope': 'Repository-only numerical consistency of published predictions, scores, intervals and artifact bytes. Does not independently reconstruct labels, refit models, validate providers or establish historical data availability.'}


if __name__ == '__main__':
    print(json.dumps(verify_results(), indent=2))
