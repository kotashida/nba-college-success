"""Independent audit checks must reject incomplete evidence and traded duplicates."""
import json

import pandas as pd
import pytest

from audit_external_sources import season_totals, retrieve
from review_evidence import SEAL, digest, verify_seal
from verify_review import check_prediction_coverage


def test_paper_compiler_isolates_stale_source_auxiliary_files(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from research import report
    paper = tmp_path / 'paper'
    paper.mkdir()
    (paper / 'five_year_nba_outcomes.tex').write_text('current manuscript fixture')
    (paper / 'five_year_nba_outcomes.aux').write_text('obsolete bibliography fixture')
    for folder in ['generated', 'figures']:
        (paper / folder).mkdir()
        (paper / folder / 'fixture').write_text('current asset')
    destination = tmp_path / 'scratch'
    monkeypatch.setenv('PDFLATEX', 'synthetic-compiler')
    class CheckedCompiler(Exception):
        pass
    def run(command, cwd, **kwargs):
        assert Path(cwd).resolve() == destination.resolve()
        assert (destination / 'five_year_nba_outcomes.tex').read_text() == 'current manuscript fixture'
        assert not (destination / 'five_year_nba_outcomes.aux').exists()
        assert (destination / 'generated/fixture').exists()
        assert (destination / 'figures/fixture').exists()
        raise CheckedCompiler
    from pathlib import Path
    monkeypatch.setattr(report.subprocess, 'run', run)
    with pytest.raises(CheckedCompiler):
        report._compile_paper(tmp_path, destination)
    assert (paper / 'five_year_nba_outcomes.aux').read_text() == 'obsolete bibliography fixture'


def test_external_traded_season_prefers_provider_total():
    names = ['gamesPlayed', 'gamesStarted', 'avgMinutes']
    stints = [{'teamId': '23', 'teamSlug': 'sacramento-kings', 'stats': ['51', '51', '34.5']},
              {'teamId': '11', 'teamSlug': 'indiana-pacers', 'stats': ['26', '26', '36.1']}]
    total = {'displayName': '2021-22 Totals', 'teamSlug': '2021-22 Totals', 'stats': ['77', '77', '35.0']}
    g, gs, minutes, tolerance = season_totals(stints + [total], names)
    assert (g, gs, minutes) == (77., 77., 2695.)
    assert tolerance < 5
    assert season_totals(stints, names)[:2] == (77., 77.)
    with pytest.raises(ValueError, match='Ambiguous'):
        season_totals(stints + [total, total], names)


def test_external_duplicate_stints_are_rejected():
    row = {'teamId': '11', 'stats': ['26', '26', '36.1']}
    with pytest.raises(ValueError, match='Duplicate'):
        season_totals([row, row], ['gamesPlayed', 'gamesStarted', 'avgMinutes'])


def test_coverage_rejects_missing_player_extra_player_and_duplicate():
    prospects = pd.DataFrame({'player': ['A', 'B'], 'draft_year': [2020, 2020], 'vorp5': [1., 2.]})
    predictions = pd.DataFrame({'player': ['A', 'B'], 'year': [2020, 2020],
                                'target': ['vorp5', 'vorp5'], 'model': ['selected', 'selected'],
                                'truth': [1., 2.], 'prediction': [1.5, 1.5]})
    assert check_prediction_coverage(predictions, prospects, [2020], ['selected'], ['vorp5']) == 1
    for changed in [predictions.iloc[:1], predictions.assign(player=['A', 'C']),
                    pd.concat([predictions, predictions.iloc[:1]], ignore_index=True)]:
        with pytest.raises(ValueError, match='coverage|Duplicate'):
            check_prediction_coverage(changed, prospects, [2020], ['selected'], ['vorp5'])


def test_retrospective_seal_detects_development_log_change(tmp_path):
    log = tmp_path / 'output/experiments/trials.jsonl'
    log.parent.mkdir(parents=True)
    log.write_text('original recorded development evidence')
    seal = tmp_path / SEAL
    seal.parent.mkdir(parents=True)
    seal.write_text(json.dumps({'files': {'output/experiments/trials.jsonl': digest(log)}}))
    verify_seal(tmp_path)
    log.write_text('changed development evidence')
    with pytest.raises(ValueError, match='audit seal mismatch'):
        verify_seal(tmp_path)


@pytest.mark.parametrize('changed', [True, False])
def test_external_cache_restoration_preserves_expected_snapshot_provenance(tmp_path, monkeypatch, changed):
    import hashlib
    from types import SimpleNamespace
    import audit_external_sources
    payload = b'{"id":"fixture"}'
    expected = {'url': 'https://example.org/audit', 'retrieved_utc': '2026-10-13T00:00:00Z',
                'http_status': 200, 'bytes': len(payload),
                'sha256': hashlib.sha256(payload).hexdigest()}
    manifest = {'fixture.json': expected}
    manifest_path = tmp_path / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2))
    original = manifest_path.read_bytes()
    response_payload = b'{"id":"changed"}' if changed else payload
    monkeypatch.setattr(audit_external_sources.requests, 'get', lambda *args, **kwargs: SimpleNamespace(
        status_code=200, content=response_payload, json=lambda: json.loads(response_payload)))
    task = ('fixture.json', 'https://example.org/audit')
    if changed:
        with pytest.raises(ValueError, match='differs from recorded audit snapshot'):
            retrieve(task, tmp_path, manifest, fetch=True)
        assert not (tmp_path / 'fixture.json').exists()
    else:
        name, record = retrieve(task, tmp_path, manifest, fetch=True)
        assert name == 'fixture.json' and record == expected
        assert (tmp_path / name).read_bytes() == payload
    assert manifest_path.read_bytes() == original
    assert manifest == {'fixture.json': expected}
