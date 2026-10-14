# Research Protocol

Prediction time is the actual draft year's pre-selection evaluation date, after the relevant college season. The population is NCAA players eventually selected in the NBA draft with a dated, school-confirmed amateur record. This conditional-on-selection population is NOT all college players and cannot establish the NBA entry probability of an arbitrary NCAA player. There is no minimum NBA appearance, career-duration, awards or professional-performance threshold. Unresolved or conflicting professional identities are excluded, so the sample also conditions on acceptable source linkage; it is not independent of professional record availability in every case.

## Information clock

For year `t`, train only on draft classes `c` satisfying `c + 5 <= t`. A validation class `v` can be used in model selection at `t` only if `v + 5 <= t`; its own training classes satisfy `c + 5 <= v`. This enforces completion of five-season follow-up, not historical publication of every metric or availability of identical database releases. Basketball Reference introduced BPM in 2014 and BPM2 in February 2020; the cached VORP vintage is unverified. Interpret this as retrospective chronological reconstruction. Pre-draft features use college seasons ending no later than the draft year, with only earlier seasons for career trajectories and contemporaneous roster data for team context. Actual draft selection number is benchmark-only.

## Outcomes

All labels concern the five calendar NBA regular seasons ending in `draft_year + 1` through `draft_year + 5`, not five seasons actually played, not a variable-length current career, and not the best seasons selected in hindsight.

- `vorp5`: cumulative VORP, including negative values.
- `minutes5`: cumulative NBA minutes.
- `active5`: number of seasons with at least one NBA game, from zero through five.
- `rotation5`: at least three seasons with 1,000 NBA minutes each.
- `starter5`: at least two seasons with 41 NBA starts each.

The last two are fixed operational definitions in the recorded frozen implementation, not universal basketball labels or externally preregistered definitions. The local evidence establishes that they were in the preserved implementation before the recorded scoring run; it does not independently certify their timing before all fitting or historical exposure. Absolute exposure thresholds are sensitive to shortened seasons and opportunity. Unmatched drafted players absent from NBA sources receive an explicitly assumed zero; known ambiguous identities are excluded.

## Development and selection

Seed 199. Seven families include a training-mean/prevalence constant, regularized linear methods, Random Forest, Extra Trees, XGBoost, LightGBM and CatBoost. For each nonconstant family, 12 seeded configurations span three feature sets, regularization and tree complexity. Regression tries raw, fixed asinh, and fold-fitted Yeo-Johnson targets. A three-family equal-weight ensemble uses the best nonconstant families within each inner selection procedure; weights are not fitted on test data. Median imputation, scaling, missingness indicators and categorical encodings are fit entirely within training folds. No full-data feature selection or target transform is allowed. Convergence failures and non-finite inverse predictions disqualify candidates and remain in trial logs.

Tune on pooled original-scale MSE for regression and Brier score for binary targets. A proper squared probability error avoids threshold optimization on a tiny sample; also report log loss, ROC AUC and average precision. Retain all outcomes rather than cherry-picking the most attractive final test. Rank their development-stage predictability with baseline-relative squared-error skill, with no implication that their utility or uncertainty is identical.

Nested outer origins are 2018 and 2019. Inner labels must already be mature at each origin, giving validation years 2013 and 2013-2014 respectively. These nested outer outcomes are **not available to select final models in 2020**. They diagnose the selection procedure only. Final family/specification selection at 2020 uses mature 2013-2015 validation classes; all fitting follows each fold's maturity clock. This is intentionally different from selecting families using the later nested scores. Final 2020 models fit through class 2015; frozen specifications refit for 2021 using class 2016. Neither test class enters training or model selection.

## Final evaluation lock

Before any final-test score, hash configuration, code, input snapshots, processed datasets, and models. Write a freeze with all family and ablation specifications selected on development data. The final test is the 2020-2021 draft classes. Evaluation is write-once and creates a receipt binding the freeze, predictions, scores and summaries. Reruns retain that receipt. Once consumed, no algorithm, feature or target changes may be justified by its scores; reserve new future cohorts for subsequent research.

Bootstrap 2,000 replicates, first resampling the two draft classes then players within each sampled class. Pair selected and baseline predictions on the same rows. These are conditional intervals, NOT reliable estimates of broad future-era uncertainty with only two classes. Nested scores, final scores, and development selection scores must be reported separately. Feature-ablation and all-family test tables are diagnostics, never permission to promote a different test winner. No confirmatory significance claim follows from the target search or these bootstrap intervals.

## Source quality and scope

Use dated Torvik-origin CSV snapshots, source field mappings checked against the archive author's collection code, and ESPN draft archives for independent name-and-school confirmation. Preserve original raw heights when available; a deterministic date-string reversal for secondary 2018-2020 heights is checked against more than 46,000 overlapping uncorrupted records. Verify a convenience sample of college and NBA totals independently against ESPN; this is not complete verification. A documented provider disagreement on one college scoring average is masked in the recorded frozen construction; the local freeze alone does not independently prove its timing before every fitting run. Eventual draft pick and undocumented recruiting ranks in the historical college cache are excluded.

Physical measurements only come from the exact actual-draft-year NBA combine record. No measurements from a later or earlier reattendance are substituted. Birth date, injuries, international-league production and scouting rankings lack complete verified sources and are not invented. Sources retrieved today may include corrections; this is retrospective reconstruction, not proof that identical snapshots were available historically.
