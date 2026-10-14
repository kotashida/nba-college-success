"""NBA prospect research CLI. Run stages in order; final test is write-once."""
import argparse
from pathlib import Path
import json
import warnings
import numpy as np

from research.data import build
from research.features import make_features

ROOT = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['data', 'develop', 'evaluate', 'report', 'paper', 'verify', 'all'])
    args = parser.parse_args()
    config = json.loads((ROOT / 'config.json').read_text())
    np.random.seed(config['seed'])
    warnings.filterwarnings('ignore', message=r'.*`sklearn\.utils\.parallel\.delayed`.*')
    if args.stage in ['data', 'all']:
        build(ROOT, config)
    if args.stage in ['develop', 'all']:
        from research.experiment import develop
        develop(ROOT, config)
    if args.stage in ['evaluate', 'all']:
        from research.experiment import evaluate
        evaluate(ROOT, config)
    if args.stage in ['report', 'all']:
        from research.report import report
        report(ROOT, config)
    if args.stage in ['paper', 'all']:
        from research.report import compile_paper
        compile_paper(ROOT)
    if args.stage in ['verify', 'all']:
        from research.experiment import verify
        verify(ROOT, config)

if __name__ == '__main__':
    main()
