"""Post-evaluation ESPN transcription checks, separate from frozen input data.

Fetches only with --fetch. Cached responses support offline rechecking. Empty
NBA responses never constitute independent proof of nonparticipation. Selection
of this review sample is post hoc and provides no new performance evaluation.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import argparse
import hashlib
import json
import unicodedata
import re

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent
SAMPLE = ['Jalen Brunson', 'Shake Milton', "Devonte' Graham", 'Ja Morant',
          'Cam Reddish', 'Ignas Brazdeikis', 'Tyrese Haliburton',
          'Anthony Edwards', 'Desmond Bane', 'Isaiah Joe', 'Justinian Jessup',
          'Scottie Barnes', 'Aaron Wiggins', 'Marcus Zegarowski', 'Balsa Koprivica']
DIRECTORY = Path('output/audit/review_2026-10-13_external_sources')


def canonical_name(value):
    value = unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', value)


def season_totals(rows, names):
    """Use an explicit total row if present; otherwise sum separate stints."""
    totals = [row for row in rows if str(row.get('teamId')) in {'0', '-1'}
              or row.get('teamSlug', '').lower() in {'tot', 'total', 'multiple-teams'}
              or re.search(r'\btotals?\b', row.get('teamSlug', '').lower())
              or re.search(r'\btotals?\b', row.get('displayName', '').lower())]
    if len(totals) > 1:
        raise ValueError('Ambiguous ESPN total rows')
    chosen = totals or rows
    teams = [row.get('teamId') for row in chosen]
    if len(teams) != len(set(teams)):
        raise ValueError('Duplicate ESPN team/season row')
    values = [dict(zip(names, row['stats'])) for row in chosen]
    g = sum(float(row['gamesPlayed']) for row in values)
    gs = sum(float(row['gamesStarted']) for row in values)
    approximate_minutes = sum(float(row['gamesPlayed']) * float(row['avgMinutes']) for row in values)
    return g, gs, approximate_minutes, .055 * g + 1e-8


def retrieve(task, directory, manifest, fetch=False):
    """Restore an audit snapshot without replacing its recorded provenance."""
    filename, url = task
    path = Path(directory) / filename
    expected = manifest.get(filename)
    if path.exists():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if expected is None or digest != expected['sha256']:
            raise ValueError(f'Unverified cached external source: {filename}')
        return filename, expected
    if not fetch:
        raise ValueError(f'Missing cached source: {filename}; run --fetch with network access')
    response = requests.get(url, timeout=25)
    # Preserve 404 as unavailable evidence, never as a fabricated zero.
    if response.status_code not in {200, 404}:
        response.raise_for_status()
    digest = hashlib.sha256(response.content).hexdigest()
    if expected is not None and digest != expected['sha256']:
        raise ValueError(f'Provider response differs from recorded audit snapshot: {filename}; restore the original audit bundle')
    response.json()
    path.write_bytes(response.content)
    if expected is not None:
        return filename, expected
    return filename, {'url': url, 'retrieved_utc': datetime.now(timezone.utc).isoformat(),
                      'http_status': response.status_code, 'bytes': len(response.content),
                      'sha256': digest}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    args = parser.parse_args()
    directory = ROOT / DIRECTORY
    directory.mkdir(parents=True, exist_ok=True)
    prospects = pd.read_csv(ROOT / 'data/processed/prospects.csv')
    nba = pd.read_csv(ROOT / 'data/processed/nba_seasons.csv')
    # Explicit stratification covers four contemporary classes, high/modest/low
    # recorded participation, traded seasons and all three final-test assumed zeros.
    sample = prospects[prospects.player.isin(SAMPLE)].copy()
    if set(sample.player) != set(SAMPLE):
        raise ValueError('Review sample identities do not match the recorded study')
    manifest_path = directory / 'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    tasks = []
    for row in sample.itertuples():
        pid = str(row.espn_id)
        tasks += [(f'{pid}_identity.json', f'https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba/athletes/{pid}?lang=en&region=us'),
                  (f'{pid}_stats.json', f'https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/{pid}/stats?region=us&lang=en&contentorigin=espn&isqualified=true&seasontype=2&page=1&limit=100')]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for filename, record in pool.map(lambda task: retrieve(task, directory, manifest, args.fetch), tasks):
            manifest[filename] = record
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    comparisons, identities = [], []
    for row in sample.itertuples():
        pid = str(row.espn_id)
        identity = json.loads((directory / f'{pid}_identity.json').read_text())
        stats = json.loads((directory / f'{pid}_stats.json').read_text())
        matched = (str(identity.get('id')) == pid and
                   canonical_name(identity.get('displayName')) == canonical_name(row.player))
        identities.append({'player': row.player, 'draft_year': row.draft_year, 'espn_id': pid,
                           'provider_name': identity.get('displayName'), 'identity_confirmed': matched,
                           'assumed_nonparticipant_in_original': pd.isna(row.nba_id),
                           'status': 'identity confirmed' if matched else 'unresolved; endpoint unavailable or identity mismatch'})
        if not matched:
            continue
        averages = next((c for c in stats.get('categories', []) if c['name'] == 'averages'), None)
        if averages is None or not averages.get('statistics'):
            identities[-1]['status'] = 'identity confirmed; no regular-season rows returned, not proof of nonparticipation'
            continue
        season_filter = next((f for f in stats.get('filters', []) if f['name'] == 'seasontype'), None)
        if season_filter is None or season_filter['value'] != '2':
            raise ValueError('Source does not confirm regular-season statistics')
        by_season = {}
        for record in averages.get('statistics', []):
            year = int(record['season']['year'])
            if row.draft_year < year <= row.draft_year + 5:
                by_season.setdefault(year, []).append(record)
        for year, records in sorted(by_season.items()):
            original = nba[nba.nba_id.eq(row.nba_id) & nba.season.eq(year)]
            if len(original) != 1:
                raise ValueError(f'Independent appearance lacks unique recorded NBA season: {row.player}/{year}')
            g, gs, minutes, tolerance = season_totals(records, averages['names'])
            for field, value, limit in [('g', g, 0.), ('gs', gs, 0.), ('mp', minutes, tolerance)]:
                archived = float(original.iloc[0][field])
                comparisons.append({'player': row.player, 'draft_year': row.draft_year, 'season': year,
                                    'field': field, 'espn': value, 'archive': archived, 'tolerance': limit,
                                    'agrees': abs(value - archived) <= limit,
                                    'source_file': f'{pid}_stats.json',
                                    'note': 'MP comparison uses rounding bounds on games times one-decimal average minutes' if field == 'mp' else 'exact count'})
    table = pd.DataFrame(comparisons)
    table.to_csv(directory / 'comparisons.csv', index=False)
    pd.DataFrame(identities).to_csv(directory / 'identities.csv', index=False)
    summary = {'review_date': '2026-10-13', 'sample_policy': 'Post hoc source audit across 2018-2021, high/modest/low service, trades and the three final-test assumed nonparticipants; no fitting or performance changes.',
               'sample_players': len(sample), 'identity_confirmed': sum(x['identity_confirmed'] for x in identities),
               'comparison_players': int(table.player.nunique()) if len(table) else 0,
               'season_field_comparisons': len(table), 'disagreements': int((~table.agrees).sum()) if len(table) else 0,
               'unresolved_identities': [x['player'] for x in identities if not x['identity_confirmed']],
               'limitations': 'No independent VORP validation. One-decimal averages give only rounding-bounded MP checks. Missing/empty NBA endpoints are not proof of no NBA appearances. Does not establish historical source vintages or full-population accuracy.'}
    (directory / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))
    if len(table) and not table.agrees.all():
        print(table[~table.agrees].to_string(index=False))
        raise ValueError('External discrepancy: retain original and investigate; do not silently alter frozen data')


if __name__ == '__main__':
    main()
