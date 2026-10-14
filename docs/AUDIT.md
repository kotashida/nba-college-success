# Research audit and publication readiness

This document preserves the October 10 audit. The subsequent [October 13 peer review](review_2026-10-13/PEER_REVIEW.md), [verification](review_2026-10-13/VERIFICATION.md), and [final assessment](review_2026-10-13/FINAL_ASSESSMENT.md) supersede its current-readiness claims where stated. New findings distinguish follow-up maturity from historical metric release, quantify twelve excluded naming variants, disclose left-truncated histories and retrospective forest interpretation, and strengthen operational and evidence checks. The historical results below remain unchanged.

Audit date: October 10, 2026. Scope: active code, raw and processed snapshots, all recorded experiment outputs, frozen evidence, LaTeX and PDF, and the original R Markdown and earlier reconstruction retained in `legacy/`. No models were retuned and no final-test winner was substituted.

**Verdict: scientifically defensible as a limited retrospective benchmark and negative-result study; not yet a fully submission-ready archival research package.** Numerical reproduction passes. The remaining obstacles are limited independent data verification, modest incremental novelty, only two test cohorts, and the absence of a persistent, rights-cleared public replication deposit. A strong predictive-superiority or scouting-replacement claim would be unsupported.

## Findings and corrections

| Finding | Action and consequence |
|---|---|
| Selected VORP RMSE 3.664 vs constant 3.655; starter Brier 0.176 vs 0.172 | Abstract now states the negative comparisons. Lower VORP MAE and positive ranking correlation do not rescue the prespecified squared-error objective. |
| Minutes, active years and rotation have modest point-estimate gains; all five paired intervals include zero | Preserved every outcome and qualified the conclusions. These intervals neither establish equivalence nor rule out useful effects. |
| Retaining an evaluation checked predictions but not all receipt-bound summaries; a deleted receipt could reopen existing results | Strengthened `check_freeze` to check freeze, predictions, scores and summary, and reject evaluation artifacts without a receipt. Report generation now checks frozen evidence before writing publication assets. Added four regression tests. |
| Protocol said mean imputation, implementation used medians | Corrected protocol to median; no fitting or prediction changed. |
| Earlier reconstruction already evaluated 2018–2019 | Disclosed prior exposure in the manuscript and documentation. Nested forecasts are retrospective diagnostics, not independent confirmation of the revised design. |
| A local hash freeze does not establish public preregistration or never-seen historical outcomes | Replaced stronger wording with the verifiable claim: recorded specifications preceded the recorded scoring run; frozen evidence has been retained. |
| Feature-group finalists differ in tuning choices as well as predictors | Clarified that these comparisons do not isolate the marginal effect of combine measurements or engineered features. |
| Binary log loss and AP were exported but absent from manuscript tables | Added a supplementary probability-metrics table with prevalence, Brier score, log loss, AUC and AP. |
| Novelty was insufficiently distinguished from existing work | Reframed contribution around school-confirmed reconstruction and label-maturity constraints; verified citations, corrected dissertation metadata and added relevant 2026 work. |
| Historical README pointed at obsolete entry points | Corrected archive guidance. Expanded reproducibility instructions and added `audit_research.py`. |

Fitting, features, target definitions, selection routines, frozen models and numerical evaluation artifacts remain unchanged. Integrity/publication amendments preserve original code and require equality of the experiment AST outside `check_freeze`. Local amendment records provide an inspectable history, not independent notarization.

## Independent verification

The separate audit reconstructed **3,315 target fields for 663 prospects** directly from raw NBA rows with total-row precedence and the fixed draft-anchored window. All matched. It recalculated **195 metric rows**, reproduced **five hierarchical bootstrap summaries**, checked **130 frozen model/cohort prediction groups**, and checked final selection against development predictions and trial logs. Maximum stored-model prediction difference was **1.82e-12**. All **1,095** recorded candidate evaluations were present; none was disqualified.

It also checked all **90 nested metric rows** and every saved development/nested truth against the processed targets. Recalculated nested metrics differed by at most **1.02e-7** because some original estimator arrays were scored in float32 while CSV recalculation uses float64. This rounding difference does not change the published precision; original scores were retained. The final-test metric checks use stricter tolerances. A small audit evidence copy is versioned in `reproducibility/audit_verification.json`.

Ten independent selected-model refits also reproduced recorded predictions. **17 tests passed**, including chronological maturity, outcome-shock isolation, fold-fitted preprocessing, traded seasons, source restoration and receipt corruption. The collector verified the 38 recorded input snapshots without replacing them, and synthetic forward inference passed. Existing source checks comprise 35 field comparisons on four named players, with one documented masked disagreement. Same-origin archive agreement is a transcription check, not independent verification. Audit evidence is in `output/audit/verification.json`; refit evidence is in `output/experiments/verification.json`.

The receipt, freeze, test predictions, scores and summaries retained their original SHA-256 values. The original receipt hash is `caa133b8d5d0f868a9438ca5aa4c7e2a29e87c60173e0fdbe797b65074bd6f52`. There was no redevelopment or new test evaluation. Publication tables were regenerated from retained artifacts and the revised 19-page PDF was compiled and visually inspected. There are no text bounds violations, overfull boxes or unresolved references; the sole compiler warning concerns disabled shell escape, which is unnecessary for the existing PDF figures.

## Scientific assessment

The five-year maturity rule is correctly applied to fitting and tuning: final selection uses 2013–2015 validation classes; 2020 and 2021 models fit through 2015 and 2016 respectively. Imputation, scaling, categorical encoding and Yeo–Johnson transforms are training-fitted. Primary predictors exclude draft order, professional data and outcomes. Prior histories use earlier college seasons; roster context uses contemporaneous college information. No computational leakage was found in the reviewed active pipeline.

The estimand is realized value and service **conditional on eventual draft selection and a recent school-confirmed NCAA record**. It cannot identify NBA entry probability across the NCAA or causal effects of college experience, size or skill. Professional opportunity influences minutes, starts and VORP. The draft-order benchmark uses later information and may encode allocation effects; its substantially better service forecasts do not justify adding it to a pre-selection model.

Selection risk remains substantial: only three early validation classes support 2020 selection, early fits have 44–140 players, and 73 base candidates per target/origin plus an ensemble are compared. Development skill is selected performance, not an unbiased estimate. Two cohort resampling units cannot establish broad future-era coverage; percentile intervals omit refitting and adaptive design uncertainty. Multiple outcome searches do not support confirmatory significance claims. Nonlinear target inversion and missing teammate BPM are disclosed approximations, not reasons to retune on this test.

The original R workflow's transformed-target errors and approximate R-squared are not comparable to the current original-scale results. Its global preprocessing, random validation, debut-anchored labels, linkage weaknesses and causal SHAP narratives are not used as evidence for the revised paper.

## Essential before journal submission

1. Independently resolve or explicitly retain uncertainty for the 41 assumed nonparticipants and the four ambiguous/conflicting professional identities. Verify college and professional totals on a broader, stratified sample, including traded seasons and high-value tails. Provider errors discovered after evaluation must be documented; a corrected score is a sensitivity result, not a renewed pristine test.
2. Make the replication package persistently accessible under verified provider permissions. The local bundle is complete, but Git excludes required snapshots and models. A code-only repository cannot support the present numerical reproducibility claim by itself.
3. Position the paper as a retrospective benchmark/negative result. If stronger generalization or feature-benefit claims are required, preregister a revised study and reserve genuinely new mature cohorts. Under this horizon, the 2022 draft class's complete labels require the 2027 season; no currently consumed cohort can replace it.
4. Apply the selected venue's submission format and complete author-supplied affiliation, funding, conflicts and any required assistance disclosures. No missing institutional statements were invented.

Optional future work: extend verified amateur history backward, acquire dated age/injury/scouting records, compare simpler tightly controlled feature procedures, improve calibration diagnostics on larger cohorts, or use opportunity-aware/schedule-normalized outcomes. These require a new development cycle and independent evaluation, not changes justified by the present test scores.

An applied sports-analytics venue is the most plausible fit. [Journal of Sports Analytics](https://journals.sagepub.com/home/san) explicitly covers player/team applications; its [submission instructions](https://journals.sagepub.com/author-instructions/san) require sufficient original contribution and use double-anonymized review. This is a scope assessment, not an acceptance prediction. Likely rejection grounds are incremental novelty, uncertain practical advantage and insufficient public data access.

## Literature verification

Claims were checked against the [Coates–Oguntimein working paper](https://college.holycross.edu/hcs/RePEc/spe/CoatesOguntimein_NBA.pdf), [Moxley–Towne publisher record](https://www.sciencedirect.com/science/article/pii/S1469029214000983), [Kannan et al. institutional publication](https://scholar.smu.edu/datasciencereview/vol1/iss3/7/), [Teramoto et al. indexed abstract](https://pubmed.ncbi.nlm.nih.gov/28135222/), [Li–Cao publisher record](https://aemps.ewapub.com/article/view/27926), and [Wiethüchter institutional repository](https://hdl.handle.net/10400.14/55936). [Milošević et al. (2026)](https://journals.sagepub.com/doi/10.1177/22150218261484000) uses observed NBA seasons, a later information set than this study. Model-selection cautions are supported by [Cawley–Talbot](https://jmlr.org/papers/v11/cawley10a.html). Literature checking establishes these specific comparisons, not an exhaustive proof of originality.
