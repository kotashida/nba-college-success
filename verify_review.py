"""Adversarial coverage and provenance checks supplemental to audit_research.py.

This checks the existing experiment; it does not tune, score alternatives, or
replace the consumed evaluation. The output is explicitly post-evaluation.
"""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import platform
import sys

import numpy as np
import pandas as pd

from review_evidence import verify_seal

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def equal_spec(a, b):
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def check_prediction_coverage(predictions, prospects, origins, labels, targets):
    require(not predictions.duplicated(['player', 'year', 'target', 'model']).any(), 'Duplicate prediction key')
    require(set(predictions.target) == set(targets), 'Target coverage mismatch')
    require(set(predictions.year) == set(origins), 'Origin coverage mismatch')
    checked = 0
    for target in targets:
        for year in origins:
            expected = set(prospects.loc[prospects.draft_year.eq(year), 'player'])
            part = predictions[predictions.target.eq(target) & predictions.year.eq(year)]
            expected_labels = labels[target] if isinstance(labels, dict) else labels
            require(set(part.model) == set(expected_labels), f'Model coverage mismatch: {target}/{year}')
            for label in expected_labels:
                group = part[part.model.eq(label)]
                require(set(group.player) == expected and len(group) == len(expected), f'Player coverage mismatch: {target}/{year}/{label}')
                require(np.isfinite(group[['truth', 'prediction']].to_numpy()).all(), 'Nonfinite saved prediction')
                reference = prospects.set_index('player').loc[group.player, target].to_numpy()
                np.testing.assert_allclose(group.truth, reference, atol=1e-10, rtol=1e-10)
                checked += 1
    return checked


def main():
    seal = verify_seal(ROOT)
    folder = ROOT / 'output/experiments'
    freeze = json.loads((folder / 'freeze.json').read_text())
    config = freeze['config']
    prospects = pd.read_csv(ROOT / 'data/processed/prospects.csv')
    require(prospects.player.is_unique, 'Prospect name key is not unique')
    predictions = pd.read_csv(folder / 'test_predictions.csv')
    nested = pd.read_csv(folder / 'nested_predictions.csv')
    selection = pd.read_csv(folder / 'selection_predictions.csv')
    test_labels = {target: list(details['entries']) for target, details in freeze['targets'].items()}
    test_groups = check_prediction_coverage(predictions, prospects, config['test_years'], test_labels, config['targets'])
    nested_groups = check_prediction_coverage(nested, prospects, config['nested_origins'], config['families'] + ['ensemble', 'selected'], config['targets'])
    selection_labels = {t: [label for label in labels if label != 'draft_order_benchmark'] for t, labels in test_labels.items()}
    selection_groups = check_prediction_coverage(selection, prospects, [2013, 2014, 2015], selection_labels, config['targets'])
    trials = [json.loads(line) for line in (folder / 'trials.jsonl').read_text().splitlines()]
    expected_trials = 1 + (len(config['families']) - 1) * config['trials_per_family']
    require(len(trials) == expected_trials * len(config['targets']) * (len(config['nested_origins']) + 1), 'Incomplete candidate log')
    candidate_groups = 0
    for origin in config['nested_origins'] + [min(config['test_years'])]:
        for target in config['targets']:
            group = [t for t in trials if t['origin'] == origin and t['target'] == target]
            require(len(group) == expected_trials and {t['candidate'] for t in group} == set(range(expected_trials)), 'Missing or duplicated candidate identity')
            require(group[0]['spec']['family'] == 'constant', 'Baseline candidate missing')
            for family in config['families'][1:]:
                require(sum(t['spec']['family'] == family for t in group) == config['trials_per_family'], 'Family search coverage mismatch')
            for t in group:
                require((t['failure'] is None) == (t['metrics'] is not None), 'Invalid failure/score pairing')
                if t['metrics']:
                    require(np.isfinite(t['metrics']['loss']), 'Nonfinite candidate score')
            candidate_groups += 1
    finalist_checks = 0
    for target, details in freeze['targets'].items():
        group = [t for t in trials if t['origin'] == 2020 and t['target'] == target and t['failure'] is None]
        for label in config['families']:
            expected = min([t for t in group if t['spec']['family'] == label], key=lambda t: t['metrics']['loss'])['spec']
            require(equal_spec(expected, details['entries'][label]), f'Family finalist mismatch: {target}/{label}')
            finalist_checks += 1
        for feature_group in config['feature_groups']:
            expected = min([t for t in group if t['spec']['group'] == feature_group], key=lambda t: t['metrics']['loss'])['spec']
            require(equal_spec(expected, details['entries']['ablation_' + feature_group]), f'Feature finalist mismatch: {target}/{feature_group}')
            finalist_checks += 1
    # Independent integer-year arithmetic, checked against every recorded split.
    temporal_checks = 0
    splits = json.loads((folder / 'splits.json').read_text())
    for entry in splits:
        origin = entry['origin']
        require(entry['outer_train_max'] == origin - config['horizon'], 'Outer maturity boundary mismatch')
        for fold in entry['inner']:
            year = fold['year']
            require(year + config['horizon'] <= origin and fold['train_max'] + config['horizon'] <= year, 'Immature validation/fitting labels')
            require(fold['n_train'] == int((prospects.draft_year + config['horizon'] <= year).sum()), 'Recorded training size mismatch')
            require(fold['n_valid'] == int(prospects.draft_year.eq(year).sum()), 'Recorded validation size mismatch')
            temporal_checks += 1
    for name in ['freeze.json', 'test_receipt.json', 'splits.json']:
        require((folder / name).read_bytes() == (ROOT / 'reproducibility' / name).read_bytes(), f'Versioned evidence differs: {name}')
    # Assert all professionally sourced target columns are absent from features.
    from research.experiment import load_data
    frame, groups = load_data(ROOT)
    forbidden = set(config['targets']) | {'pick', 'pick_reference_only', 'nba_id', 'draft_year', 'Rec_Rank', 'age'}
    for label, columns in groups.items():
        require(not forbidden.intersection(columns), f'Outcome/professional predictor in {label}')
    early = frame[frame.draft_year.eq(2008)]
    ranges = {}
    for data_name, table in [('test', predictions), ('nested', nested)]:
        for target in ['minutes5', 'active5']:
            part = table[table.target.eq(target) & table.model.eq('selected')]
            ranges[data_name + '/' + target] = {'min': float(part.prediction.min()), 'max': float(part.prediction.max())}
    lock = {}
    for line in (ROOT / 'requirements-lock.txt').read_text().splitlines():
        if '==' in line and not line.startswith('#'):
            package, version = line.split('==', 1)
            require(importlib.metadata.version(package) == version, f'Installed lock mismatch: {package}')
            lock[package] = version
    verify_seal(ROOT)
    record = {'review_date': '2026-10-13', 'status': 'passed',
              'sealed_files': len(seal['files']), 'test_prediction_groups': test_groups,
              'nested_prediction_groups': nested_groups, 'selection_prediction_groups': selection_groups,
              'candidate_origin_target_groups': candidate_groups, 'candidate_records': len(trials),
              'family_and_feature_finalists': finalist_checks, 'recorded_inner_temporal_splits': temporal_checks,
              'installed_lock_packages': len(lock), 'python': sys.version, 'platform': platform.platform(),
              'earliest_cohort': {'n': len(early), 'no_earlier_observed_college_records': int(early.prior_seasons.eq(0).sum()),
                                  'nonfreshmen_without_earlier_records': int((early.prior_seasons.eq(0) & early.class_year.gt(1)).sum())},
              'selected_continuous_prediction_ranges': ranges,
              'limitations': 'Post-evaluation consistency audit of recorded retrospective sources, not independent provider truth, external preregistration, or a new test.'}
    path = ROOT / 'output/audit/review_2026-10-13_expanded_checks.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
