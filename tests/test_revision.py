"""Operational safeguards added after the consumed scientific evaluation."""
import json
import sys
from zipfile import ZipFile

import numpy as np
import pandas as pd
import pytest

import package
import predict
import train_final
from research.data import sha
from review_evidence import SEAL


@pytest.fixture
def inference_environment(tmp_path, monkeypatch):
    folder = tmp_path / 'output/forward_models'
    folder.mkdir(parents=True)
    model_path = folder / 'vorp5.joblib'
    model_path.write_bytes(b'synthetic model fixture')
    metadata = {'fitting_origin': 2026, 'target_tasks': {'vorp5': 'regression'},
                'model_hashes': {'vorp5.joblib': sha(model_path)}}
    (folder / 'metadata.json').write_text(json.dumps(metadata))
    input_path, output_path = tmp_path / 'input.csv', tmp_path / 'forecasts.csv'
    monkeypatch.setattr(predict, 'ROOT', tmp_path)
    monkeypatch.setattr(sys, 'argv', ['predict.py', str(input_path), str(output_path)])
    loads = []

    def load(path):
        loads.append(path)
        return {'columns': []}

    monkeypatch.setattr(predict.joblib, 'load', load)
    monkeypatch.setattr(predict, 'predict_spec', lambda fitted, frame, task: np.full(len(frame), .5))
    return input_path, output_path, folder, loads


@pytest.mark.parametrize('year', [np.nan, np.inf, -np.inf, 2027.5, 'not-a-year', 0, 10000])
def test_forecast_rejects_invalid_calendar_year_before_model_load(inference_environment, year):
    input_path, output_path, _, loads = inference_environment
    pd.DataFrame([{'player': 'SYNTHETIC TEST', 'prediction_year': year}]).to_csv(input_path, index=False)
    with pytest.raises(ValueError, match='finite integer calendar years'):
        predict.main()
    assert not loads and not output_path.exists()


@pytest.mark.parametrize('year', [2020, 2026])
def test_forecast_rejects_historical_origin(inference_environment, year):
    input_path, output_path, _, loads = inference_environment
    pd.DataFrame([{'player': 'SYNTHETIC TEST', 'prediction_year': year}]).to_csv(input_path, index=False)
    with pytest.raises(ValueError, match='historical validation'):
        predict.main()
    assert not loads and not output_path.exists()


@pytest.mark.parametrize('player', [None, '', '   '])
def test_forecast_rejects_blank_player(inference_environment, player):
    input_path, output_path, _, loads = inference_environment
    pd.DataFrame([{'player': player, 'prediction_year': 2027}]).to_csv(input_path, index=False)
    with pytest.raises(ValueError, match='nonblank player name'):
        predict.main()
    assert not loads and not output_path.exists()


def test_forecast_rejects_empty_input(inference_environment):
    input_path, output_path, _, loads = inference_environment
    pd.DataFrame(columns=['player', 'prediction_year']).to_csv(input_path, index=False)
    with pytest.raises(ValueError, match='At least one prospect'):
        predict.main()
    assert not loads and not output_path.exists()


@pytest.mark.parametrize('corruption', ['model', 'metadata'])
def test_forecast_requires_matching_artifact_hashes(inference_environment, corruption):
    input_path, output_path, folder, loads = inference_environment
    pd.DataFrame([{'player': 'SYNTHETIC TEST', 'prediction_year': 2027}]).to_csv(input_path, index=False)
    if corruption == 'model':
        (folder / 'vorp5.joblib').write_bytes(b'changed artifact')
    else:
        metadata = json.loads((folder / 'metadata.json').read_text())
        metadata.pop('model_hashes')
        (folder / 'metadata.json').write_text(json.dumps(metadata))
    with pytest.raises(ValueError, match='integrity'):
        predict.main()
    assert not loads and not output_path.exists()


def test_valid_forecast_retains_predictions(inference_environment):
    input_path, output_path, _, loads = inference_environment
    pd.DataFrame([{'player': ' SYNTHETIC TEST ', 'prediction_year': 2027.0}]).to_csv(input_path, index=False)
    predict.main()
    result = pd.read_csv(output_path)
    assert result.to_dict('records') == [{'player': 'SYNTHETIC TEST', 'prediction_year': 2027, 'vorp5': .5}]
    assert len(loads) == 1


def test_forward_refit_metadata_binds_saved_models_and_training_inputs(tmp_path, monkeypatch):
    config = {'coverage_end': 2026, 'horizon': 5, 'targets': {'vorp5': 'regression'}}
    (tmp_path / 'config.json').write_text(json.dumps(config))
    for name in ['data/processed/prospects.csv', 'data/processed/college_seasons.csv',
                 'research/features.py', 'research/models.py', 'output/experiments/freeze.json']:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('synthetic provenance fixture')
    freeze = {'targets': {'vorp5': {'selected': {'family': 'constant'}}}}
    monkeypatch.setattr(train_final, 'ROOT', tmp_path)
    monkeypatch.setattr(train_final, 'verify', lambda *args: None)
    monkeypatch.setattr(train_final, 'check_freeze', lambda *args: freeze)
    monkeypatch.setattr(train_final, 'load_data', lambda *args: (pd.DataFrame({'draft_year': [2021]}), {}))
    monkeypatch.setattr(train_final, 'fit_spec', lambda *args: {'model': 'synthetic fitted model', 'columns': []})
    protected = (tmp_path / 'output/experiments/freeze.json').read_bytes()
    train_final.main()
    folder = tmp_path / 'output/forward_models'
    metadata = json.loads((folder / 'metadata.json').read_text())
    assert metadata['model_hashes'] == {'vorp5.joblib': sha(folder / 'vorp5.joblib')}
    assert all(sha(tmp_path / path) == expected for path, expected in metadata['training_input_hashes'].items())
    assert metadata['scientific_freeze_sha256'] == sha(tmp_path / 'output/experiments/freeze.json')
    assert (tmp_path / 'output/experiments/freeze.json').read_bytes() == protected


def test_package_keeps_replication_inputs_and_excludes_backup_and_scratch(tmp_path, monkeypatch):
    experiments = tmp_path / 'output/experiments'
    experiments.mkdir(parents=True)
    receipt = {}
    for key, name in [('freeze_sha256', 'freeze.json'), ('predictions_sha256', 'test_predictions.csv'),
                      ('summary_sha256', 'test_summary.json'), ('scores_sha256', 'test_scores.csv')]:
        (experiments / name).write_text('{}')
        receipt[key] = sha(experiments / name)
    (experiments / 'test_receipt.json').write_text(json.dumps(receipt))
    (experiments / 'splits.json').write_text('[]')
    for name in ['data/raw/manifest.json', 'data/raw/source.csv', 'output/experiments/models/model.joblib',
                 'paper/research.tex', 'backups/original/snapshot.json', 'tmp/page.png', '.venv/library.py',
                 'output/audit/review_2026-10-13_bundle_validation.json']:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('{}')
    monkeypatch.setattr(package, 'ROOT', tmp_path)
    monkeypatch.setattr(package, 'check_freeze', lambda *args: {})
    # A fresh replication has no publication amendment.
    package.main()
    with ZipFile(tmp_path / 'output/nba_college_success.zip') as archive:
        members = set(archive.namelist())
        assert 'nba-college-success/data/raw/source.csv' in members
        assert 'nba-college-success/output/experiments/models/model.joblib' in members
        assert 'nba-college-success/paper/research.tex' in members
        assert 'nba-college-success/output/audit/review_2026-10-13_bundle_validation.json' not in members
        assert not any('/backups/' in path or '/tmp/' in path or '/.venv/' in path for path in members)
        assert archive.testzip() is None


def test_package_rejects_changed_sealed_development_log_before_writing(tmp_path, monkeypatch):
    log = tmp_path / 'output/experiments/trials.jsonl'
    log.parent.mkdir(parents=True)
    log.write_text('original development record')
    seal = tmp_path / SEAL
    seal.parent.mkdir(parents=True)
    seal.write_text(json.dumps({'files': {'output/experiments/trials.jsonl': sha(log)}}))
    log.write_text('changed development record')
    destination = tmp_path / 'output/nba_college_success.zip'
    destination.write_bytes(b'previous bundle retained')
    monkeypatch.setattr(package, 'ROOT', tmp_path)
    monkeypatch.setattr(package, 'check_freeze', lambda *args: {})
    with pytest.raises(ValueError, match='audit seal mismatch'):
        package.main()
    assert destination.read_bytes() == b'previous bundle retained'
    assert list(seal.parent.iterdir()) == [seal]
