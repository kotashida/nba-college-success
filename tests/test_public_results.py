"""The repository-only scorer must reject altered receipt-bound results."""
import json

import pytest

from verify_results import digest, verify_results


@pytest.mark.parametrize('changed', ['test_predictions.csv', 'test_scores.csv', 'test_summary.json'])
def test_public_verifier_rejects_corrupt_result_before_reading_other_inputs(tmp_path, changed):
    folder = tmp_path / 'output/experiments'
    folder.mkdir(parents=True)
    receipt = {}
    for key, filename in [('freeze_sha256', 'freeze.json'), ('predictions_sha256', 'test_predictions.csv'),
                          ('scores_sha256', 'test_scores.csv'), ('summary_sha256', 'test_summary.json')]:
        (folder / filename).write_text('original recorded result fixture')
        receipt[key] = digest(folder / filename)
    (folder / 'test_receipt.json').write_text(json.dumps(receipt))
    (folder / changed).write_text('altered result fixture')
    with pytest.raises(ValueError, match='Published evaluation receipt mismatch'):
        verify_results(tmp_path)
    # No source data, models, or supplementary seal are provided by this fixture;
    # receipt failures must be detected before any such dependency is consulted.
