from io import StringIO
import json
import numpy as np
import pandas as pd
import pytest
from research import experiment
from research.data import sha

def test_final_test_label_shock_cannot_change_tuning(monkeypatch):
    frame = pd.DataFrame({'draft_year': np.repeat(range(2008, 2022), 40),
                          'height': np.tile(np.arange(40), 14) + 60.})
    frame['vorp5'] = np.sin(frame.height) + (frame.draft_year - 2008) / 10
    specs = [{'family': 'constant', 'group': 'college', 'transform': 'raw', 'params': {}},
             {'family': 'linear', 'group': 'college', 'transform': 'raw', 'params': {'kind': 'ridge', 'alpha': 10.}}]
    monkeypatch.setattr(experiment, 'candidates', lambda config, task: specs)
    config = {'seed': 199, 'horizon': 5, 'min_training': 35, 'targets': {'vorp5': 'regression'}, 'feature_groups': ['college']}
    first_log, second_log = StringIO(), StringIO()
    a = experiment.tune(frame, 2020, 'vorp5', {'college': ['height']}, config, first_log)
    frame.loc[frame.draft_year >= 2020, 'vorp5'] += 1000000
    b = experiment.tune(frame, 2020, 'vorp5', {'college': ['height']}, config, second_log)
    assert a[0] == b[0]
    assert first_log.getvalue() == second_log.getvalue()
    for candidate in a[3]:
        pd.testing.assert_frame_equal(a[3][candidate], b[3][candidate])

def test_changed_frozen_input_is_rejected(tmp_path):
    folder = tmp_path / 'output/experiments'
    folder.mkdir(parents=True)
    source = tmp_path / 'input.csv'
    source.write_text('x\n1\n')
    (folder / 'freeze.json').write_text(json.dumps({'hashes': {'input.csv': sha(source)}, 'model_hashes': {}}))
    experiment.check_freeze(tmp_path)
    source.write_text('x\n2\n')
    with pytest.raises(ValueError, match='Frozen input'):
        experiment.check_freeze(tmp_path)


@pytest.mark.parametrize('artifact', ['test_scores.csv', 'test_summary.json', 'test_predictions.csv'])
def test_consumed_receipt_checks_every_artifact(tmp_path, artifact):
    folder = tmp_path / 'output/experiments'
    folder.mkdir(parents=True)
    (folder / 'freeze.json').write_text(json.dumps({'hashes': {}, 'model_hashes': {}}))
    receipt = {}
    for key, file in [('freeze_sha256', 'freeze.json'), ('predictions_sha256', 'test_predictions.csv'),
                      ('summary_sha256', 'test_summary.json'), ('scores_sha256', 'test_scores.csv')]:
        if file != 'freeze.json':
            (folder / file).write_text('original')
        receipt[key] = sha(folder / file)
    (folder / 'test_receipt.json').write_text(json.dumps(receipt))
    experiment.check_freeze(tmp_path)
    (folder / artifact).write_text('changed')
    with pytest.raises(ValueError, match='Test receipt mismatch'):
        experiment.check_freeze(tmp_path)


def test_missing_receipt_cannot_reopen_consumed_evaluation(tmp_path):
    folder = tmp_path / 'output/experiments'
    folder.mkdir(parents=True)
    (folder / 'freeze.json').write_text(json.dumps({'hashes': {}, 'model_hashes': {}}))
    (folder / 'test_predictions.csv').write_text('recorded evidence')
    with pytest.raises(ValueError, match='without a test receipt'):
        experiment.check_freeze(tmp_path)
