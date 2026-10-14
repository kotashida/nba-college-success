"""Training-fold pipelines and seeded finite hyperparameter searches."""
import numpy as np
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler, PowerTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge, ElasticNet, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, ExtraTreesRegressor, ExtraTreesClassifier
from sklearn.dummy import DummyRegressor, DummyClassifier
from xgboost import XGBRegressor, XGBClassifier
from lightgbm import LGBMRegressor, LGBMClassifier
from catboost import CatBoostRegressor, CatBoostClassifier

def inverse_asinh(values):
    return np.sinh(np.clip(values, -12, 12))

def candidates(config, task):
    rng = np.random.default_rng(config['seed'])
    specifications = [{'family': 'constant', 'group': 'college', 'transform': 'raw', 'params': {}}]
    for family in config['families']:
        if family == 'constant':
            continue
        for i in range(config['trials_per_family']):
            group = config['feature_groups'][i % len(config['feature_groups'])]
            transform = ['raw', 'asinh', 'yeojohnson'][(i // 3) % 3] if task == 'regression' else 'raw'
            if family == 'linear':
                if task == 'classification':
                    params = {'C': float(10 ** rng.uniform(-3, 1))}
                elif i % 2 == 0:
                    params = {'kind': 'ridge', 'alpha': float(10 ** rng.uniform(0, 4))}
                else:
                    params = {'kind': 'elastic', 'alpha': float(10 ** rng.uniform(-1, 2)),
                              'l1_ratio': float(rng.choice([.1, .5, .9]))}
            elif family in ['random_forest', 'extra_trees']:
                params = {'n_estimators': 200, 'max_depth': rng.choice([3, 5, 8, None]),
                          'min_samples_leaf': int(rng.choice([3, 5, 10, 15])),
                          'max_features': float(rng.choice([.4, .7, 1.]))}
            elif family == 'xgboost':
                params = {'n_estimators': int(rng.choice([100, 200, 350])),
                          'max_depth': int(rng.choice([1, 2, 3])),
                          'learning_rate': float(rng.choice([.02, .05, .1])),
                          'min_child_weight': int(rng.choice([5, 10, 20])),
                          'reg_lambda': float(rng.choice([5, 20, 50])),
                          'subsample': .85, 'colsample_bytree': .8}
            elif family == 'lightgbm':
                params = {'n_estimators': int(rng.choice([100, 200, 350])),
                          'num_leaves': int(rng.choice([3, 7, 15])),
                          'min_child_samples': int(rng.choice([10, 20, 30])),
                          'learning_rate': float(rng.choice([.02, .05, .1])),
                          'reg_lambda': float(rng.choice([5, 20, 50]))}
            else:
                params = {'iterations': int(rng.choice([150, 300])),
                          'depth': int(rng.choice([2, 3, 4])),
                          'learning_rate': float(rng.choice([.02, .05, .1])),
                          'l2_leaf_reg': float(rng.choice([5, 20, 50]))}
            specifications.append({'family': family, 'group': group, 'transform': transform, 'params': params})
    return specifications

def estimator(spec, columns, task, seed=199):
    categorical = [col for col in columns if col in ['conf', 'position']]
    numeric = [col for col in columns if col not in categorical]
    pre = ColumnTransformer([
        ('numeric', Pipeline([('impute', SimpleImputer(strategy='median', add_indicator=True, keep_empty_features=True)),
                              ('scale', StandardScaler())]), numeric),
        ('categorical', Pipeline([('impute', SimpleImputer(strategy='constant', fill_value='Unknown')),
                                  ('encode', OneHotEncoder(handle_unknown='ignore', sparse_output=False))]), categorical)],
        verbose_feature_names_out=False)
    family, params = spec['family'], dict(spec['params'])
    classification = task == 'classification'
    if family == 'constant':
        model = DummyClassifier(strategy='prior') if classification else DummyRegressor(strategy='mean')
    elif family == 'linear':
        if classification:
            model = LogisticRegression(**params, max_iter=10000, random_state=seed)
        elif params.pop('kind') == 'ridge':
            model = Ridge(**params)
        else:
            model = ElasticNet(**params, max_iter=50000, tol=1e-5, random_state=seed)
    elif family == 'random_forest':
        model = (RandomForestClassifier if classification else RandomForestRegressor)(**params, random_state=seed, n_jobs=2)
    elif family == 'extra_trees':
        model = (ExtraTreesClassifier if classification else ExtraTreesRegressor)(**params, random_state=seed, n_jobs=2)
    elif family == 'xgboost':
        model = (XGBClassifier if classification else XGBRegressor)(**params, random_state=seed, n_jobs=2, tree_method='hist', verbosity=0)
    elif family == 'lightgbm':
        model = (LGBMClassifier if classification else LGBMRegressor)(**params, random_state=seed, n_jobs=2, verbosity=-1, deterministic=True, force_col_wise=True)
    else:
        model = (CatBoostClassifier if classification else CatBoostRegressor)(**params, random_seed=seed, thread_count=2, verbose=False, allow_writing_files=False)
    pipeline = Pipeline([('preprocess', pre), ('model', model)])
    if classification or spec['transform'] == 'raw':
        return pipeline
    if spec['transform'] == 'asinh':
        return TransformedTargetRegressor(regressor=pipeline, func=np.arcsinh, inverse_func=inverse_asinh)
    return TransformedTargetRegressor(regressor=pipeline, transformer=PowerTransformer(method='yeo-johnson', standardize=True))

def predict(model, frame, task):
    if task == 'regression':
        result = model.predict(frame)
    else:
        probabilities = model.predict_proba(frame)
        classes = model.classes_
        result = probabilities[:, np.where(classes == 1)[0][0]] if 1 in classes else np.zeros(len(frame))
        result = np.clip(result, 1e-6, 1 - 1e-6)
    if not np.isfinite(result).all():
        raise ValueError('Non-finite prediction; candidate invalid')
    return result
