# Independent manuscript peer review

Review date: October 13, 2026. Scope: the active LaTeX manuscript, all generated textual tables and result statements, publication-figure construction, the current 19-page PDF's text and metadata, retained predictions and summaries, and primary literature. This review was performed independently of the existing October 10 audit. The separate methods/data review supplies the newly quantified ascertainment and left-truncation findings; this reviewer independently recalculated the central performance claims and all five bootstrap summaries. The backup was verified before manuscript edits. Raw sources, population, targets, models, predictions, scores, receipt and frozen specifications were not changed.

## Overall assessment

The paper is scientifically defensible as a limited retrospective benchmark and negative-result report. It is not evidence of a dependable draft decision system or of general superiority of a particular model family. Its strongest contribution is an inspectable five-season reconstruction with explicit follow-up constraints and candid baseline comparisons. College-to-professional prediction, multiple service targets, combine ablations and chronological forecasting have clear precedents. A new algorithm or an originality claim based solely on using machine learning would be unsupported.

The revised source handles the principal interpretation risks responsibly: all five targets remain visible, unfavorable primary results are retained, actual draft order is a later-information benchmark, and uncertain point estimates are distinguished from reliable gains. Remaining publication limitations include incomplete identity ascertainment, very limited independent provider verification, undocumented metric vintages, few chronological cohorts, and no persistent public replication deposit. Those limits cannot be repaired by polishing prose or repeating the consumed test.

## Independently verified numerical findings

The calculation read `output/experiments/test_predictions.csv` and used NumPy, scikit-learn and SciPy directly, without calling project metric or reporting functions. Selected, constant and draft-order forecasts were checked for all five targets, giving 15 pooled target/model groups with 98 players each. Player/year pairs were unique. The values agree with `paper/generated/holdout.tex`, `probability_metrics.tex`, `results.tex` and the generated empirical discussion at displayed precision.

A subsequent independent pass checked all 195 retained final-score rows, including every family/ablation and both class-specific tables. All 6,370 player/year/target/model records had unique keys. Maximum absolute discrepancies were 1.86e-9 for MSE measured in squared minutes, 4.55e-13 for RMSE/MAE, and 2.85e-16 for R-squared; binary probability/discrimination metrics differed by at most 2.23e-16. Undefined within-year constant Spearman correlations remained undefined. No printed result required numerical correction.

| Target | Selected primary error | Training constant error | Draft-order error | Other verified selected metric |
|---|---:|---:|---:|---|
| Five-year VORP | RMSE 3.6636805013 | 3.6548669091 | 3.3962647983 | MAE 2.1742107708; R-squared -0.0071714963; Spearman 0.2703701468 |
| Five-year minutes | RMSE 3443.5166590 | 3531.4935710 | 2793.3587576 | R-squared 0.0464199536 |
| Years active | RMSE 1.4586169081 | 1.5094040001 | 1.4238403177 | R-squared 0.0147966352 |
| Rotation | Brier 0.2274890079 | 0.2398165460 | 0.1676984257 | AUC 0.6305953933; AP 0.5661227125; prevalence 0.3979591837 |
| Starter | Brier 0.1758416115 | 0.1723126726 | 0.1321709119 | AUC 0.6462585034; AP 0.3437339473; prevalence 0.2142857143 |

The five hierarchical bootstrap calculations were also reproduced independently from paired CSV rows, with seed 199, 2,000 replicates, sorting by year/player, cohort resampling followed by within-cohort player resampling, and percentile endpoints. The largest difference from recorded interval endpoints was 4.55e-13. Sorting matters for reproducing a finite seeded resampling sequence; an initial calculation in CSV order produced a different Monte Carlo realization, and sorting resolved that implementation-order difference. This was not a discrepancy in the retained research results.

| Target | Verified 95% primary-error interval | Verified 95% constant-minus-selected interval |
|---|---|---|
| VORP | [2.522717, 4.994414] | [-0.687531, 0.573564] |
| Minutes | [2805.542675, 4083.593122] | [-333.721962, 530.519172] |
| Active years | [1.287213, 1.627767] | [-0.021244, 0.131878] |
| Rotation | [0.197008, 0.262244] | [-0.016424, 0.038577] |
| Starter | [0.125435, 0.240957] | [-0.038849, 0.028595] |

All paired intervals include zero. Their inclusion of zero neither establishes equivalence nor proves absence of practically useful effects. Two observed cohorts and fixed fitted models provide conditional uncertainty only. The manuscript correctly avoids a confirmatory significance claim. The selected VORP procedure lowers MAE while slightly worsening its primary squared-error objective; the starter model improves discrimination relative to some constants while worsening Brier score and log loss. Neither fact should be converted into a favorable primary-result claim.

## Major concerns and implemented responses

### P1: Follow-up maturity is not historical metric availability

Affected source: `paper/five_year_nba_outcomes.tex:38`, `:140`, `:257`; related original wording in `docs/PROTOCOL.md` and `docs/AUDIT.md` should receive the same qualification.

Confirmed provider fact: Basketball Reference's original BPM was released in 2014 and its second version was introduced in February 2020. VORP derives from BPM. See the [provider methodology](https://www.basketball-reference.com/about/bpm2.html?trk=article-ssr-frontend-pulse_little-text-block). The archived NBA CSV's exact metric vintage has not been independently established. Consequently, `draft_year + 5 <= origin` proves completion of the relevant sporting follow-up window, not that the archived VORP definition was available for fitting in 2013 or 2014. Modern advanced-metric reconstruction and historical information availability are different issues.

Response: narrowed the information-clock claim, described the rule as follow-up eligibility, and explicitly disclosed metric-release and version uncertainty. Kept the recorded VORP labels and all scores. This is an essential scope correction, not proof of a discovered player-outcome error. A literal historical-deployment study needs dated metric releases or a measurement rule whose historical availability is established.

### P1: Population ascertainment is incomplete

Affected source: `paper/five_year_nba_outcomes.tex:65`, `:69`, `:255`; evidence inputs `data/processed/exclusions.csv`, `draft_universe.csv` and `college_seasons.csv`.

The team linkage review identifies 12 candidate same-school naming variants among exclusions; 11 also agree with the retrospective college archive's eventual draft-pick field. Row-specific primary biography corroboration is recorded for all 12 in `LINKAGE_CANDIDATES.csv` and explained in `METHODS_REVIEW.md`. They are documented excluded candidates, not a fully reconstructed and adjudicated replacement population. Exact name-and-school matching is stronger than unchecked fuzzy matching but demonstrably omits recognizable NCAA draftees. The first exclusion count already mixes noncollege prospects and unresolved links, so it must not be described as complete ascertainment of all drafted NCAA players.

Response: added the quantified limitation, labeled the draft-pick corroboration post hoc, and kept the frozen 663-player population unchanged. Newly adjudicated aliases belong in a documented reconstruction with preserved original outputs. Any corrected historical comparison would be a correction or sensitivity analysis after test consumption, not a fresh confirmatory test.

### P1: Independent provider verification remains limited

Affected source: `paper/five_year_nba_outcomes.tex:62`, `:255`, `:257`, `:273`; retained evidence `data/processed/independent_checks.json` and `independent_source_checks.csv`.

The recorded convenience sample contains 35 field checks with one masked college scoring disagreement. Agreement of more than 46,000 records between copies with a common origin verifies transcription consistency rather than independent statistical correctness. ESPN checks do not independently establish VORP accuracy. Forty-one absent NBA records are assigned assumed zeros. These choices are transparently described but remain meaningful sources of uncertainty, particularly for negative outcomes and rare high-value players.

Response: retained the explicit limitations and corrected the suggestion that VORP must be reconstructed from play-by-play: the provider defines it from box-score-based BPM and exposure. A broad provider audit should cover aliases, assumed nonparticipants, traded seasons, missing values and influential high-value cases. This review did not execute a new comprehensive provider comparison and does not claim to have done so.

### P1: Small chronological samples and consumed outcomes limit inference

Affected source: `paper/five_year_nba_outcomes.tex:142`, `:144`, `:170`, `:246`, `:261`; recorded splits `reproducibility/splits.json`.

Three mature inner validation cohorts and early fitting pools of 44, 89 and 140 players support a sizeable configuration/family/transformation comparison. Development skill is selected performance and is not unbiased. The nested 2018-2019 cohorts were already consumed in an earlier reconstruction. The final two cohorts are historical observations, not a registered prospective trial; the freeze demonstrates the recorded execution sequence rather than lack of previous human knowledge. Current prose acknowledges these limitations appropriately.

Response: preserved the conservative interpretation and added exact execution dates to distinguish 2026 computation from simulated 2020-2021 origins. No re-ranking or model substitution was performed. Future performance claims require new mature cohorts and a declared procedure. Additional tuning on the current test cannot resolve this concern.

## Moderate concerns and corrections

| Priority/status | Evidence | Finding and response |
|---|---|---|
| P2, confirmed documentation error corrected | Source line 23; original PDF page 1; PDF metadata; freeze and receipt timestamps | The manuscript said March 20, 2025 although it includes outcomes through the 2026 season, literature published in late 2025 and August 2026, and an October 2026 execution receipt. Changed the revision date to October 13, 2026 and stated actual freeze/scoring times. No invented claim about the original draft date. |
| P2, confirmed diagnostic scope clarified | `research/report.py:240`-`:248`, manuscript `:227`, `:231`, `:238` | The interpretability model is the 2020-fitted RF finalist through class 2015, explained on class 2019. Those 2015 outcomes mature in 2020, so this is retrospective identity-held-out explanation, not a simulated 2019 forecast. Revised prose and captions. SHAP remains on the asinh target scale; permutation remains original-scale VORP MSE. |
| P2, confirmed range behavior disclosed | Manuscript `:162`; retained selection/nested/test CSVs | Active years is an unconstrained continuous regression response despite its 0-5 integer support. The selected nested prediction for Wendell Carter Jr. is 5.217221. Final primary active-year forecasts are within [2.834419, 4.705499], while the draft-order benchmark reaches 5.480005 and has a minutes forecast as low as -245.663798. Disclosed raw unbounded scoring; did not clip, refit or improve consumed scores. |
| P2, confirmed history limitation disclosed | `research/features.py:38`-`:50`; manuscript `:128`; team feature audit | The panel starts in 2008, so all 44 draftees that year have zero observed previous seasons, including 33 nonfreshmen. A zero history count is not equivalent to being a freshman. Added explicit left-truncation wording without rebuilding features. |
| P2, verified relevant literature omission corrected | Manuscript `:47`, `:308`; primary sources in `LITERATURE_VERIFICATION.md` | Added Czasonis et al.'s January 2024 relevance-based draft forecasting paper. It forecasts rookie VORP/minutes using earlier draftees, so chronological college forecasting and these outcomes are established choices. The present five-year horizon and preservation of assumed nonparticipants offer a narrower comparison. |
| P2, provenance wording corrected | Manuscript `:90`; frozen construction code and local receipt | Replaced the unqualified prespecification implication with the verifiable statement that service thresholds are fixed in frozen construction code and are not optimized during candidate fitting. The local record is not public preregistration. |

## Minor editorial and presentation findings

Li and Cao's primary publisher record identifies volume 226, pages 83-96, published October 14, 2025. Added the page range; secondary copies have inconsistent pagination/copyright dates and were not used to override the publisher's citation. Corrected Wiethuechter's surname to its verified umlaut form in prose. The generated interpretability paragraph says "a asinh"; its reporting template should say "an asinh" and explicitly identify the RF as a finalist rather than the selected Ridge procedure. The root reviewer owns that generated-template edit and publication-amendment registration.

The reviewed development heatmap, binary calibration, SHAP and permutation PNGs were legible, correctly labeled and not visibly clipped. The calibration plot is descriptive with about 20 observations per bin; it should not support a firm calibration claim. A useful future improvement is to display bin counts and uncertainty, declared as a descriptive plot amendment. Figure and table units are consistently distinguished. The current supplementary probability table explains why two per-year constant probabilities need not have pooled AUC exactly 0.5 or AP exactly equal to pooled prevalence.

This reviewer read the LaTeX source and generated textual tables, and extracted the current PDF's first/last page content and metadata, but did not claim a visual inspection of every PDF page. Final compilation and complete rendered-page inspection are separate root-review tasks. The source was edited only after backup verification, and a final PDF should be produced from that revised source before delivery.

## Prioritized follow-through

1. Complete the root's final integrity checks, regenerated publication text, LaTeX compilation and visual review; confirm all printed numbers still bind to the original retained evidence.
2. Retain the new source-clock, alias, left-truncation, diagnostic-origin and unbounded-regression disclosures in every package-level summary. They are substantive scientific limits, not cosmetic caveats.
3. Keep provider accuracy, exact metric vintages, full alias adjudication and public replication access marked unresolved unless new evidence establishes them. Do not promote local consistency checks into external validity.
4. Obtain any venue-required affiliation, funding, competing-interest and assistance declarations from the author. They have not been fabricated or inferred from a filesystem path.
5. For a future study, extend verified college history backward, predeclare admissible bounded forecasting procedures, and reserve new five-season-mature cohorts. This is proposed future work, not an amendment to the frozen primary results.

Conditional editorial verdict: major revision of scope and reproducibility statements was warranted; the specific manuscript corrections above are now implemented. The paper can be evaluated as an incremental retrospective benchmark with negative/inconclusive predictive findings. Full submission readiness still depends on the unresolved external verification/access requirements and the root's final executed checks.
