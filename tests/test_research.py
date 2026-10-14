import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from research.data import height, school, canonical_nba, window_outcomes
from research.features import make_features, BASIC
from research.experiment import folds
from research.models import estimator

def test_corrupted_height_reverses_exactly():
    assert height('6-8') == height('8-Jun') == 80
    assert height('5-11') == height('11-May') == 71
    assert height('6-0') == height('Jun-00') == 72
    assert np.isnan(height('unknown'))

def test_school_confirmation():
    assert school('Iowa St.') == school('Iowa State')
    assert school('UConn') == school('Connecticut')
    assert school('St. Johns') == school('Saint Johns')
    assert school('Michigan') != school('Michigan State')

def test_trades_do_not_duplicate_totals():
    data = pd.DataFrame({'lg': ['NBA'] * 3, 'player_id': ['a'] * 3, 'season': [2020] * 3,
                         'player': ['A'] * 3, 'team': ['2TM', 'AAA', 'BBB'],
                         'vorp': [2., .5, 1.5], 'mp': [1500, 400, 1100],
                         'g': [60, 20, 40], 'gs': [10, 0, 10]})
    result = canonical_nba(data)
    assert len(result) == 1 and result.vorp.iloc[0] == 2.
    assert result.mp.iloc[0] == 1500
    result = canonical_nba(data.iloc[1:])
    assert result.vorp.iloc[0] == 2.

def test_calendar_targets_and_missing_outcome():
    data = pd.DataFrame({'season': range(2010, 2017), 'vorp': [-100, -1, 1, 2, 3, 4, 100],
                         'mp': [1001] * 7, 'g': [60] * 7, 'gs': [41] * 7})
    result = window_outcomes(data, 2010)
    assert result == {'vorp5': 9., 'minutes5': 5005., 'active5': 5, 'rotation5': 1, 'starter5': 1}
    data.loc[data.season == 2012, 'vorp'] = np.nan
    assert window_outcomes(data, 2010) is None
    assert window_outcomes(data.iloc[:0], 2010)['active5'] == 0

def test_every_inner_label_mature_at_selection_origin():
    frame = pd.DataFrame({'draft_year': np.repeat(range(2008, 2022), 40)})
    for origin in [2018, 2019, 2020]:
        for year, train, valid in folds(frame, origin, {'horizon': 5, 'min_training': 35}):
            assert (frame.loc[train, 'draft_year'] + 5 <= year).all()
            assert year + 5 <= origin
            assert (frame.loc[valid, 'draft_year'] == year).all()
    assert [y for y, _, _ in folds(frame, 2020, {'horizon': 5, 'min_training': 35})] == [2013, 2014, 2015]

def test_preprocessing_is_training_only():
    x = pd.DataFrame({'height': [70., 72., np.nan, 74.], 'conf': ['A', 'A', 'B', 'B']})
    spec = {'family': 'linear', 'transform': 'yeojohnson', 'params': {'kind': 'ridge', 'alpha': 10.}}
    model = estimator(spec, list(x), 'regression')
    model.fit(x, [-1, 0, 2, 5])
    medians = model.regressor_.named_steps['preprocess'].named_transformers_['numeric'].named_steps['impute'].statistics_.copy()
    transform = model.transformer_.lambdas_.copy()
    model.predict(pd.DataFrame({'height': [10000., np.nan], 'conf': ['NEW', 'NEW']}))
    np.testing.assert_array_equal(medians, model.regressor_.named_steps['preprocess'].named_transformers_['numeric'].named_steps['impute'].statistics_)
    np.testing.assert_array_equal(transform, model.transformer_.lambdas_)

def test_predictors_exclude_outcomes_and_draft_pick():
    assert not set(BASIC) & {'pick', 'vorp5', 'draft_year', 'nba_id', 'Rec_Rank', 'age'}
    root = Path(__file__).resolve().parents[1]
    if not (root / 'data/processed/prospects.csv').exists():
        pytest.skip('Recorded prospect data is required for this scientific check')
    prospects = pd.read_csv(root / 'data/processed/prospects.csv')
    college = pd.read_csv(root / 'data/processed/college_seasons.csv', low_memory=False)
    frame, groups = make_features(prospects, college)
    for columns in groups.values():
        assert not set(columns) & {'pick', 'pick_reference_only', 'vorp5', 'minutes5', 'active5', 'rotation5', 'starter5', 'draft_year', 'nba_id'}
    shocked = prospects.copy()
    shocked.loc[shocked.draft_year >= 2020, ['vorp5', 'minutes5', 'active5', 'rotation5', 'starter5']] = 99999
    changed, _ = make_features(shocked, college)
    for columns in groups.values():
        pd.testing.assert_frame_equal(frame[columns], changed[columns])

def test_career_features_ignore_future_college_seasons():
    root = Path(__file__).resolve().parents[1]
    if not (root / 'data/processed/prospects.csv').exists():
        pytest.skip('Recorded prospect data is required for this scientific check')
    prospects = pd.read_csv(root / 'data/processed/prospects.csv').query('draft_year <= 2015')
    college = pd.read_csv(root / 'data/processed/college_seasons.csv', low_memory=False)
    a, groups = make_features(prospects, college)
    college.loc[college.year > 2015, ['bpm', 'usg', 'TS_per']] = 999999
    b, _ = make_features(prospects, college)
    pd.testing.assert_frame_equal(a[groups['hybrid']], b[groups['hybrid']])
