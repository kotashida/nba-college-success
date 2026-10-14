# Independent statistical and methodological review

Review date: October 13, 2026. This is an independent review of the active implementation, source snapshots, frozen experiment artifacts, manuscript, and relevant historical code. Findings refer to the versions inspected at the beginning of this audit; source line numbers can shift during revision. Earlier `docs/AUDIT.md` conclusions were not treated as proof. No scientific input, target, feature, model, frozen specification, prediction, score, or consumed receipt was edited by this reviewer. The supplemental identity investigation is post hoc review evidence.

## Scientific assessment

The project supports a limited retrospective benchmark of realized five-year NBA value and participation within an ascertained subset of recent NCAA draftees. It does not support a reliable improvement over constant predictions, a prospective historical deployment claim, an exhaustive NCAA draftee registry, or a causal measure of talent. The active fitting and tuning implementation does enforce elapsed-season maturity and excludes final-test cohorts from learning. That computational condition must be distinguished from availability of the provider's metric definition and exact snapshot at the simulated date.

The final-test conclusions are appropriately unfavorable or inconclusive. The VORP selected-model squared error is slightly worse than the constant; starter probability error also worsens. Minutes, years active, and rotation have modest favorable point estimates. All five recorded paired loss intervals span zero. This is uncertainty about comparative performance, not a demonstration of equality, noninferiority, or absence of useful signal. A publication may present these negative results, provided it accurately states the retrospective source clock and ascertainment limitations. Public rights-cleared replication access and venue-specific author statements remain outside what these local computations establish.

## Major findings and essential corrections

| ID | Severity and status | Evidence | Required handling |
|---|---|---|---|
| M01 | High; confirmed mismatch between strong historical-information claims and available provenance | `research/experiment.py:28-38,106-110` enforces season arithmetic. `paper/five_year_nba_outcomes.tex:57,95,138-142` and `docs/PROTOCOL.md` describe availability more strongly than source metadata demonstrates. Original Basketball Reference BPM was released in 2014; BPM 2.0 was introduced February 25, 2020. The cached VORP version is not explicitly identified. | Explain two clocks: completed sport follow-up versus provider definition/release and exact snapshot availability. Describe a retrospective evaluation with season-maturity restrictions; avoid asserting that all metrics were literally available at every inner forecast date. Preserve the current results. |
| M02 | High; confirmed incomplete name ascertainment within the intended recent-NCAA population | `research/data.py:47-57,184-197` preserves spaces between initials and uses a finite alias map; `data/processed/exclusions.csv` contains 173 no-match exclusions. Twelve have unique dated same-school college records under variant names, tabulated in `LINKAGE_CANDIDATES.csv`. | Quantify these known misses and the resulting sample restriction. Retain the frozen 663-player analysis. Do not add the twelve to fitting or recompute an alternative winner after seeing the test. A future matching protocol requires independently reserved evaluation. |
| M03 | Medium; unsupported strength of temporal prespecification language | `docs/PROTOCOL.md:19` calls service definitions prespecified; manuscript line 88 says declared before fitting. Local freeze timestamp is 2026-10-09T21:33:17.877556+00:00; scoring receipt timestamp is 21:33:49.435672+00:00. The active protocol/code first appear in Git on October 10, after recorded scoring. | Call these fixed operational definitions in the recorded frozen implementation. The local records support preservation and the recorded order of freezing/scoring, not independent proof of prefit decisions, a never-seen outcome set, or public preregistration. Do not infer misconduct from unavailable independent timestamps. |
| M04 | Medium; confirmed left truncation of engineered histories | `research/features.py:39-51` counts only earlier observed archive rows; archive begins in 2008. All 44 retained 2008 prospects have zero observed earlier rows, including 33 nonfreshmen. | State that `prior_seasons=0` means no earlier observed record, not no earlier college experience. Explain that the first 2013 inner training pool has no variation in prior-record counts and missing prior summaries; early folds cannot fully learn trajectory effects. No retrospective imputation of unobserved history. |
| M05 | Medium; source absence assumptions remain unresolved | `research/data.py:174-176,205-222`, `data/processed/identity_links.csv`; 41 assumed nonparticipants and four ambiguous/conflicting identities. Annual row counts are a completeness proxy, not an exhaustive registry audit. | Retain the explicit zero assumption and identity exclusions. Do not relabel source consistency as independent absence verification. Broader independent ID-level verification is still necessary; new verified data errors must be documented as corrections, with the original evidence retained. |
| M06 | Medium; strong generalization claims would exceed this design | Only three final selection validation cohorts, small inner fitting samples, two nested diagnostic cohorts, and two final-test cohorts. Inner winners are selected among 73 base candidates plus an ensemble. `research/experiment.py:63-104,249-264`. | Retain selected development performance as selected performance, not unbiased efficacy. Retain conditional bootstrap caveats and lack of significance claims. Never promote a supplementary final-test winner. |

### M01: season maturity does not certify provider availability

The season inequalities are correct: a class `c` can fit at origin `t` only when `c + 5 <= t`; an inner class `v` is scored using training labels satisfying `c + 5 <= v` and may contribute to selection only if `v + 5 <= t`. They ensure that no future sporting season enters an earlier fitting window. They do not prove that the corresponding provider-derived number, or its present metric definition, existed at that date.

The provider's [BPM methodology page](https://www.basketball-reference.com/about/bpm2.html) identifies the original release as 2014. Its [BPM 2.0 announcement](https://www.sports-reference.com/blog/2020/02/introducing-bpm-2-0/) is dated February 25, 2020 and describes changes to historical VORP values. The [2014 announcement archive](https://www.sports-reference.com/blog/2014/10/) provides additional original-provider chronology. Provider-indexed primary content was retrieved during this review; direct opening of some provider pages returned HTTP 403. No access-control bypass was attempted.

Consequently, an exact 2013 replay cannot be established merely by five-year season completeness. The metric version in `nba_advanced.csv` was not independently proved, and Torvik's specific college BPM, offensive/defensive components, and advanced fields also lack a verified first-publication and version history in this package. It would be incorrect to assert either that all cached values definitely use BPM 2.0 or that every college field was unavailable historically. The defensible statement is narrower: the supplied retrospective values are evaluated under a sport-follow-up restriction, with provider-release availability unresolved. Basic games, starts, and minutes are much closer to contemporaneously observable counts, but their exact cached snapshots can still contain retrospective corrections.

### M02: twelve independently reviewed name misses

| Draft | ESPN draft name | College archive name | College ID | Latest eligible season | School |
|---|---|---|---:|---:|---|
| 2008 | J. J. Hickson | JJ Hickson | 49713 | 2008 | North Carolina State |
| 2008 | J. R. Giddens | J.R. Giddens | 2973 | 2008 | New Mexico |
| 2008 | Luc Richard Mbah a Moute | Luc Mbah a Moute | 49823 | 2008 | UCLA |
| 2009 | B.J. Mullens | Byron Mullens | 50000 | 2009 | Ohio State |
| 2009 | Jeff Pendergraph | Jeff Ayres | 49752 | 2009 | Arizona State |
| 2010 | Wesley Johnson | Wes Johnson | 49721 | 2010 | Syracuse |
| 2010 | Keith Gallon | Tiny Gallon | 11036 | 2010 | Oklahoma |
| 2011 | Trey Thompkins | Howard Thompkins III | 13410 | 2011 | Georgia |
| 2012 | Maurice Harkless | Moe Harkless | 21044 | 2012 | St. John's |
| 2016 | Kay Felder | Kahlil Felder | 33408 | 2016 | Oakland |
| 2018 | Vince Edwards | Vincent Edwards | 47002 | 2018 | Purdue |
| 2019 | Dewan Hernandez | Dewan Huell | 46264 | 2018 | Miami |

All twelve have an eligible latest record with a unique candidate and the same canonical school. Eleven also have an embedded eventual draft pick agreeing with ESPN; Thompkins's embedded pick is missing. That pick agreement is review corroboration only, not an admissible pre-selection predictor or a rule applied to change the cohort. No candidate is from the final-test 2020 or 2021 classes. Adding historical candidates would nevertheless change development and fitting, so it is not innocuous to silently update the matching code after evaluation.

Independent primary evidence supports the nontrivial aliases: [Thunder's Mullens report](https://www.nba.com/thunder/news/orlandosummerleague_090706.html), [Pacers media guide](https://cdn.nba.com/teams/uploads/sites/1610612754/2025/10/2025-26-Indiana-Pacers-Media-Guide-web.pdf), [Oklahoma's Gallon announcement](https://soonersports.com/news/2010/4/20/208373989), [Georgia's Thompkins profile](https://georgiadogs.com/news/2009/1/2/Rinnai_Who_s_Hot_Student_Athlete_of_the_Week), [St. John's Harkless biography](https://redstormsports.com/sports/mens-basketball/roster/moe-harkless/466), [Oakland's Felder biography](https://goldengrizzlies.com/sports/mens-basketball/roster/kay-felder/609), [Purdue's Edwards profile](https://purduesports.com/news/2017/10/26/getting-to-know-vincent-edwards), and [Miami's Hernandez announcement](https://miamihurricanes.com/news/2018/10/19/mens-basketball-hernandez-named-to-abdul-jabbar-award-watch-list). The CSV records row-specific primary URLs and local identifiers. This is a verified convenience investigation of the exclusion list, not a guarantee that all remaining exclusions are correct.

### M04: early histories are structurally absent

The initial chronological fits have 44, 89, and 140 players. In 2008 every player has `prior_seasons=0`; the maximum observed history is one prior row for class 2009 and two for class 2010. This structural truncation can make later history features behave differently from the initial fitting distribution. Training-only imputation correctly avoids outcome leakage, but cannot recover history that the source panel omits. Extending the source archive backward would be a future study design improvement, not a post-test patch here.

## Minor confirmed findings

| ID | Finding | Evidence and correction |
|---|---|---|
| M07 | Manuscript date cannot describe this computation honestly as an original 2025 analysis | Initial inspected `paper/five_year_nba_outcomes.tex:23` states March 20, 2025 while line 57 uses 2025–2026 outcomes and bibliography contains 2026 work. Preserve the supplied version and identify the current revision date explicitly. Latest Git date-edit commit had March 20, 2026, so the initial working copy also differed from committed source. |
| M08 | Years-active regression is continuous and unconstrained | Selected 2018 nested forecast for Wendell Carter Jr. is 5.217220702844531 despite a label maximum of five. Selected final-test forecasts all lie within bounds. Disclose the limitation; do not clip the consumed evaluation or replace its specification. A bounded/count model is proposed future work only. |
| M09 | Historical archive guidance has an obsolete manuscript path | `legacy/README.md:5` points to `../paper/main.tex`; active source is `../paper/five_year_nba_outcomes.tex`. Correct the link without modifying historical scientific artifacts. |
| M10 | Feature-group comparisons are not controlled causal or incremental-information ablations | `research/experiment.py:100-101,157-159` separately optimizes family/specification within feature group, and the ensemble can mix groups. Current manuscript discussion already mostly acknowledges this. Preserve that distinction. The constant candidate occurs only in the college group, although no observed ablation winner is constant, so the realized comparisons are unaffected by that search asymmetry. |

## Independent numerical and data checks actually executed

The reproducible supplement is `verify_methods.py`, run using the existing `.venv/Scripts/python.exe -B`. It writes only the review's CSV and JSON. `METHODS_CHECKS.json` records the actual checks and limitations.

- Independently recomputed pooled squared error, and regression RMSE, MAE, and R-squared, directly from selected and constant test prediction rows for all five targets. All ten score groups agree with recorded score tables within the script's explicit tolerances. This computation does not reuse `research.experiment.metrics`.
- Confirmed 663 retained prospects, 98 final-test prospects, twelve reviewed name misses, eleven embedded-pick agreements, one unavailable embedded pick, and no candidate from the final-test classes.
- Independently counted mature fitting samples: origins 2013/2014/2015 use 44/89/140 players; 2018/2019 use 281/327; 2020/2021 use 372/415.
- Checked zero duplicate college `pid,year` rows. The full panel has 383 IDs with multiple normalized names; among retained prospects only four IDs have variants, corresponding to Robbie John/Robbie Hummel, Raymond/Ray Spalding, Temetrius/Ja Morant, and Kezie/KZ Okpala. These examples are consistent with aliases, not evidence of a confirmed ID collision. This does not prove every identifier in the full source panel is correct.
- Counted prior-history availability by all fourteen cohorts. Verified 33 nonfreshmen in the earliest fitting class have zero prior observed records.
- Inspected selected test and nested prediction ranges; recorded one out-of-range selected nested years-active forecast and none in selected final-test forecasts.
- Checked all 41 assumed-zero normalized names against the raw NBA per-game appearance source: none appears. The advanced and per-game archives share provenance, so this is source consistency, not independent verification of absence.
- Read actual maturity conditions, preprocessing estimators, transformation inversion, final selection, saved freeze/receipt order, and relevant legacy source. No final-test row or later cohort label enters active fitting/tuning conditions.

| Target | Selected error | Constant error | Meaning |
|---|---:|---:|---|
| VORP | RMSE 3.663681 | RMSE 3.654867 | Slightly worse selected squared-error objective |
| Minutes | RMSE 3443.516659 | RMSE 3531.493571 | Modest favorable point estimate |
| Years active | RMSE 1.458617 | RMSE 1.509404 | Modest favorable point estimate |
| Rotation | Brier 0.227489 | Brier 0.239817 | Modest favorable point estimate |
| Starter | Brier 0.175842 | Brier 0.172313 | Worse selected probability error |

The lower VORP MAE (2.174211 versus 2.604133), positive selected rank correlation, and service AUCs answer different questions from the selected squared-error objectives. They do not reverse the negative primary comparison. Year-specific constants can differ after refitting, so pooled constant AUC or Spearman correlation need not equal a single-value no-discrimination reference.

This reviewer did not rerun all model training, every raw outcome reconstruction, all bootstrap replicates, or the PDF build. Those tasks belong to the coordinated reproducibility and publication checks, whose executed results must be recorded separately. Prior reports of successful checks are not counted as executions by this reviewer.

## Statistical design and interpretation that remain defensible

The formulas in the manuscript match active outcome aggregation: draft-anchored five season-ending years, cumulative VORP/minutes, positive-game season count, three 1000-minute seasons for rotation, and two 41-start seasons for starter. Total-row precedence prevents summing a traded player's total and stints twice. A present missing required statistic invalidates the complete outcome; absence of a player-season is explicitly treated as zero. Targets remain distinct realized value/opportunity/service outcomes.

Fold-fitted imputation, scaling, one-hot encoding, and fitted Yeo–Johnson transforms are appropriate. Fixed shooting shrinkage is deterministic and preserves unavailable inputs as missing. The nonlinear target-inversion caveat is already stated; raw-scale validation is necessary and implemented. Combine records are restricted to the actual draft year, and primary feature groups exclude embedded picks, recruiting ranks, professional identity fields, and professional outcomes. Prior histories use earlier college years; team context uses the contemporaneous amateur roster. Missing roster BPM as zero in its weighted numerator remains a disclosed approximation.

All-family and feature-group test tables are diagnostics of frozen choices. They do not justify choosing a different winner. Nested outcomes of the 2018/2019 cohorts cannot select the final 2020 procedure because their five-year windows finish later. The code does not use those outer scores for final selection. Those cohorts were already consumed by the earlier reconstruction, so their retrospective reuse cannot provide independent confirmation of design decisions.

The two-stage paired bootstrap evaluates loss for fixed predictions conditional on resampled classes and players. Pairing is preserved by identical `(year,player)` ordering. It omits model refitting, adaptive specification/design choice, common shocks beyond the observed classes, and simultaneous target-comparison uncertainty. With two independent class units, its numerical percentile calculation is reproducible while broad future-era confidence is unsupported. The existing caveat is essential and should remain prominent.

## Historical evidence and integrity

The original R Markdown actually filters `Draft_Year < 2020` at lines 64–67, globally imputes at lines 75–105, then uses random XGBoost cross-validation at line 332 and approximates R-squared from selected CV RMSE and full-target variance at line 346. `legacy/src/processing.py:64-95` anchors on inferred debut, sums rows without NBA total-row precedence, and fits a target transformation before cross-validation. These are genuine original-method problems, not evidence that active models share the same errors. The old claimed 14.7% normalized-target variance explanation is not comparable to the current original-scale held-out R-squared.

The earlier `legacy/archive_research` population is first recorded combine attendance, including undrafted invitees; its final test was 2018–2019 and its receipt records scoring October 9, 2026. Its negative primary result and provenance-unverified college sensitivity were read as historical evidence, not promoted as validation of the active 663-player draft-anchored study. Preserve the archive, receipt, and original negative/inconclusive results. The active 2020–2021 receipt is consumed and remains binding.

The project backup was verified by the coordinating reviewer before this supplemental report was written. Ten inaccessible cloud-only legacy files were documented by that coordinator. This reviewer did not independently hydrate, inspect, or claim reproduction of those unavailable files.

## Prioritized disposition

1. Correct M01 historical-source availability framing and M02 sample ascertainment disclosure before any publication-readiness claim. Keep the original scientific experiment intact.
2. Replace unsupported prespecification language (M03), identify the revision date (M07), and disclose history truncation and unconstrained years-active regression (M04/M08).
3. Finish numerical replay, source integrity, tests, and PDF compilation/rendering through the coordinated verification workflow. Do not claim checks that did not execute.
4. Resolve the archival/public replication and broader provider/identity verification limitations before claiming a complete journal-submission package.
5. Reserve genuinely new mature cohorts for any new matching policy, broader source collection, bounded model, schedule-adjusted service definition, calibration method, or algorithm selection. Under this five-season horizon, the 2022 class finishes follow-up in the season ending 2027; that future reserve is not supplied by the already-consumed 2020–2021 evidence.

Final independent methods judgment: publication may be defensible as a transparently retrospective, narrowly scoped benchmark with uncertain or negative gains. Strong historical point-in-time forecasting, general predictive superiority, complete population ascertainment, causal talent, or scouting-decision claims remain unsupported. The required corrections primarily concern provenance and interpretation; the present review supplies no basis for test-driven scientific refitting.
