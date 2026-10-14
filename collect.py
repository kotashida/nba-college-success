"""Fetch and verify dated public college, draft, and NBA snapshots."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import time
from urllib.parse import quote

import requests

ROOT = Path(__file__).resolve().parent
SOURCES = {
    'college.csv': ('warrensuca/nba-role-player-prediction-model', '0524c1e21992bc3e55197a467ead6e6262c4c200', 'data/cbb.csv'),
    'nba_advanced.csv': ('warrensuca/nba-role-player-prediction-model', '0524c1e21992bc3e55197a467ead6e6262c4c200', 'data/nba_advanced.csv'),
    'nba_per_game.csv': ('warrensuca/nba-role-player-prediction-model', '0524c1e21992bc3e55197a467ead6e6262c4c200', 'data/nba_per_game.csv'),
    'college_schema_reference.R': ('mathgonzaga/NBADraftModel', '099a9fc5776a25d72ceae5fb9a8cb09b67890c1c', '1_clean_college_data.R'),
    'college_uncorrupted_2009.csv': ('mathgonzaga/NBADraftModel', '099a9fc5776a25d72ceae5fb9a8cb09b67890c1c', 'data/raw/trank_data (0).csv'),
}

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    folder = ROOT / 'data/raw'
    folder.mkdir(parents=True, exist_ok=True)
    manifest_path = folder / 'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    urls = {name: f'https://raw.githubusercontent.com/{repo}/{commit}/{quote(path)}'
            for name, (repo, commit, path) in SOURCES.items()}
    for index in range(1, 11):
        urls[f'college_original_{index}.csv'] = 'https://raw.githubusercontent.com/mathgonzaga/NBADraftModel/099a9fc5776a25d72ceae5fb9a8cb09b67890c1c/' + quote(f'data/raw/trank_data ({index}).csv')
    for athlete in ['4432166', '4432158', '4432816', '4278031']:
        urls[f'espn_stats_{athlete}.json'] = f'https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/{athlete}/stats?region=us&lang=en&contentorigin=espn&isqualified=true&page=1&limit=100'
    for athlete in ['4432166', '4432158', '4395628', '4396993']:
        urls[f'espn_college_{athlete}.json'] = f'https://site.web.api.espn.com/apis/common/v3/sports/basketball/mens-college-basketball/athletes/{athlete}/stats?region=us&lang=en&contentorigin=espn&isqualified=true&page=1&limit=100'
    for year in range(2008, 2022):
        urls[f'draft_{year}.json'] = f'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/draft?season={year}'
    for name, url in urls.items():
        path = folder / name
        if not path.exists():
            response = requests.get(url, timeout=90)
            response.raise_for_status()
            expected = manifest.get(name, {}).get('sha256')
            if expected and hashlib.sha256(response.content).hexdigest() != expected:
                raise ValueError(f'Provider response differs from recorded snapshot: {name}. Restore the recorded data bundle; do not overwrite provenance.')
            if name.startswith('draft_'):
                if len(response.json().get('picks', [])) < 50:
                    raise ValueError(f'Incomplete draft archive {name}')
            path.write_bytes(response.content)
            if name not in manifest:
                manifest[name] = {'url': url, 'retrieved_utc': datetime.now(timezone.utc).isoformat(),
                                  'sha256': digest(path), 'bytes': path.stat().st_size}
                manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
            print(name, path.stat().st_size, flush=True)
            time.sleep(.3)
        elif name not in manifest or digest(path) != manifest[name]['sha256']:
            raise ValueError(f'Unmanifested or changed input: {name}')
    # The undated combine cache cannot be reconstructed as a dated API snapshot.
    path = folder / 'combine.csv'
    if not path.exists():
        raise FileNotFoundError('Restore data/raw/combine.csv from the recorded data bundle. Its collection timestamp is unknown; a current API response is not an exact replacement.')
    if path.name not in manifest or digest(path) != manifest[path.name]['sha256']:
        raise ValueError('Unmanifested or changed input: combine.csv')
    print('Collection complete', flush=True)

if __name__ == '__main__':
    main()
