# Independent computational and reproducibility review

Review date: October 13, 2026. This review concerns the active Python pipeline, its operational scripts, environment, tests, serialized models, publication diagnostics, and replication bundle. Relevant original and earlier reconstruction code was inspected as historical context. It is distinct from the earlier October 10 audit: the numerical checks below were executed anew, and its claims were not adopted merely because a prior report said they passed.

## Assessment

No confirmed defect in the frozen target equations, chronological fitting rule, training-fold median preprocessing, recorded model specifications, or selected-model numerical predictions was found in this computational review. Ten newly fitted selected target/cohort models reproduce the retained final-test predictions to a maximum absolute difference of 1.8189894035458565e-12. This establishes implementation consistency on the recorded environment and snapshots. It does not establish provider truth, historical availability of identical data, public preregistration, or future predictive superiority.

The most consequential defects are in evidence coverage and operational safeguards. The original scientific freeze binds configuration, raw snapshots, two processed datasets, scientific source, and 130 model files; the receipt binds the freeze, final predictions, final scores, and final summaries. Development logs and diagnostic predictions were not bound by either mechanism. Forward model artifacts had no digest checks. Invalid forecast dates could bypass the date guard, and packaging included backup and scratch directories. Narrow operational corrections are implemented below; no frozen scientific fitting, feature, selection, outcome, or evaluation routine was edited by this reviewer.

The root review coordinator verified the original-project backup before authorizing writes. This reviewer performed only read-only calculations until that authorization. The coordinator reports 19,343 readable files verified against their SHA256 values and ten inaccessible legacy OneDrive placeholders separately recorded; this is the coordinator's backup verification, not a second backup check by this reviewer.

## Prioritized findings

### C1. Supplemental experimental evidence was outside the original integrity guard

**Severity: major integrity concern. Status: confirmed coverage defect; no observed corruption.**

`research/experiment.py:118` defines tracked hashes from configuration, processed prospects and college seasons, research source, collectors, and raw files. The freeze written at lines 183–187 separately binds model files. The receipt checks at lines 234–246 bind only `freeze.json`, `test_predictions.csv`, `test_summary.json`, and `test_scores.csv`.

The following files are absent from both original hash maps and from the receipt: `trials.jsonl`, `selection_predictions.csv`, `nested_predictions.csv`, `nested_scores.csv`, and `splits.json`. Derived audit inputs `data/processed/audit.json` and `independent_checks.json` are also unbound. `research/report.py:59` reads several of these inputs to generate publication claims; `audit_research.py:149` uses development artifacts to check selection. Consistent modifications to unbound logs and diagnostic records can therefore escape the original core hash guard. This is a preservation weakness, not evidence that such modifications occurred.

**Action:** retain the original freeze and receipt byte-for-byte and add a dated supplemental evidence manifest anchored to the verified backup. Include original development artifacts, supporting data checks, provenance, audit scripts, current operational code, and forward metadata. The root coordinator owns this addition. Its status must be checked in the final verification report; this reviewer has not claimed that addition already passed.

### C2. Forward models were not bound to their metadata

**Severity: moderate operational defect. Status: confirmed and corrected.**

The original `output/forward_models/metadata.json` listed specifications, fitting origin, population, and training count but contained no artifact digests. Original `predict.py:29` loaded serialized files by target name without testing whether they matched that metadata. A stale or replaced model could silently produce forecasts under another model's provenance. No actual forward model corruption was found: all five saved bundles yielded finite predictions on the canonical frame, and observed binary predictions stayed within [0,1].

**Correction:** `train_final.py:22` now records the digest of every forward model, the original scientific freeze digest, and the input/configuration/feature-source hashes. `predict.py:37` checks all required artifacts before loading any serialized estimator. These checks detect mismatched artifacts against the supplied metadata; they are not cryptographic authentication against someone deliberately rewriting both metadata and files.

The coordinator must regenerate the forward-only refits with the unchanged selected specifications. Old metadata intentionally fails the new guard. This reviewer did not run the actual `train_final.py`; its execution and full-data forward verification belong in the coordinator's final execution log.

### C3. Invalid forecast dates and unidentified rows could bypass the interface contract

**Severity: moderate operational defect. Status: confirmed and corrected.**

Original `predict.py:21` rejected rows only when `prediction_year <= fitting_origin`. Executed checks show that `[NaN, +infinity, 2027.5, 2027, 2026] <= 2026` evaluates to `[False, False, False, False, True]`. Thus missing, infinite, and fractional dates passed the historical-date test. Missing/blank names were accepted, and an empty CSV reached estimator prediction rather than receiving a clear interface error.

**Correction:** `predict.py:23` requires at least one prospect and a nonmissing, nonblank player identifier. Lines 28–36 require finite integer calendar years from 1 to 9999, normalize the integer type, and retain the strict after-fitting-origin rule. Valid inputs use exactly the existing frozen prediction function. This adds no outcome-dependent decision and changes no retained test predictions.

### C4. Packaging traversed backup and scratch directories

**Severity: moderate reproducibility defect. Status: confirmed and corrected.**

Original `package.py:30` omitted `backups` and `tmp` from excluded directories. ZIP files were excluded by suffix, so the existing backup ZIP itself would not be nested. However, backup manifests, extracted original files, and scratch images such as `tmp/pdfs/paper-first.png` were eligible. This could contaminate the active package and significantly enlarge it if backups were extracted.

**Correction:** `package.py:12` extracts reusable active-file discovery and excludes `backups` and `tmp` while retaining raw data, serialized models, manuscript source, and review reports. The new end-to-end packaging test constructs a synthetic complete minimal bundle and checks both retention and exclusions by reading the actual resulting ZIP. No real full package was rebuilt by this reviewer; the coordinator owns final packaging and CRC checks.

### C5. Two scientific tests silently passed without their required data

**Severity: minor reporting defect. Status: confirmed and corrected.**

Original `tests/test_research.py:65` and `:80` returned normally when recorded prospect data was absent. A code-only clone consequently reported those tests as passed without exercising predictor or history checks.

**Correction:** these branches now call `pytest.skip` with the missing-data reason. On the restored complete package the scientific checks still execute. Bare-clone test counts should distinguish skipped checks from executed ones.

### C6. A fresh independent replication could not be packaged without an amendment

**Severity: minor reproducibility defect. Status: confirmed and corrected.**

Original `package.py:22` unconditionally copied `publication_amendment.json`. A freshly generated freeze whose scientific code already matched its own hashes would have no amendment and would fail packaging despite otherwise complete evidence.

**Correction:** current `package.py:46` copies the amendment if present. If an evidence copy exists without a runtime original, it refuses to silently drop that orphaned record. The synthetic end-to-end package test explicitly exercises the no-amendment case.

### C7. The selected-refit verifier does not itself require complete prediction coverage

**Severity: moderate verification weakness. Status: confirmed logic gap; no observed incomplete predictions.**

`research/experiment.py:328` uses an inner merge between recomputed selected predictions and stored rows and then compares only merged values. There is no assertion that both row sets equal the full valid cohort. Missing stored rows can escape this specific check if other integrity evidence is independently regenerated or the verifier is reused for another study. The present historical receipt prevents unrecorded modifications to this project's final CSV, and `audit_research.py:140` separately checks full coverage. Current data have complete selected predictions.

**Action:** the root coordinator's external expanded verification should require the full target/model/year Cartesian set, uniqueness, complete player coverage, and matching truth values. Preserve the frozen experiment source rather than modifying a scientific routine merely to add redundant audit checks. This finding does not invalidate the current numerical result.

### C8. The dependency lock is specific to the recorded Windows environment

**Severity: minor portability limitation. Status: confirmed lock gap for Linux; Linux execution untested.**

All unconditional installed Windows dependencies in the lock are pinned. Evaluation of installed package metadata under Linux markers exposes `xgboost -> nvidia-nccl-cu13; platform_system == "Linux"`, which is not pinned in `requirements-lock.txt`. Therefore a Linux installation can resolve an additional dependency outside the recorded lock. The active interpreter is Python 3.12.4 on Windows. Selected refits pass there.

**Action:** describe the lock as the recorded Windows environment, document Linux/macOS replication as unverified, and pin/test platform-specific dependencies before claiming portable exact installation. Do not invent an untested NCCL version. `pyproject.toml` also supplies no install-time runtime dependencies or CLI entry point, so the documented `pip install -r requirements-lock.txt` workflow remains necessary.

### C9. Archived navigation contains a stale manuscript path

**Severity: minor documentation issue. Status: confirmed; historical file left intact.**

`legacy/README.md:5` points to `../paper/main.tex`, while the active manuscript is `paper/five_year_nba_outcomes.tex`. The root reviewer can add an archival-navigation clarification in current documentation without rewriting original research evidence.

## Executed independent checks

All numerical computations below ran with `.venv/Scripts/python.exe -B`, and `PYTHONDONTWRITEBYTECODE=1`, before implementation. They did not call development, evaluation, report generation, or any writer to retained experiment outputs.

| Check | Observed result | Practical limit |
|---|---|---|
| Current freeze/integrity guard | Passed; 130 model file digests retained | Supplemental evidence gaps described in C1 |
| Runtime versus versioned freeze, receipt, splits, amendment | All four pairs byte-identical | This does not create an independent timestamp authority |
| Fresh selected-model fitting and prediction | Ten target/year refits matched; max absolute difference 1.8189894035458565e-12 | Recorded environment and fixed specifications only |
| Stored bundle schema, tuning parameters, numeric imputation medians, missingness indicator columns | All 130 model/cohort bundles and 162 member estimators matched the expected mature training frame | Does not establish which human design choices preceded exposure |
| Constant model training mean/prevalence | Matched the correct mature classes for every target/year | Snapshot labels themselves still need provider validation |
| SHAP encoded matrix versus recomputed 2019 RF preprocessing | Exact equality; shape 51 by 96 | This is the specified RF diagnostic, not the selected VORP model |
| Saved SHAP additive reconstruction versus RF transformed output | Max error 2.6645352591003757e-15 | Contributions are on the asinh scale |
| Saved mean-absolute SHAP table versus saved contributions | Max difference 9.75781955236954e-17 | Model explanation is not causal inference |
| Existing pre-revision replication ZIP | 291 members, 46,706,332 bytes; `ZipFile.testzip()` returned `None` | Original ZIP predates current manuscript revisions |
| Active Python syntax | Every root and research module parsed successfully with `ast.parse` | Syntax parsing is not end-to-end execution |
| Forecast-date guard counterexample | Invalid dates accepted by old boolean guard as described in C3 | Corrected operationally and tested |
| Forward prediction finiteness | Five saved forward bundles produced finite canonical-frame predictions | This provides no independent forward performance evidence |
| College school-season uniqueness | No duplicated `(pid,year)` rows in the recorded college snapshot | Future multi-school records require explicit handling |

The recorded information-clock folds independently reconstructed as:

| Selection origin | Validation classes | Training counts at respective validation classes | Validation counts |
|---|---|---|---|
| 2018 | 2013 | 44 | 45 |
| 2019 | 2013, 2014 | 44, 89 | 45, 46 |
| 2020 | 2013, 2014, 2015 | 44, 89, 140 | 45, 46, 45 |

Every fitted inner training class satisfies `class + 5 <= validation_year`; every usable validation label satisfies `validation_year + 5 <= selection_origin`. Feature dimensions are 28 college, 59 engineered, and 76 hybrid columns. Primary columns exclude the eventual selection number; the explicitly named draft-order benchmark uses it alone.

The ten refit discrepancies were: VORP 2020 1.7763568394002505e-15 and 2021 4.440892098500626e-16; minutes 2020 9.094947017729282e-13 and 2021 1.8189894035458565e-12; active years both 8.881784197001252e-16; rotation 2020 5.551115123125783e-17 and 2021 1.1102230246251565e-16; starter both 1.6653345369377348e-16.

## Historical code and mathematical interpretation

The original workflow is not comparable evidence for current results. Direct source inspection confirms global Yeo–Johnson transformation in `legacy/src/processing.py:90`, position normalization over the full merged frame at line 130, latest combine attendance retained at line 56, debut-based outcome windows at lines 67–71, and name-only NCAA merges at line 121. `legacy/src/03_analysis.py:41` imputes before random validation splitting at line 87. The original R manuscript draws strong causal/scouting interpretations from SHAP and transformed-target errors. These artifacts remain historical evidence; this review did not run or repair them into another consumed-test experiment.

In the active code, fold-fitted target transformations are correctly applied through `TransformedTargetRegressor`. The ensemble averages inverse-transformed predictions on the original outcome scale. Nevertheless, inverse-transforming an estimate of the transformed conditional mean generally does not estimate the original conditional mean. This is a modeling approximation, not an arithmetic bug; raw-scale validation selected among the frozen alternatives. The asinh inverse clips transformed values to [-12,12]. Both choices must be disclosed, and neither justifies retuning against the consumed final test.

Missing roster BPM contributes zero to the weighted numerator while its exposure remains in the denominator (`research/features.py:58`). Prior history is truncated to earlier college seasons (`:43`). A multi-program school-season count can differ from distinct seasons in future data, but no duplicated player/year records occur in the present snapshot. These are disclosed feature semantics or future-data concerns, not confirmed present leakage.

## Implemented verification and boundaries

Executed focused test command:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -B -m pytest -q tests/test_revision.py -p no:cacheprovider
```

**Observed: 18 passed in 2.53 seconds.** Tests cover invalid dates, historical origins, empty inputs, blank identifiers, missing and altered forward integrity metadata, unchanged valid forecast values, forward provenance generation with synthetic artifacts, and actual ZIP content retention/exclusion without a publication amendment. Fixtures are synthetic and provide no scientific performance evidence.

Owned changes: `predict.py`, `train_final.py`, `package.py`, new `tests/test_revision.py`, and the two missing-data branches plus import in `tests/test_research.py`. The coordinator owns full-suite execution, actual forward refits, expanded evidence sealing, final package creation, manuscript compilation, and the second adversarial review. This report does not preemptively claim those later steps passed.

The repository has no general root code license; the included `data/licenses/mathgonzaga-MIT.txt` expressly limits its notice to the archived reference collection script and grants no blanket third-party statistics rights. A local reproducible ZIP does not itself establish rights-cleared public redistribution. Resolving provider permissions and a persistent public deposit remains a publication limitation, not a reason to discard valid local negative results.
