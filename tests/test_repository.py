import hashlib
import json
from types import SimpleNamespace

import pytest

import collect
from research.data import sha
from research.experiment import check_freeze


def test_cli_integrity_registration_cannot_change_execution(tmp_path):
    folder = tmp_path / 'output/experiments'
    folder.mkdir(parents=True)
    original = folder / 'original_run.py'
    original.write_text('"""CLI."""\nx = 1\n')
    current = tmp_path / 'run.py'
    current.write_text('"""Research CLI."""\nx = 1\n')
    (folder / 'freeze.json').write_text(json.dumps({
        'hashes': {'run.py': sha(original)}, 'model_hashes': {}}))

    def register():
        (folder / 'publication_amendment.json').write_text(json.dumps({
            'run.py': {'preserved_original': original.relative_to(tmp_path).as_posix(),
                       'revised_sha256': sha(current)}}))

    register()
    check_freeze(tmp_path)
    current.write_text('"""Research CLI."""\nx = 2\n')
    register()
    with pytest.raises(ValueError, match='Frozen input/code/model'):
        check_freeze(tmp_path)


def setup_collector(tmp_path, monkeypatch):
    folder = tmp_path / 'data/raw'
    folder.mkdir(parents=True)
    payload = b'x\n1\n'
    manifest = folder / 'manifest.json'
    manifest.write_text(json.dumps({'college.csv': {
        'sha256': hashlib.sha256(payload).hexdigest(), 'bytes': len(payload),
        'retrieved_utc': '2026-01-01T00:00:00Z', 'url': 'https://example.org/source'}}))
    monkeypatch.setattr(collect, 'ROOT', tmp_path)
    monkeypatch.setattr(collect, 'SOURCES', {'college.csv': ('provider/source', 'commit', 'college.csv')})
    monkeypatch.setattr(collect.time, 'sleep', lambda _: None)
    return folder, manifest, payload


def test_collector_rejects_changed_provider_response(tmp_path, monkeypatch):
    folder, manifest, _ = setup_collector(tmp_path, monkeypatch)
    original = manifest.read_bytes()
    monkeypatch.setattr(collect.requests, 'get', lambda *a, **k: SimpleNamespace(
        content=b'changed', raise_for_status=lambda: None))
    with pytest.raises(ValueError, match='differs from recorded snapshot'):
        collect.main()
    assert not (folder / 'college.csv').exists()
    assert manifest.read_bytes() == original


def test_collector_restoration_preserves_manifest_bytes(tmp_path, monkeypatch):
    folder, manifest, payload = setup_collector(tmp_path, monkeypatch)
    original = manifest.read_bytes()

    def response(url, **kwargs):
        if url.endswith('/college.csv'):
            return SimpleNamespace(content=payload, raise_for_status=lambda: None)
        raise RuntimeError('Stop after restored snapshot')

    monkeypatch.setattr(collect.requests, 'get', response)
    with pytest.raises(RuntimeError, match='Stop after restored snapshot'):
        collect.main()
    assert (folder / 'college.csv').read_bytes() == payload
    assert manifest.read_bytes() == original
