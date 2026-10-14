"""Independent ESPN cross-checks; discrepancies are logged, never silently repaired."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from research.data import name

ROOT = Path(__file__).resolve().parent

def main():
    raw = ROOT / 'data/raw'
    college = pd.read_csv(ROOT / 'data/processed/college_seasons.csv', low_memory=False)
    nba = pd.read_csv(ROOT / 'data/processed/nba_seasons.csv')
    athletes = {}
    for path in raw.glob('draft_*.json'):
        for pick in json.loads(path.read_text())['picks']:
            player = pick['athlete']
            athletes[str(player.get('alternativeId', player['id']))] = player['displayName']
    records = []
    for path in sorted(raw.glob('espn_*_*.json')):
        athlete = path.stem.split('_')[-1]
        if athlete not in athletes:
            continue
        key = name(athletes[athlete])
        payload = json.loads(path.read_text())
        average = next((c for c in payload.get('categories', []) if c['name'] == 'averages'), None)
        if not average:
            continue
        is_college = path.name.startswith('espn_college')
        for record in average.get('statistics', []):
            year = record['season']['year']
            source = college[(college.key == key) & (college.year == year)] if is_college else nba[(nba.key == key) & (nba.season == year)]
            if len(source) != 1:
                continue
            official = dict(zip(average['names'], record['stats']))
            fields = {'gamesPlayed': 'GP', 'avgMinutes': 'mp', 'avgPoints': 'pts'} if is_college else {'gamesPlayed': 'g', 'gamesStarted': 'gs'}
            for espn_col, archive_col in fields.items():
                value = float(official[espn_col])
                archived = float(source.iloc[0][archive_col])
                tolerance = .11 if espn_col.startswith('avg') else 0
                records.append({'source': path.name, 'player': athletes[athlete], 'season': year,
                                'field': archive_col, 'espn': value, 'archive': archived,
                                'agrees': bool(abs(value - archived) <= tolerance),
                                'masked': bool(np.isnan(archived))})
    result = pd.DataFrame(records)
    result.to_csv(ROOT / 'data/processed/independent_source_checks.csv', index=False)
    summary = {'checks': len(result), 'disagreements': int((~result.agrees & ~result.masked).sum()),
               'masked_discrepancies': int(result.masked.sum()),
               'college_checks': int(result.source.str.startswith('espn_college').sum()),
               'nba_checks': int(result.source.str.startswith('espn_stats').sum()),
               'limitations': 'Convenience sample only. Agreement between college copies is not independent verification. ESPN does not publish VORP.'}
    (ROOT / 'data/processed/independent_checks.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    if not (result.agrees | result.masked).all():
        print(result[~result.agrees & ~result.masked].to_string(index=False))
        raise ValueError('Independent source discrepancy; inspect before development')

if __name__ == '__main__':
    main()
