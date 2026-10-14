"""Reproduce this review's checks without changing scientific inputs or outputs."""
from pathlib import Path
import csv
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DEST = Path(__file__).resolve().parent

# This is post-evaluation review evidence, not a replacement matching policy.
PAIRS = [
    ('J. J.  Hickson', 'JJ Hickson', 'https://www.nba.com/player/201581/jj-hickson'),
    ('J. R. Giddens', 'J.R. Giddens', 'https://www.nba.com/player/201592/jr-giddens'),
    ('Luc Richard Mbah a Moute', 'Luc Mbah a Moute', 'https://uclabruins.com/documents/download/2018/10/15/MBKB_19MG_142_150.pdf'),
    ('B.J. Mullens', 'Byron Mullens', 'https://www.nba.com/thunder/news/orlandosummerleague_090706.html'),
    ('Jeff Pendergraph', 'Jeff Ayres', 'https://cdn.nba.com/teams/uploads/sites/1610612754/2025/10/2025-26-Indiana-Pacers-Media-Guide-web.pdf'),
    ('Wesley Johnson', 'Wes Johnson', 'https://www.nba.com/timberwolves/news/dc2010_wesley_johnson.html'),
    ('Keith Gallon', 'Tiny Gallon', 'https://soonersports.com/news/2010/4/20/208373989'),
    ('Trey Thompkins', 'Howard Thompkins III', 'https://georgiadogs.com/news/2009/1/2/Rinnai_Who_s_Hot_Student_Athlete_of_the_Week'),
    ('Maurice Harkless', 'Moe Harkless', 'https://redstormsports.com/sports/mens-basketball/roster/moe-harkless/466'),
    ('Kay Felder', 'Kahlil Felder', 'https://goldengrizzlies.com/sports/mens-basketball/roster/kay-felder/609'),
    ('Vince Edwards', 'Vincent Edwards', 'https://purduesports.com/news/2017/10/26/getting-to-know-vincent-edwards'),
    ('Dewan Hernandez', 'Dewan Huell', 'https://miamihurricanes.com/news/2018/10/19/mens-basketball-hernandez-named-to-abdul-jabbar-award-watch-list'),
]


def main():
    from research.data import name, school

    college = pd.read_csv(ROOT / 'data/processed/college_seasons.csv', low_memory=False)
    prospects = pd.read_csv(ROOT / 'data/processed/prospects.csv')
    exclusions = pd.read_csv(ROOT / 'data/processed/exclusions.csv')
    nba = pd.read_csv(ROOT / 'data/processed/nba_seasons.csv')
    per_game = pd.read_csv(ROOT / 'data/raw/nba_per_game.csv')
    records = []
    for draft_name, college_name, url in PAIRS:
        excluded = exclusions.loc[exclusions.player.eq(draft_name)]
        assert len(excluded) == 1
        d = excluded.iloc[0]
        variants = college.loc[college.player_name.eq(college_name)
                               & college.year.between(d.year - 1, d.year)
                               & college.school_key.eq(school(d.school_espn))]
        latest = variants.loc[variants.year.eq(variants.year.max())]
        assert len(latest) == 1 and d.reason == 'no dated name-and-school college match'
        c = latest.iloc[0]
        picks = json.loads((ROOT / f'data/raw/draft_{int(d.year)}.json').read_text(encoding='utf-8'))['picks']
        draft = [p for p in picks if p['athlete']['displayName'] == draft_name]
        assert len(draft) == 1
        athlete = draft[0]['athlete']
        professional = nba.loc[nba.key.isin([name(draft_name), name(college_name)])]
        agrees = pd.notna(c.pick) and float(c.pick) == float(d.pick)
        assert pd.isna(c.pick) or agrees
        records.append({
            'draft_year': int(d.year), 'espn_player': draft_name,
            'espn_athlete_id': str(athlete['id']),
            'espn_alternative_id': str(athlete.get('alternativeId', '')),
            'college_name_variant': college_name, 'college_pid': int(c.pid),
            'college_year': int(c.year), 'espn_school': d.school_espn,
            'college_school': c.team, 'canonical_school': c.school_key,
            'original_key': d.key, 'variant_key': c.key,
            'original_pick': int(d.pick),
            'source_embedded_pick': '' if pd.isna(c.pick) else int(c.pick),
            'source_pick_agrees': bool(agrees),
            'eligible_variant_records': int(len(variants)),
            'latest_candidate_count': int(len(latest)),
            'source_origin': c.origin,
            'nba_id_candidates_reference_only': '|'.join(sorted(professional.nba_id.unique())),
            'evidence': 'Unique latest same-school eligible-year college record; independent primary identity corroboration; embedded pick is corroboration only',
            'status': 'post hoc ascertainment finding; excluded in unchanged frozen study; no model or outcome correction applied',
            'primary_url': url, 'verification_date': '2026-10-13',
        })
    with (DEST / 'LINKAGE_CANDIDATES.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

    joined = college[['pid', 'year']].merge(
        prospects[['pid', 'year', 'draft_year', 'player', 'yr']], on='pid',
        suffixes=('_history', '_prospect'))
    earlier = joined.loc[joined.year_history.lt(joined.year_prospect)]
    counts = earlier.groupby('player').size()
    prospects['observed_prior'] = prospects.player.map(counts).fillna(0).astype(int)
    by_year = prospects.groupby('draft_year').agg(
        n=('player', 'size'), no_prior=('observed_prior', lambda s: int(s.eq(0).sum())),
        max_prior=('observed_prior', 'max'))
    test = pd.read_csv(ROOT / 'output/experiments/test_predictions.csv')
    score_table = pd.read_csv(ROOT / 'output/experiments/test_scores.csv')
    manual_scores = []
    for (target, model), rows in test.loc[test.model.isin(['selected', 'constant'])].groupby(['target', 'model']):
        actual = score_table.loc[score_table.target.eq(target) & score_table.model.eq(model) & score_table.year.eq('pooled')]
        assert len(actual) == 1 and int(actual.iloc[0]['n']) == len(rows)
        error = rows.truth.to_numpy() - rows.prediction.to_numpy()
        mse = float(np.mean(error ** 2))
        assert np.isclose(mse, actual.iloc[0].loss, atol=1e-8, rtol=1e-12)
        calculated = {'target': target, 'model': model, 'n': len(rows), 'mse_or_brier': mse}
        if target in ['vorp5', 'minutes5', 'active5']:
            calculated.update(rmse=float(np.sqrt(mse)), mae=float(np.mean(np.abs(error))),
                              r2=float(1 - np.sum(error ** 2) / np.sum((rows.truth - rows.truth.mean()) ** 2)))
            for metric in ['rmse', 'mae', 'r2']:
                assert np.isclose(calculated[metric], actual.iloc[0][metric], atol=1e-8, rtol=1e-12)
        manual_scores.append(calculated)
    nested = pd.read_csv(ROOT / 'output/experiments/nested_predictions.csv')
    active_outside = nested.loc[nested.model.eq('selected') & nested.target.eq('active5')
                                & ~nested.prediction.between(0, 5)]
    oldnames = set(per_game.loc[per_game.lg.eq('NBA'), 'player'].map(name))
    assumed = set(prospects.loc[prospects.nba_id.isna(), 'key'])
    result = {
        'audit_date': '2026-10-13',
        'scope': 'Independent methods checks; no refitting, tuning, scoring substitutions or scientific mutations',
        'n_original': len(prospects), 'n_test': int(prospects.draft_year.isin([2020, 2021]).sum()),
        'independently_recalculated_selected_and_constant_pooled_scores': manual_scores,
        'ascertainment_candidates': len(records),
        'candidate_latest_unique': all(r['latest_candidate_count'] == 1 for r in records),
        'candidate_embedded_pick_agreements': sum(r['source_pick_agrees'] for r in records),
        'candidate_embedded_pick_missing': sum(r['source_embedded_pick'] == '' for r in records),
        'candidate_test_cohorts': sorted(set(r['draft_year'] for r in records) & {2020, 2021}),
        'college_duplicate_pid_year_rows': int(college.duplicated(['pid', 'year']).sum()),
        'source_pids_with_multiple_normalized_names': int(college.groupby('pid').key.nunique().gt(1).sum()),
        'prospect_pids_with_multiple_normalized_names': int(college.loc[college.pid.isin(prospects.pid)].groupby('pid').key.nunique().gt(1).sum()),
        '2008_nonfreshmen_with_no_earlier_observed_records': int((prospects.draft_year.eq(2008) & prospects.yr.ne('Fr') & prospects.observed_prior.eq(0)).sum()),
        'observed_history_by_cohort': {int(y): {k: int(v) for k, v in row.items()} for y, row in by_year.to_dict(orient='index').items()},
        'mature_training_counts': {y: int((prospects.draft_year + 5 <= y).sum()) for y in [2013, 2014, 2015, 2018, 2019, 2020, 2021]},
        'selected_test_prediction_ranges': test.loc[test.model.eq('selected')].groupby('target').prediction.agg(['min', 'max']).to_dict(orient='index'),
        'selected_nested_active_predictions_outside_0_5': active_outside.to_dict(orient='records'),
        'assumed_nonparticipant_names_found_in_raw_nba_per_game_source': sorted(assumed & oldnames),
        'limitations': ['The per-game absence check is same-origin consistency, not independent league-complete verification.',
                        'Primary URLs verify identities; they do not certify historical point-in-time snapshot availability.',
                        '12 candidates are manually reviewed ascertainment evidence, not an exhaustive automated identity audit.',
                        'Embedded eventual picks support review corroboration only and remain forbidden primary features.'],
    }
    (DEST / 'METHODS_CHECKS.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['n_original', 'n_test', 'ascertainment_candidates', 'candidate_embedded_pick_agreements', 'candidate_test_cohorts', 'college_duplicate_pid_year_rows', '2008_nonfreshmen_with_no_earlier_observed_records', 'selected_nested_active_predictions_outside_0_5']}, indent=2))


if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(ROOT))
    main()
