"""Check the retrospective audit seal without rewriting the original freeze.

The seal dates from the October 13, 2026 review. It is a local integrity record,
not preregistration, historical point-in-time proof, or independent notarization.
"""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parent
SEAL = Path('reproducibility/review_2026-10-13_evidence_seal.json')


def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def verify_seal(root=ROOT):
    root = Path(root)
    record = json.loads((root / SEAL).read_text(encoding='utf-8'))
    for relative, expected in record['files'].items():
        path = root / relative
        if not path.is_file() or digest(path) != expected:
            raise ValueError(f'Retrospective audit seal mismatch: {relative}')
    return record


def create_seal(root=ROOT):
    root = Path(root)
    destination = root / SEAL
    if destination.exists():
        raise ValueError('Existing audit seal must not be replaced')
    manifest = json.loads((root / 'backups/pre_review_2026-10-13/manifest.json').read_text(encoding='utf-8'))
    protected_names = {'freeze.json', 'test_receipt.json', 'test_predictions.csv',
                       'test_scores.csv', 'test_summary.json', 'trials.jsonl',
                       'nested_predictions.csv', 'nested_scores.csv',
                       'selection_predictions.csv', 'splits.json'}
    scientific = {'research/data.py', 'research/features.py', 'research/models.py',
                  'research/experiment.py', 'config.json'}
    files = {}
    for item in manifest['files']:
        path = Path(item['path'])
        parts = path.parts
        keep = (item['path'] in scientific or parts[:2] in [('data', 'raw'), ('data', 'processed')]
                or (parts[:2] == ('output', 'experiments') and
                    (path.name in protected_names or 'models' in parts or 'frozen_publication_code' in parts))
                or (parts[:1] == ('reproducibility',) and path.name in {'freeze.json', 'test_receipt.json', 'splits.json', 'source_manifest.json'}))
        if keep:
            files[item['path']] = item['sha256']
    record = {'review_date': '2026-10-13', 'scope': 'Retrospective integrity seal of pre-review recorded evidence, including previously unbound development logs and splits.',
              'status': 'Local audit record; no claim of prespecification or external timestamp authority.',
              'backup_manifest': 'backups/pre_review_2026-10-13/manifest.json',
              'backup_file_count': manifest['file_count'],
              'unavailable_legacy_files': manifest['unavailable_files'], 'files': files}
    destination.write_text(json.dumps(record, indent=2), encoding='utf-8')
    verify_seal(root)
    print(f'Created retrospective seal for {len(files)} unchanged evidence files.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--create-from-backup', action='store_true')
    args = parser.parse_args()
    if args.create_from_backup:
        create_seal()
    else:
        record = verify_seal()
        print(f"Retrospective evidence seal passed: {len(record['files'])} files.")


if __name__ == '__main__':
    main()
