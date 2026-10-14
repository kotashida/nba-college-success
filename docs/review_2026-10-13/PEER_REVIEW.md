# Comprehensive independent peer review

Review date: October 13, 2026, America/Los_Angeles. Reviewed version: the working project as supplied, including uncommitted manuscript/PDF changes, followed by the implemented revision. This report combines independent statistical, computational, and manuscript/literature reviews. Detailed supporting reports are [METHODS_REVIEW.md](METHODS_REVIEW.md), [CODE_REVIEW.md](CODE_REVIEW.md), [PAPER_REVIEW.md](PAPER_REVIEW.md), and [LITERATURE_VERIFICATION.md](LITERATURE_VERIFICATION.md). The [issue register](ISSUE_REGISTER.csv) distinguishes confirmed errors, demonstrated limitations, unresolved concerns, and optional future work.

## Overall assessment

The active study is a credible, modest retrospective benchmark of five-year NBA outcomes among school-confirmed NCAA draftees. It is more defensible than the archived R analysis and earlier reconstruction: it retains nonparticipants, uses a fixed draft-anchored window, handles traded totals, fits preprocessing within training folds, observes a five-year follow-up gap, retains all targets, and reports negative baseline comparisons. Independent numerical reproduction found no material error in the frozen outcomes, primary predictions, metrics, or bootstrap intervals. Those results should be preserved.

The supplied version nevertheless overstates the historical information clock in places, misses at least twelve school-confirmed naming variants, incompletely documents early history truncation, and presents a retrospective interpretation diagnostic without sufficiently explaining its fitting date. It also contains a false manuscript date and operational weaknesses in inference, packaging, and supplementary evidence integrity. These are substantive corrections, not reasons to select a better-performing model on the consumed test.

The revised manuscript now supports a conditional, retrospective, negative/inconclusive result. It cannot substantiate literal contemporaneous deployment at every historical origin, superior scouting decisions, causal trait effects, complete ascertainment of NCAA draftees, or broad future-era performance guarantees. An applied benchmark/negative-result venue is a plausible framing; originality remains incremental. Submission still requires provider/archival permissions, a persistent accessible replication deposit, and author/venue declarations. This audit cannot create those permissions or invent institutional facts.

## Scope and preservation

The audit covered all active Python modules and entry points, tests, configuration, dependency lock, manuscript source and generated assets, 38 recorded input snapshots, processed data/linkage/exclusion records, development logs, saved predictions, all 130 frozen model/cohort bundles, original freeze/receipt and later integrity amendments. The historic R Markdown and collector/processing scripts and earlier reconstruction were examined to distinguish superseded evidence and prior evaluation exposure. Large historical game/play-by-play datasets are not inputs to the active study and were reviewed by inventory/schema and role rather than rerun as obsolete models. Environment and Git objects were backed up, not treated as research findings.

Before research edits, 19,343 readable files (2,732,784,016 original bytes) were captured and every archived SHA-256 compared with its original. No mismatches occurred. Ten legacy online-only OneDrive files, totaling 422,010,332 bytes, could not be hydrated because the cloud provider was not running; exact names/errors are in the backup manifest. They remain untouched and are unnecessary for the active replication. Thus the backup covers all readable originals, not the inaccessible historical placeholders. No unavailable file is claimed to have been independently verified.

The original scientific modules, config, raw/processed sources, frozen models, test receipt, predictions, scores, and summaries remain byte-identical. A new October 13 local seal binds 203 original evidence files, including development records absent from the original freeze. It is explicitly retrospective, not external preregistration. Publication amendments preserve the earlier amendment and pre-evaluation code. New source/ascertainment checks are post-evaluation audit evidence; they are not newly prespecified experiments.

## Major concerns and implemented response

### R01 — Historical metric release is distinct from follow-up maturity (major; confirmed scope error)

`research/experiment.py:28` and `:106` correctly implement the integer-year rule: training class + 5 must not exceed the fitting origin, and validation class + 5 must not exceed the tuning origin. This prevents using uncompleted sporting follow-up. It does not establish historical availability of the same outcome metric or archived predictors. Basketball Reference's [BPM methodology](https://www.basketball-reference.com/about/bpm2.html) dates original BPM to 2014 and BPM2 to February 2020; VORP derives from BPM. The exact metric version in the cached NBA CSV is unverified. A literal 2013 forecast cannot be certified by showing that 2008 players completed five seasons if the relevant published metric definition was not then available.

Revised the introduction, maturity methods, and source limitations, and aligned `docs/PROTOCOL.md` and `docs/DATA.md`. The study now claims retrospective chronological reconstruction under completed follow-up, not verified historical database releases. Sporting chronology still passes. No cached VORP value, model, or score was replaced. Dating/versioning all predictor/outcome definitions remains necessary for a stronger point-in-time claim; it requires new source research and a separately declared study.

### R02 — Demonstrated underascertainment from naming variants (major; confirmed data limitation)

`research/data.py:193` matches normalized name plus school. The active alias/normalization registry does not reconcile all known names. Twelve of the 173 nominally unmatched selections have unique latest eligible, same-school records under documented variants, such as J. J. Hickson/JJ Hickson, Jeff Pendergraph/Jeff Ayres, Keith/Tiny Gallon, and Dewan Hernandez/Dewan Huell. [LINKAGE_CANDIDATES.csv](LINKAGE_CANDIDATES.csv) records identifiers, dates, schools, evidence and primary biography URLs. Eleven have matching embedded eventual picks; one lacks that field. Pick agreement is post hoc corroboration only and never becomes a primary feature. These twelve candidates are all outside 2020–2021; this manual audit is not exhaustive certification of the remaining exclusions.

The paper now quantifies this selection limitation. Original inclusion/training/outcomes remain unchanged: changing historical training records would change the frozen experiment. A future corrected population should resolve these names and the four ambiguous/conflicting professional identities before new fitting, with a new independent test. No accuracy sensitivity from adding these records was run or implied.

### R03 — Absent NBA records do not independently prove zero outcomes (major; unresolved source accuracy)

`research/data.py:220` assigns empty-window zeros when no NBA identity exists. There are 41 such prospects. Same-origin per-game checks found no contradictory appearances, but that is not independent absence verification. The original ESPN convenience checks cover 35 fields and cannot certify all identities or VORP. Four professional name conflicts/ambiguities are conservatively excluded rather than guessed.

A separate post-evaluation ESPN audit now confirms all 15 sampled identities and 174 season-field comparisons across 12 players, including high/low participation and traded seasons. Games/starts agree exactly; minutes agree within the bound from one-decimal average minutes. The three sampled final-test assumed nonparticipants return no NBA season rows. Those empty responses remain supporting absence-of-record evidence, not proof of no appearance. No VORP was independently validated. The revised manuscript states the exact extent and limitations. Full independent identity/appearance verification remains open; provider errors, if later established, require both original and corrected evidence rather than reopening this test.

### R04 — Local freeze does not prove prefit design or never-seen outcomes (major; provenance limitation)

The original local freeze is dated October 9, 2026, 21:33:17 UTC, and its receipt 21:33:49 UTC. The five-year calendar origins 2020–2021 are simulated dates, not execution dates. Source hashes bind operational thresholds and frozen choices before that recorded scoring run. They are not external time-stamped evidence of prefit specification, and cannot prove that historical outcomes were never seen by researchers. An earlier reconstruction already evaluated 2018–2019.

Removed unsupported strong prespecification wording, retained accurate fixed-operational-definition language, and added actual execution dates. The paper already distinguished previously consumed nested cohorts; this remains explicit. No public preregistration, pristine prospective test, or independent design confirmation is claimed.

### R05 — Small, adaptive selection problem and weak generalization evidence (major; confirmed limitation)

Final tuning compares 73 base candidates plus an ensemble per target on only three validation cohorts. Inner training sizes are 44, 89 and 140; final fits contain 372 and 415 prospects. Five outcomes, transformations, families and feature procedures create selection risk. Development skill is selected performance, not an unbiased estimate. Two test classes (48 + 50 players) cannot identify population-level future-era uncertainty.

The paired two-stage percentile bootstrap correctly reproduces the recorded conditional calculation, but two resampled cohort units provide weak information about class-level variation and omit refitting/adaptive design uncertainty. All five paired intervals include zero. That does not establish equivalence, absence of useful effects, or significance. Retained the calculation and conservative interpretation. Larger independent mature cohorts and a new development protocol are future requirements, not changes justified by current test scores.

### R06 — Interpretation diagnostic is retrospective at a later fitting origin (moderate; confirmed labeling defect)

`research/report.py:240` loads the 2020 Random Forest fitted through draft class 2015 and explains draft class 2019. The 2015 labels complete follow-up in 2020, so this is not a valid 2019-origin forecast even though the diagnostic players are not fitting records. The primary VORP model is Ridge, not this forest. Its SHAP units are the asinh target scale; the saved contributions reconstruct that estimator to machine precision.

The generated description and manuscript now identify a 2020-fitted retrospective forest diagnostic on 2019 and separate it from both primary Ridge and chronological procedure diagnostics. Causal interpretations remain disallowed by the observational/model-specific analysis. Numerical SHAP/permutation calculations are unchanged.

### R07 — Engineered history is left-truncated in early cohorts (moderate; demonstrated limitation)

`research/features.py:39` correctly uses only earlier seasons for the same college ID. The archive starts in 2008: all 44 earliest prospects have zero observed prior records, including 33 nonfreshmen. The first inner fit therefore cannot learn effects from actual prior-history variation; later early folds contain only one or two preceding archived seasons. No duplicate college pid/year rows were observed in the current snapshot.

The paper/data contract now distinguishes no earlier observed record from no prior experience. Missing prior means still undergo training-fitted imputation. Backward extension would improve evidence but constitutes a new development cycle. No synthetic history or modified features were introduced.

### R08 — Continuous regressors need not respect outcome support (moderate; confirmed reporting omission)

The active-year estimand is an integer 0–5, but the regressors are unconstrained. One selected nested prediction is 5.2172207 (Wendell Carter Jr., 2018); selected final-test predictions remain within 2.8344–4.7055. Some supplementary regressors produce negative minutes or active years above five. Those are mathematical forecasts, not valid realized counts.

Disclosed raw unconstrained scoring. Clipping or changing model classes would change consumed results and was not done. Bounded/count procedures may be assessed only under a separately declared future analysis. Binary predictions retain their existing clipping and Brier/log-loss definitions.

### R09 — Supplementary development evidence was unbound (moderate; confirmed integrity gap)

The original freeze/receipt binds inputs, model files, final predictions and summaries, but not `trials.jsonl`, nested/selection prediction records or split logs. Existing audit/report code reads those artifacts. No corruption was observed. The new retrospective seal preserves their supplied hashes without editing the original freeze. `verify_review.py` checks complete player/model/cohort keys, all 1,095 candidate identities, 50 frozen family/feature finalists, recorded temporal sizes and versioned copies. A meaningful test verifies that changing a development log is rejected. The seal detects local mismatches, not malicious rewriting of every local record or external authenticity.

### R10 — Forward inference and bundle safeguards (moderate; confirmed operational errors, corrected)

The former `predict.py` year comparison allowed NaN, infinities and fractional dates. It also loaded forward estimators without artifact hashes. The revised script requires a nonempty input, nonblank names and finite integer calendar years after the fitting origin, and checks every forward model digest before loading. `train_final.py` records model hashes, frozen-source digest and training provenance. Fixed choices were refitted on mature labels for forward research use; these are not new accuracy estimates.

The former packager traversed backups/scratch and required an amendment even for a fresh replication. It now excludes backups/tmp/environment/history caches and handles absent amendments honestly. Data-dependent tests now explicitly skip missing datasets rather than silently pass. The 44 installed lock versions match and `pip check` passes on recorded Windows/Python 3.12.4; clean installation and other platforms remain untested.

## Minor/editorial findings

- Corrected the title-page March 20, 2025 date, which contradicted 2026 outcomes/references. Current revision date is October 13, 2026; original supplied source/PDF remains in the backup.
- Added the directly relevant [Czasonis et al. 2024 Sloan paper](https://www.sloansportsconference.com/research-papers/how-to-predict-the-performance-of-nba-draft-prospects), contrasting rookie VORP/minutes with a five-year fixed horizon and preserved nonparticipants. No incompatible accuracy comparison was added. Corrected Li–Cao publisher pagination and Wiethüchter spelling. Reference existence/metadata and specific claims were verified through primary records with access limits recorded; not every subscription/full text or remote pinned commit was fetched.
- Retained appropriate caveats: conditional-on-selection population, opportunity-mediated service outcomes, fixed thresholds in shortened seasons, nonlinear target inversion, correlated predictors, missing teammate BPM approximation, separately tuned feature-group procedures, and actual draft-order information available only after selection. These are design limitations, not demonstrated computational bugs.
- Historical R/earlier-model claims about transformed error, approximate R-squared, random/full-sample preprocessing, causal SHAP or scouting bias are not evidence for the active study. Archived files remain historical. Added current navigation rather than rewriting the retired research.
- An internal first pass of the new ESPN audit double-counted traded totals because ESPN labels them `2021-22 Totals`, not `TOT`. The discrepancy was in the new audit parser, not the frozen pipeline. Initial evidence is retained; the parser now recognizes explicit total labels, rejects duplicates, and has a regression test. Rechecking all 174 fields then passed. No provider value was silently repaired.

## Independently verified results and discrepancies

| Outcome | Selected error | Constant error | Paired 95% interval: constant minus selected |
|---|---:|---:|---:|
| VORP (RMSE) | 3.663681 | 3.654867 | [-0.687531, 0.573564] |
| Minutes (RMSE) | 3443.516659 | 3531.493571 | [-333.721962, 530.519172] |
| Active years (RMSE) | 1.458617 | 1.509404 | [-0.021244, 0.131878] |
| Rotation (Brier) | 0.227489 | 0.239817 | [-0.016424, 0.038577] |
| Starter (Brier) | 0.175842 | 0.172313 | [-0.038849, 0.028595] |

All 3,315 reconstructed target fields match raw recorded NBA rows. All 195 final-score and 90 nested-score rows reproduce; the largest nested rounding difference is 1.017e-7, consistent with original float32 estimator-array scoring versus float64 CSV recalculation and immaterial to printed precision. All 130 stored model/cohort prediction groups reproduce within 2.73e-12; ten independent selected refits reproduce within 1.82e-12. All five hierarchical bootstrap summaries match. Coverage checks confirm 130 final, 90 nested and 180 selection model/target/cohort groups; every candidate log and 50 finalist specifications match. No corrected final score is required. The important discrepancies are scientific scope/ascertainment and operational validation, not improved model accuracy.

## Prioritized revision plan and disposition

1. **Completed:** preserve originals; qualify historical-information and preregistration language; disclose quantified linkage and history limits; correct dates, interpretation and literature; retain all frozen results.
2. **Completed:** independently replay numerical and coverage checks, add retrospective evidence binding and meaningful operational tests, seal forward research artifacts, repair package traversal, regenerate/compile publication assets and inspect them.
3. **Open before archival submission:** establish provider permissions and persistent bundle access; broader independent linkage/nonparticipation/VORP verification; complete venue-specific author/affiliation/funding/conflict/assistance declarations. No fabricated declarations or public data publication occurred.
4. **Future study, not a current fix:** independently vetted expanded historical cohorts, dated scouting/injury/age information, bounded/opportunity-aware outcomes, simpler controlled feature comparisons and genuinely unused mature test cohorts. The 2022 class requires complete 2027-season follow-up under this horizon and is not currently a replacement test.

The accompanying [verification report](VERIFICATION.md), [change log](CHANGELOG.md), and [final adversarial assessment](FINAL_ASSESSMENT.md) document what was actually executed and what remains unresolved.
