"""Apply forward research models to canonical precomputed prospect feature CSVs."""
from pathlib import Path
import argparse
import json
import joblib
import numpy as np
import pandas as pd
from research.experiment import predict_spec
from research.data import sha

ROOT = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    folder = ROOT / 'output/forward_models'
    metadata = json.loads((folder / 'metadata.json').read_text())
    frame = pd.read_csv(args.input)
    if not {'player', 'prediction_year'}.issubset(frame.columns):
        raise ValueError('player and prediction_year are required')
    if frame.empty:
        raise ValueError('At least one prospect row is required')
    players = frame.player.astype('string').str.strip()
    if players.isna().any() or players.eq('').any():
        raise ValueError('Every prospect requires a nonblank player name')
    years = pd.to_numeric(frame.prediction_year, errors='coerce')
    values = years.to_numpy(dtype=float, na_value=np.nan)
    if not (np.isfinite(values) & (values == np.floor(values)) &
            (values >= 1) & (values <= 9999)).all():
        raise ValueError('prediction_year must contain finite integer calendar years')
    frame['player'] = players
    frame['prediction_year'] = years.astype('int64')
    if frame.prediction_year.le(metadata['fitting_origin']).any():
        raise ValueError('Forward models cannot create historical validation predictions')
    model_hashes = metadata.get('model_hashes')
    if not isinstance(model_hashes, dict):
        raise ValueError('Forward model integrity metadata is missing; restore a sealed bundle or run train_final.py')
    # Validate every artifact before loading any serialized estimator.
    for target in metadata['target_tasks']:
        filename = f'{target}.joblib'
        path = folder / filename
        if not path.is_file() or model_hashes.get(filename) != sha(path):
            raise ValueError(f'Forward model integrity mismatch: {filename}')
    def columns(fitted):
        if isinstance(fitted, list):
            return set().union(*(columns(member) for member in fitted))
        return set(fitted['columns'])
    result = frame[['player', 'prediction_year']].copy()
    for target, task in metadata['target_tasks'].items():
        fitted = joblib.load(folder / f'{target}.joblib')
        missing = columns(fitted) - set(frame.columns)
        if missing:
            raise ValueError(f'Missing canonical feature columns for {target}: {sorted(missing)}. Supply explicit NaN for unrecorded measurements.')
        result[target] = predict_spec(fitted, frame, task)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print('Saved forward research forecasts. Population and source-quality limitations still apply.')

if __name__ == '__main__':
    main()
