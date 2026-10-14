"""Pre-NBA predictors only; deterministic features never consult professional outcomes."""
import numpy as np
import pandas as pd
from .data import PHYSICAL

BASIC = ['height', 'GP', 'mp', 'Min_per', 'Ortg', 'usg', 'eFG', 'TS_per',
         'ORB_per', 'DRB_per', 'AST_per', 'TO_per', 'FT_per', 'twoP_per',
         'TP_per', 'blk_per', 'stl_per', 'ftr', 'bpm', 'obpm', 'dbpm',
         'pts', 'ast', 'stl', 'blk', 'treb', 'class_year']

def safe_div(a, b):
    return a / b.where(b.gt(0))

def make_features(prospects, college):
    frame = prospects.copy()
    frame['class_year'] = frame.yr.map({'Fr': 1, 'So': 2, 'Jr': 3, 'Sr': 4})
    extras = []
    for stat in ['pts', 'ast', 'stl', 'blk', 'oreb', 'dreb']:
        col = stat + '_per40'
        frame[col] = 40 * safe_div(frame[stat], frame.mp)
        extras.append(col)
    exposure = frame.GP * frame.mp
    for stat in ['FTA', 'TPA', 'twoPA']:
        col = stat + '_per40'
        frame[col] = 40 * safe_div(frame[stat], exposure)
        extras.append(col)
    for label, made, attempted, prior, strength in [
        ('three_smoothed', 'TPM', 'TPA', .35, 50),
        ('free_smoothed', 'FTM', 'FTA', .70, 30),
        ('two_smoothed', 'twoPM', 'twoPA', .50, 50)]:
        frame[label] = (frame[made] + prior * strength) / (frame[attempted] + strength)
        extras.append(label)
    frame['three_share'] = safe_div(frame.TPA, frame.TPA + frame.twoPA)
    frame['assist_turnover_rate'] = safe_div(frame.AST_per, frame.TO_per)
    frame['stocks_per40'] = frame.stl_per40 + frame.blk_per40
    frame['creation_efficiency'] = frame.usg * (frame.Ortg - 100) / 100
    frame['exposure_log'] = np.log1p(exposure)
    extras += ['three_share', 'assist_turnover_rate', 'stocks_per40', 'creation_efficiency', 'exposure_log']
    grouped = dict(tuple(college.groupby('pid')))
    history = []
    for _, row in frame.iterrows():
        previous = grouped[row.pid]
        previous = previous[previous.year.lt(row.year)]
        record = {'prior_seasons': len(previous)}
        for stat in ['bpm', 'usg', 'TS_per', 'AST_per', 'stl_per', 'blk_per']:
            weights = previous.GP * previous.mp
            mask = previous[stat].notna() & weights.gt(0)
            career = np.average(previous.loc[mask, stat], weights=weights[mask]) if mask.any() else np.nan
            record['prior_' + stat] = career
            record['change_' + stat] = row[stat] - career
        history.append(record)
    history = pd.DataFrame(history, index=frame.index)
    frame = pd.concat([frame, history], axis=1)
    extras += list(history.columns)
    # Entire college roster statistics were observable before the draft; exclude the player.
    roster = college.copy()
    roster['exposure'] = roster.GP * roster.mp
    roster['weighted_bpm'] = roster.bpm.fillna(0) * roster.exposure
    context = roster.groupby(['school_key', 'year'])[['weighted_bpm', 'exposure']].sum()
    lookup = frame.set_index(['school_key', 'year']).index
    totals = context.reindex(lookup).reset_index(drop=True)
    frame['teammate_bpm'] = safe_div(totals.weighted_bpm.set_axis(frame.index) - frame.bpm * exposure,
                                      totals.exposure.set_axis(frame.index) - exposure)
    extras.append('teammate_bpm')
    physical = [info[0] for info in PHYSICAL.values()]
    frame['wingspan_surplus'] = frame.wingspan - frame.combine_height
    frame['bmi'] = 703 * frame.weight / frame.combine_height.pow(2)
    frame['jump_gain'] = frame.max_vertical - frame.standing_vertical
    frame['max_touch'] = frame.reach + frame.max_vertical
    groups = {'college': BASIC + ['conf'],
              'engineered': BASIC + extras + ['conf'],
              'hybrid': BASIC + extras + physical + ['wingspan_surplus', 'bmi', 'jump_gain', 'max_touch', 'conf', 'position']}
    for columns in groups.values():
        numeric = [x for x in columns if x not in ['conf', 'position']]
        frame[numeric] = frame[numeric].replace([np.inf, -np.inf], np.nan)
    return frame, groups
