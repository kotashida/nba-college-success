# Source Contract

October 13 review supplement: [methods review](review_2026-10-13/METHODS_REVIEW.md), [twelve linkage candidates](review_2026-10-13/LINKAGE_CANDIDATES.csv), and [verification report](review_2026-10-13/VERIFICATION.md). These post-evaluation findings do not change the frozen 663-player sample. Earlier noncollege/unmatched counts must not be interpreted as complete ascertainment of every known NCAA draftee.

The five-year gap enforces sporting follow-up completion. Provider metric releases and historical data vintages are separately uncertain: Basketball Reference first released BPM in 2014 and BPM2 in February 2020, and the cached VORP version is unverified. The amateur archive starts in 2008; all 44 earliest-cohort prospects have no earlier observed records, including 33 nonfreshmen. Zero `prior_seasons` denotes absence from the observed archive, not necessarily no previous college experience.

The new source audit is separate from the original frozen inputs: `audit_external_sources.py` verifies cached public ESPN responses for a post hoc 15-player sample, with 174 games/starts/rounding-bounded minutes comparisons across 12 players. All match within stated bounds. The other three identities return no NBA statistics, which is not independent proof of nonparticipation. Neither ESPN check independently validates VORP. Cached responses, URLs, retrieval dates, and hashes live in `output/audit/review_2026-10-13_external_sources/`.

Forward inference now requires nonblank identities and finite integer forecast years strictly after the forward fitting origin. The forward metadata binds each model by SHA-256 and records its training provenance. The local seal detects mismatched files; it is not an authenticated deployment service.

All required snapshots live under `data/raw`. `collect.py` caches public files and records SHA-256, URL, time and byte size. Recorded hashes are enforced when restoring a missing snapshot; changed provider responses are rejected. The NBA combine snapshot's original collection timestamp is unknown and the collector does not reconstruct it from today's API. Restore the recorded snapshot for exact reproduction. Replacing any input requires a new study and a genuinely new test. See [reproduction instructions](REPRODUCIBILITY.md).

| Source | Role | Coverage and checks |
|---|---|---|
| Torvik-origin original college CSVs | Amateur predictors and prior histories | Original field mapping; 2008-2017 and 2021 |
| Secondary college CSV | 2018-2020 amateur seasons; cross-check | Explicit years; height conversion repaired and validated against original overlap |
| ESPN historical draft JSON | Independent name-and-school evidence; actual information year | 2008-2021 all selected players; selection number benchmark-only |
| Basketball Reference-origin NBA advanced CSV | Professional targets only | Stable IDs; VORP, minutes, games and starts through 2026 |
| NBA per-game CSV | Known-appearance checks | Separate professional snapshot; never model features |
| NBA combine CSV | Optional pre-draft physical predictors | Only exact actual-draft-year measurements; negative shared IDs ignored |
| ESPN season JSON | Independent small-sample source checks | 15 college and 20 NBA field checks; one college discrepancy masked |

Repository snapshots are pinned to commits in the collector; provenance is stated without asserting a redistribution license. Torvik and Basketball Reference are original metric providers, while the repository owners preserve accessible archives. Copies with a common origin are not independent sources. Four NBA ESPN snapshots were collected; only the two matching draft identities enter the automatic verification table. The unmatched verification snapshots are not used to infer a player's identity.

`source_quality_policy.json` documents a single mask in the recorded frozen construction for Cade Cunningham's 2021 points-per-game disagreement (20.2222 in the college archive vs 20.1 at ESPN). Original sources remain unchanged. The missing value propagates into per-40 points; there is no hidden manual replacement. Other features remain source values.

Output `data/processed/identity_links.csv` lists every eligible player, the ESPN and college schools, season, college ID, professional ID and linkage assumption. `exclusions.csv` lists all exclusions. `draft_universe.csv` preserves the full selected population. No exclusion uses professional minutes, VORP, awards or All-Star selection; however, known ambiguous professional names are conservatively removed.

College seasons after actual draft year never enter predictors. A latest eligible college season can precede the draft by one year; therefore this is a recent-NCAA drafted population, not necessarily direct college-to-NBA entry. Embedded eventual draft `pick`, unverified `Rec_Rank`, role strings of unspecified derivation, jersey number and extra unlabeled numeric columns are ignored. Heights are inches; college shooting percentages follow original provider units; shooting counts are totals; `mp` is college minutes per game. NBA outcome `mp` is total minutes. Physical weight is pounds, vertical/reach measurements inches, timed drills seconds and body fat percentage points.

Missing values remain missing until training-fold imputation. Actual zero attempts remain zero; fixed shooting shrinkage returns its fixed prior at zero attempts. Prior-season history uses only earlier season-ending years. `prior_seasons` counts earlier observed college school-season records, which need not be distinct years if a player has multiple program records. Team context is contemporaneous full-amateur-roster information, not a calculation over future NBA survivors. Its weighted numerator treats missing roster BPM as zero while retaining exposure in the denominator; the paper discloses this approximation.

Sources retrieved now may have retrospective corrections. Annual NBA row counts establish broad coverage, not complete ID-level absence verification. Forty-one prospects absent from the NBA appearance sources receive assumed zero outcomes; alias errors remain possible. A five-year horizon measured in calendar seasons is not full-career success.

Forward inference requires canonical feature columns as constructed by `research/features.py`, `player`, and `prediction_year`. Missing measurements must be represented explicitly as NaN, not zero. All measurements and college summaries must be available at that forecast date. The script rejects historical years relative to the full-data refit origin. It does not automatically verify new rows or turn all college players into the validated drafted population.
