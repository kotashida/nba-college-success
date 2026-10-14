"""Dated college records, school-confirmed joins, and fixed-horizon outcomes."""
from pathlib import Path
import hashlib
import json
import re
import unicodedata

import numpy as np
import pandas as pd

COLS = 'player_name team conf GP Min_per Ortg usg eFG TS_per ORB_per DRB_per AST_per TO_per FTM FTA FT_per twoPM twoPA twoP_per TPM TPA TP_per blk_per stl_per ftr yr ht num porpag adjoe pfr year pid type Rec_Rank ast_tov rim_made rim_att mid_made mid_att rim_pct mid_pct dunk_made dunk_att dunk_pct pick drtg adrtg dporpag stops bpm obpm dbpm gbpm mp ogbpm dgbpm oreb dreb treb ast stl blk pts role extra'.split()
ALIASES = {'edrice adebayo': 'bam adebayo', 'nicolas claxton': 'nic claxton',
 'mohamed bamba': 'mo bamba', 'cameron reddish': 'cam reddish',
 'sviatoslav mykhailiuk': 'svi mykhailiuk', 'james mcadoo': 'james michael mcadoo',
 'wesley iwundu': 'wes iwundu', 'jeff taylor': 'jeffery taylor',
 'patrick mills': 'patty mills', 'henry walker': 'bill walker',
 'william walker': 'bill walker', 'brandon boston': 'bj boston',
 'herbert jones': 'herb jones', 'cameron thomas': 'cam thomas',
 'nahshon hyland': 'bones hyland', 'gregory brown': 'greg brown',
 'joseph young': 'joe young', 'roy devyn marble': 'devyn marble'}
SCHOOL_ALIASES = {'uconn': 'connecticut', 'usc': 'southern california',
 'lsu': 'louisiana state', 'ole miss': 'mississippi', 'pitt': 'pittsburgh',
 'ucf': 'central florida', 'vcu': 'virginia commonwealth',
 'unlv': 'nevada las vegas', 'smu': 'southern methodist',
 'byu': 'brigham young', 'utsa': 'texas san antonio',
 'st johns': 'saint johns', 'st josephs': 'saint josephs',
 'st marys': 'saint marys', 'saint marys ca': 'saint marys',
 'miami fl': 'miami', 'miami florida': 'miami', 'nc state': 'north carolina state',
 'ncstate': 'north carolina state', 'unc': 'north carolina',
 'cal state northridge': 'california state northridge',
 'cs northridge': 'california state northridge',
 'san jose st': 'san jose state', 'utah st': 'utah state',
 'iupui': 'iu indianapolis', 'tennessee martin': 'ut martin',
 'college of charleston': 'charleston', 'detroit mercy': 'detroit',
 'louisiana lafayette': 'louisiana'}
PHYSICAL = {'HEIGHT_WO_SHOES': ('combine_height', 60, 95), 'WEIGHT': ('weight', 120, 400),
 'WINGSPAN': ('wingspan', 60, 105), 'STANDING_REACH': ('reach', 75, 125),
 'BODY_FAT_PCT': ('body_fat', 1, 35), 'HAND_LENGTH': ('hand_length', 5, 13),
 'HAND_WIDTH': ('hand_width', 5, 15), 'STANDING_VERTICAL_LEAP': ('standing_vertical', 10, 50),
 'MAX_VERTICAL_LEAP': ('max_vertical', 10, 55), 'LANE_AGILITY_TIME': ('agility', 8, 18),
 'THREE_QUARTER_SPRINT': ('sprint', 2, 5), 'BENCH_PRESS': ('bench', 0, 40)}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def clean(value):
    value = unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode().lower()
    value = re.sub(r'[^a-z0-9 ]', '', value)
    return ' '.join(value.split())

def name(value):
    value = re.sub(r'\s+(jr|sr|ii|iii|iv)$', '', clean(value))
    return ALIASES.get(value, value)

def school(value):
    value = clean(value)
    value = re.sub(r'\bst\b', 'state', value)
    value = re.sub(r'\buniversity\b', '', value).strip()
    value = SCHOOL_ALIASES.get(value, value)
    # Torvik abbreviates several non-state Saint schools.
    return {'state johns': 'saint johns', 'state josephs': 'saint josephs',
            'state marys': 'saint marys'}.get(value, value)

def height(value):
    value = str(value)
    match = re.fullmatch(r'(\d)-(\d{1,2})', value)
    if match:
        feet, inches = map(int, match.groups())
    else:
        match = re.fullmatch(r'(\d{1,2})-(May|Jun|Jul)', value)
        reverse = re.fullmatch(r'(May|Jun|Jul)-(\d{2})', value)
        months = {'May': 5, 'Jun': 6, 'Jul': 7}
        if match:
            inches, month = match.groups()
            feet, inches = months[month], int(inches)
        elif reverse:
            month, inches = reverse.groups()
            feet, inches = months[month], int(inches)
        else:
            return np.nan
    result = 12 * feet + inches
    return result if 0 <= inches <= 11 and 60 <= result <= 90 else np.nan

def canonical_nba(frame):
    frame = frame[frame.lg.eq('NBA') & frame.season.ge(1995)].copy()
    rows = []
    for (pid, year), group in frame.groupby(['player_id', 'season'], sort=True):
        totals = group[group.team.str.match(r'^(TOT|\d+TM)$')]
        if len(totals) > 1:
            raise ValueError(f'Multiple NBA totals for {pid}, {year}')
        used = totals if len(totals) else group.drop_duplicates('team')
        if not len(totals) and len(group) != len(used):
            raise ValueError('Conflicting duplicate NBA stints')
        record = {'nba_id': pid, 'season': int(year), 'player': used.player.iloc[0],
                  'key': name(used.player.iloc[0]), 'source_rows': len(group)}
        for col in ['vorp', 'mp', 'g', 'gs']:
            record[col] = pd.to_numeric(used[col], errors='coerce').sum(min_count=len(used))
        rows.append(record)
    return pd.DataFrame(rows)

def window_outcomes(seasons, year, horizon=5):
    window = seasons[seasons.season.between(year + 1, year + horizon)]
    if window[['vorp', 'mp', 'g', 'gs']].isna().any().any():
        return None
    return {'vorp5': float(window.vorp.sum()), 'minutes5': float(window.mp.sum()),
            'active5': int(window.g.gt(0).sum()),
            'rotation5': int(window.mp.ge(1000).sum() >= 3),
            'starter5': int(window.gs.ge(41).sum() >= 2)}

def build(root, config):
    root = Path(root)
    raw, out = root / 'data/raw', root / 'data/processed'
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((raw / 'manifest.json').read_text())
    for file, meta in manifest.items():
        if sha(raw / file) != meta['sha256']:
            raise ValueError(f'Source changed: {file}')
    secondary = pd.read_csv(raw / 'college.csv', low_memory=False)
    secondary.columns = COLS
    secondary['origin'] = 'secondary; reversible height corruption'
    originals = []
    for path in sorted(raw.glob('college_original_*.csv')) + [raw / 'college_uncorrupted_2009.csv']:
        data = pd.read_csv(path, header=None, low_memory=False)
        if data.shape[1] != len(COLS):
            raise ValueError('College schema changed')
        data.columns = COLS
        data['origin'] = path.name
        originals.append(data)
    original = pd.concat(originals, ignore_index=True)
    for frame in [secondary, original]:
        frame['key'] = frame.player_name.map(name)
        frame['school_key'] = frame.team.map(school)
        frame['height'] = frame.ht.map(height)
        for col in COLS:
            if col not in ['player_name', 'team', 'conf', 'yr', 'ht', 'num', 'type', 'role']:
                frame[col] = pd.to_numeric(frame[col], errors='coerce')
    # Compare copies on player ID, year and school, never on eventual draft pick.
    comparison = original.merge(secondary, on=['pid', 'year', 'school_key'], suffixes=('_a', '_b'))
    checks = {}
    for col in ['GP', 'bpm', 'pts', 'FTM', 'FTA', 'TPM', 'TPA', 'height']:
        a, b = comparison[col + '_a'], comparison[col + '_b']
        usable = a.notna() & b.notna()
        checks[col] = {'compared': int(usable.sum()),
                      'disagreements': int((~np.isclose(a[usable], b[usable], atol=1e-8)).sum())}
        if checks[col]['disagreements']:
            raise ValueError(f'College copies disagree on {col}')
    college = pd.concat([original, secondary[~secondary.year.isin(original.year.unique())]], ignore_index=True)
    college = college.drop_duplicates(['pid', 'year', 'school_key'])
    college = college[college.GP.ge(1) & college.year.between(2008, 2021)].copy()
    quality_policy = json.loads((raw / 'source_quality_policy.json').read_text())
    for flag in quality_policy['masked_college_fields']:
        affected = college.key.eq(name(flag['player'])) & college.year.eq(flag['season'])
        if affected.sum() != 1:
            raise ValueError('Quality flag identity is not unique')
        college.loc[affected, flag['field']] = np.nan
    for col in ['FTM', 'FTA', 'twoPM', 'twoPA', 'TPM', 'TPA']:
        if college[col].dropna().lt(0).any():
            raise ValueError('Negative shooting count')
    bad_shooting = ((college.FTM > college.FTA) | (college.TPM > college.TPA) | (college.twoPM > college.twoPA))
    if bad_shooting.any():
        raise ValueError('Made shots exceed attempts')
    college.to_csv(out / 'college_seasons.csv', index=False)
    nba = canonical_nba(pd.read_csv(raw / 'nba_advanced.csv'))
    counts = nba.groupby('season').size()
    if any(counts.get(y, 0) < 400 for y in range(2009, config['coverage_end'] + 1)):
        raise ValueError('NBA annual coverage too sparse')
    # A traded player can legitimately exceed 82 due to different team schedules.
    if (nba.g > 90).any() or (nba.gs > nba.g).any() or (nba.mp < 0).any():
        raise ValueError('Impossible NBA totals')
    nba.to_csv(out / 'nba_seasons.csv', index=False)
    keys = nba.groupby('key').nba_id.unique().to_dict()
    first_season = nba.groupby('nba_id').season.min().to_dict()
    nba_group = dict(tuple(nba.groupby('nba_id')))
    full_names = nba.groupby('nba_id').player.first().map(clean).to_dict()
    per_game = pd.read_csv(raw / 'nba_per_game.csv')
    known_nba = set(per_game[per_game.lg.eq('NBA')].player.map(name))
    combine = pd.read_csv(raw / 'combine.csv')
    combine['key'] = combine.PLAYER_NAME.map(name)
    combine['year'] = combine.SEASON.str[:4].astype(int)
    combine = combine.drop_duplicates(['key', 'year'], keep=False)
    combine_lookup = {(r.key, r.year): r for _, r in combine.iterrows()}
    prospects, links, exclusions = [], [], []
    drafts = []
    for year in range(2008, 2022):
        path = raw / f'draft_{year}.json'
        if not path.exists():
            continue
        for pick in json.loads(path.read_text(encoding='utf-8'))['picks']:
            athlete = pick['athlete']
            key = name(athlete['displayName'])
            team = athlete.get('team', {})
            teams = {school(team.get(field, '')) for field in ['location', 'shortDisplayName', 'displayName']}
            candidates = college[(college.key == key) & (college.year <= year) & (college.year >= year - 1)]
            matched = candidates[candidates.school_key.isin(teams)]
            drafts.append({'year': year, 'player': athlete['displayName'], 'key': key,
                           'school_espn': team.get('location', ''), 'pick': pick['overall'],
                           'college_name_candidates': '|'.join(candidates.team.astype(str).unique())})
            if matched.empty:
                exclusions.append({**drafts[-1], 'reason': 'no dated name-and-school college match'})
                continue
            matched = matched[matched.year.eq(matched.year.max())]
            if len(matched) != 1:
                exclusions.append({**drafts[-1], 'reason': 'ambiguous college player'})
                continue
            ids = keys.get(key, [])
            if len(ids) > 1:
                exact = [pid for pid in ids if full_names[pid] == clean(athlete['displayName'])]
                if len(exact) == 1:
                    ids = exact
                else:
                    exclusions.append({**drafts[-1], 'reason': 'ambiguous NBA name; no inferred identity'})
                    continue
            pid = ids[0] if len(ids) else None
            if not pid and key in known_nba:
                exclusions.append({**drafts[-1], 'reason': 'NBA appearance found but no advanced-stat linkage'})
                continue
            if pid and first_season[pid] <= year:
                exclusions.append({**drafts[-1], 'reason': 'NBA identity already active before draft'})
                continue
            seasons = nba_group[pid] if pid else nba.iloc[:0]
            outcomes = window_outcomes(seasons, year, config['horizon'])
            if outcomes is None or year + config['horizon'] > config['coverage_end']:
                exclusions.append({**drafts[-1], 'reason': 'incomplete outcome'})
                continue
            record = matched.iloc[0].to_dict()
            record.update({'draft_year': year, 'pick_reference_only': int(pick['overall']),
                           'player': athlete['displayName'], 'nba_id': pid,
                           'espn_id': athlete.get('alternativeId', athlete['id']),
                           'outcome_link': 'unique NBA name' if pid else 'no NBA record; assumed zero',
                           **outcomes})
            measured = combine_lookup.get((key, year))
            for source, (feature, low, high) in PHYSICAL.items():
                value = pd.to_numeric(measured[source], errors='coerce') if measured is not None else np.nan
                record[feature] = value if pd.notna(value) and low <= value <= high else np.nan
            record['position'] = str(measured.POSITION_anthro) if measured is not None else 'Unknown'
            prospects.append(record)
            links.append({'player': record['player'], 'draft_year': year, 'espn_school': team.get('location'),
                          'college_school': record['team'], 'college_season': int(record['year']),
                          'college_id': int(record['pid']), 'nba_id': pid, 'outcome_link': record['outcome_link']})
    frame = pd.DataFrame(prospects)
    # Early 2008 draft archive is collected separately, giving a viable 2013 inner fold.
    if frame.empty or not frame.draft_year.min() == 2008:
        raise ValueError('2008 draft source required')
    if frame.key.duplicated().any():
        raise ValueError('Same player entered more than one draft')
    frame.to_csv(out / 'prospects.csv', index=False)
    pd.DataFrame(links).to_csv(out / 'identity_links.csv', index=False)
    pd.DataFrame(exclusions).to_csv(out / 'exclusions.csv', index=False)
    pd.DataFrame(drafts).to_csv(out / 'draft_universe.csv', index=False)
    report = {'college_seasons': len(college), 'college_years': college.groupby('year').size().to_dict(),
              'copy_agreement': checks, 'nba_coverage': counts.to_dict(),
              'eligible_prospects': len(frame), 'cohorts': frame.groupby('draft_year').size().to_dict(),
              'outcome_links': frame.outcome_link.value_counts().to_dict(),
              'exclusions': pd.DataFrame(exclusions).reason.value_counts().to_dict(),
              'source_manifest_sha256': sha(raw / 'manifest.json')}
    report['source_quality_policy'] = quality_policy
    (out / 'audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2), flush=True)
    return frame, college
