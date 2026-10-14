"""Generate a clearly synthetic interface fixture and test forward CSV prediction."""
from pathlib import Path
import subprocess
import sys
import pandas as pd
from research.experiment import load_data

ROOT = Path(__file__).resolve().parent

def main():
    frame, groups = load_data(ROOT)
    record = {'player': 'SYNTHETIC_INTERFACE_TEST_NOT_A_REAL_PROSPECT', 'prediction_year': 2027}
    for col in groups['hybrid']:
        record[col] = 'ACC' if col == 'conf' else 'PG' if col == 'position' else frame[col].median()
    directory = ROOT / 'output/forward_models'
    input_path, output_path = directory / 'synthetic_interface.csv', directory / 'synthetic_predictions.csv'
    pd.DataFrame([record]).to_csv(input_path, index=False)
    subprocess.run([sys.executable, str(ROOT / 'predict.py'), str(input_path), str(output_path)], check=True)
    result = pd.read_csv(output_path)
    assert len(result) == 1 and result[['vorp5', 'minutes5', 'active5', 'rotation5', 'starter5']].notna().all().all()
    print('Synthetic inference smoke test passed. This fixture provides no scientific performance evidence.')

if __name__ == '__main__':
    main()
