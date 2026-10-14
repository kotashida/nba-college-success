# Verified Results

Independent college-to-NBA study: 663 drafted prospects, 98 final-test prospects (2020-2021).
All targets use five calendar NBA regular seasons after actual draft year.

| Target | Frozen model | Selected error | Constant error |
|---|---|---:|---:|
| Five-year VORP | Regularized linear | 3.664 | 3.655 |
| Five-year minutes | Three-family ensemble | 3,444 | 3,531 |
| Years active (of five) | Three-family ensemble | 1.459 | 1.509 |
| Sustained rotation | Three-family ensemble | 0.227 | 0.240 |
| Sustained starter | Extra Trees | 0.176 | 0.172 |

Regression errors are original-scale RMSE; binary errors are Brier scores.
The test is consumed. Do not choose a new winner using supplementary test scores.
Only two test cohorts; bootstrap intervals are conditional and do not establish future-era guarantees.
College sources are dated and school-confirmed, but fully independent verification is limited to a small sample.