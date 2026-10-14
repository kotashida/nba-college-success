"""Refit frozen choices on all mature labels for forward research use; no retuning."""
from pathlib import Path
import json
import joblib
from research.experiment import check_freeze, load_data, fit_spec, verify
from research.data import sha

ROOT = Path(__file__).resolve().parent

def main():
    config = json.loads((ROOT / 'config.json').read_text())
    verify(ROOT, config)
    freeze = check_freeze(ROOT)
    frame, groups = load_data(ROOT)
    directory = ROOT / 'output/forward_models'
    directory.mkdir(parents=True, exist_ok=True)
    for target, task in config['targets'].items():
        fitted = fit_spec(frame, config['coverage_end'], target, freeze['targets'][target]['selected'], groups, config)
        joblib.dump(fitted, directory / f'{target}.joblib')
    metadata = {'fitting_origin': config['coverage_end'], 'latest_training_class': config['coverage_end'] - config['horizon'],
                'n_mature': len(frame), 'target_tasks': config['targets'], 'specifications': {t: d['selected'] for t, d in freeze['targets'].items()},
                'model_hashes': {f'{target}.joblib': sha(directory / f'{target}.joblib') for target in config['targets']},
                'scientific_freeze_sha256': sha(ROOT / 'output/experiments/freeze.json'),
                'training_input_hashes': {path: sha(ROOT / path) for path in [
                    'config.json', 'data/processed/prospects.csv', 'data/processed/college_seasons.csv',
                    'research/features.py', 'research/models.py']},
                'status': 'Research refits only; no new out-of-sample performance claim. Selected specifications unchanged.',
                'population': 'NCAA prospects conditional on being drafted; not all college players.'}
    (directory / 'metadata.json').write_text(json.dumps(metadata, indent=2))
    print(f'Refit five fixed specifications on {len(frame)} mature records. No new test scores.', flush=True)

if __name__ == '__main__':
    main()
