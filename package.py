"""Build a portable research bundle with snapshots, models, and manuscript."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json
import shutil
import os
from research.experiment import check_freeze
from research.data import sha
from review_evidence import SEAL, verify_seal

ROOT = Path(__file__).resolve().parent

def bundle_paths(root):
    """Discover active replication files while excluding local archives and scratch."""
    root = Path(root)
    excluded_directories = {'.venv', 'venv', 'env', '__pycache__', '.pytest_cache', '.git',
                            'legacy', 'backups', 'tmp', 'build', 'dist', '.ruff_cache', '.mypy_cache',
                            '.publication-check', '.idea', '.vscode', '.tox', '.nox', '.conda', 'htmlcov'}
    paths = []
    for folder, directories, files in os.walk(root):
        directories[:] = sorted(d for d in directories if d not in excluded_directories and not d.endswith('.egg-info'))
        for name in sorted(files):
            path = Path(folder) / name
            # An archive's external receipt cannot contain its own ZIP digest.
            if path == root / 'output/audit/review_2026-10-13_bundle_validation.json':
                continue
            if name in ['.DS_Store', 'Thumbs.db'] or (name.startswith('.env') and name != '.env.example'):
                continue
            if path.suffix in ['.zip', '.pyc', '.tmp']:
                continue
            if path.parent == root / 'paper' and (name == 'main.pdf' or path.suffix in ['.aux', '.out', '.log', '.toc', '.fls', '.fdb_latexmk'] or name.endswith('.synctex.gz')):
                continue
            if path.parent == root / 'output/paper' and path.suffix in ['.png', '.aux', '.out', '.log', '.pdf']:
                continue
            paths.append(path)
    return paths

def main():
    check_freeze(ROOT)
    if (ROOT / SEAL).exists():
        verify_seal(ROOT)
    evidence = ROOT / 'reproducibility'
    evidence.mkdir(exist_ok=True)
    experiments = ROOT / 'output/experiments'
    receipt = json.loads((experiments / 'test_receipt.json').read_text())
    for key, name in [('freeze_sha256', 'freeze.json'), ('predictions_sha256', 'test_predictions.csv'),
                      ('summary_sha256', 'test_summary.json'), ('scores_sha256', 'test_scores.csv')]:
        if sha(experiments / name) != receipt[key]:
            raise ValueError(f'Evaluation receipt mismatch: {name}')
    for name in ['freeze.json', 'test_receipt.json', 'splits.json']:
        shutil.copyfile(experiments / name, evidence / name)
    amendment = experiments / 'publication_amendment.json'
    if amendment.exists():
        shutil.copyfile(amendment, evidence / amendment.name)
    elif (evidence / amendment.name).exists():
        raise ValueError('A copied publication amendment has no runtime original; preserve and resolve it before packaging')
    manifest = json.loads((ROOT / 'data/raw/manifest.json').read_text())
    source_manifest = {name: {k: value for k, value in record.items()
                             if k in ['url', 'retrieved_utc', 'sha256', 'bytes']}
                       for name, record in manifest.items()}
    (evidence / 'source_manifest.json').write_text(json.dumps(source_manifest, indent=2), encoding='utf-8')
    destination = ROOT / 'output/nba_college_success.zip'
    paths = bundle_paths(ROOT)
    with ZipFile(destination, 'w', compression=ZIP_DEFLATED, compresslevel=6) as archive:
        for path in paths:
            archive.write(path, (Path('nba-college-success') / path.relative_to(ROOT)).as_posix())
    print(f'{destination.name}: {len(paths)} files, {destination.stat().st_size / 1024**2:.1f} MiB')

if __name__ == '__main__':
    main()
