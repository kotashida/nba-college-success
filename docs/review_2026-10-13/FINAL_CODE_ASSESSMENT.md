# Final independent computational assessment

Date: October 13, 2026 (America/Los_Angeles). This is the second computational review, following implementation. It supplements `CODE_REVIEW.md` and the coordinator's final verification report. It examines the dated supplemental integrity seal, expanded coverage verifier, post-evaluation ESPN audit, isolated paper compiler, amendments, new tests, forward provenance, and final packaging scope. Original evidence was not modified during this re-review.

## Verdict

The implemented revisions close the confirmed operational and evidence-preservation defects identified in the first computational review. Current checks pass for all 203 retrospectively sealed evidence files and 130 originally frozen model artifacts. The scientific data/feature/model/experiment source and configuration remain exactly equal to the pre-review backup seal. The consumed freeze, receipt, predictions, scores, and summaries remain protected. No new tuning, alternative test winner, or changed scientific result was introduced.

Two additional guard defects discovered during this final review were corrected: packaging now checks the retrospective seal before any evidence-copy or ZIP writes; missing external audit caches cannot be restored with a changed provider response while silently replacing recorded provenance. Focused temporary-fixture tests passed after these corrections. Full-suite re-execution and final ZIP construction are the coordinator's final steps; this report does not claim those later steps already passed.

The remaining limitations concern scientific scope and evidence authority, rather than a demonstrated arithmetic defect: historical metric vintages, identity omissions and assumed nonparticipants, incomplete independent provider validation, two final cohorts, and rights-cleared public deposition. The code supports a reproducible local retrospective study in the recorded Windows environment. It does not establish an independently timestamped prospective trial, general future-era accuracy, or a universally portable locked installation.

## Integrity seal and coverage verification

`review_evidence.py:23` reads a dated seal anchored to original backup digests. The retained set includes previously unbound development logs, selection and nested predictions, splits, raw/processed data, scientific modules, original models, and frozen publication source. Current **203-file verification passed anew**. The seal's description correctly states that it is retrospective, local, and not preregistration or notarization. Its `--create-from-backup` path refuses to overwrite an existing seal. Backup omissions explicitly identify unavailable legacy placeholders, rather than pretending the inaccessible files were captured.

`verify_review.py:30` requires unique `(player, year, target, model)` keys, the complete target/origin/model Cartesian structure, exact player coverage per group, finite numeric predictions, and agreement with recorded truths. These are materially stronger than an inner-merge-only check. Executed independent checks on the actual saved CSVs passed for:

| Recorded evidence | Complete groups independently checked |
|---|---:|
| Final-test predictions | 130 |
| Nested predictions | 90 |
| Selection predictions | 180 |

For **each of the three actual CSVs**, this reviewer mutated an in-memory copy in five ways: deleted one player, duplicated one row, changed one truth, inserted an infinite prediction, and removed one entire model/cohort/target group. All **15 adversarial corruption cases were rejected** by `check_prediction_coverage`. No corrupted copies were saved and no original files were touched.

The expanded verifier also checks candidate IDs and counts, failure/score pairing, family search counts, finalist identity, recorded temporal sample sizes, versioned evidence agreement, and all 44 installed package versions. The coordinator's recorded output reports 1,095 candidate records in 15 origin/target groups, 50 family/feature finalist comparisons, and 15 recorded inner temporal splits. Source inspection supports these reported checks. This reviewer independently executed coverage and integrity checks, rather than rerunning the write-producing verifier command.

The original local receipt is still a record of a scoring run and retained bytes. Neither it nor the new local seal proves that a human had never seen historical outcomes. Documentation retains that qualification.

## External ESPN audit: independent numerical reconstruction

All **30 cached response files** were checked against their audit manifest SHA256 values and byte sizes. This reviewer parsed the cached JSON independently of the audit's `season_totals` helper, checked ESPN IDs and normalized names against the selected prospects, selected explicit provider total rows when present, and reconstructed games, starts, and rounded-average-derived minutes.

Observed results agree with the corrected saved audit:

- **15 of 15 identities confirmed.**
- **58 distinct player/seasons** returned in the five-calendar-season windows; returned season sets match the recorded season sets for all 15 sampled players.
- **174 field comparisons on 12 players, zero disagreements.**
- **Three identity-confirmed players have empty NBA regular-season responses:** Justinian Jessup, Marcus Zegarowski, and Balsa Koprivica.

Empty responses are expressly recorded as **not proof of nonparticipation**. There are no independent numerical field comparisons for those three players; identity confirmation must not be rephrased as validation of their zero labels. The report also correctly excludes independent VORP verification, historical source-vintage proof, and full-population accuracy. The minutes check uses a conservative rounding bound on games times a one-decimal average; it is not an exact independent total-minute source.

Explicit provider totals correctly prevent traded-season duplication in five observed windows: Devonte' Graham 2023, Cam Reddish 2022 and 2023, Ignas Brazdeikis 2021, and Tyrese Haliburton 2022. The first parser had double-counted provider rows titled `2021-22 Totals` and analogous totals. Its summary recorded 14 disagreements. That failed summary and comparison table remain in `initial_parser_summary.json` and `initial_parser_comparisons.csv`, while corrected outputs are separate. This is a documented audit-parser correction; it does not change the original study data or scores. The corrected total-row recognition and duplicate/ambiguous-row rejection have focused tests.

Final-review defect: the initial retrieval implementation checked cached hashes but ignored an existing expected hash when restoring a missing cache with `--fetch`. It could therefore replace the response and its retrieval metadata. **Corrected:** current `audit_external_sources.py:51` exposes a retrieval helper; lines 67–73 reject a changed restoration response before writing and retain the original metadata on exact restoration. Two tests exercise changed and exact responses, checking refusal/no file write in the first case and byte-identical restoration with unchanged provenance in the second. No live network call or real audit-cache rewrite was performed for these tests. The actual 30 cached files and their manifest were preserved.

The hard-coded sample is explicitly post hoc and spans four draft classes, 2018–2021. Its stratification improves transcription checks; it provides no new performance evaluation or prespecified statistical test.

## Publication compiler and amendment review

The compiler change is operational: `research/report.py` copies the current manuscript and its `generated/` and `figures/` assets into a fresh temporary directory and launches `pdflatex` there. A stale source-directory `.aux` can no longer shadow freshly generated bibliography state. Existing manuscript `\input` and `\includegraphics` dependencies all lie within these copied asset directories; no external bibliography file is required by the present source.

The new regression test plants a stale source `.aux`, intercepts compiler invocation, and verifies that compilation occurs inside the scratch directory with current manuscript/assets and without that stale auxiliary file. It also verifies the source auxiliary file is preserved. This test verifies isolation; it is not a replacement for the coordinator's actual LaTeX build and page inspection.

The recorded coordinator build log states **20 pages**, no out-of-page text bounds, and one disabled-shell-escape warning. This reviewer inspected the compiler log/layout JSON but did not independently render or visually inspect all pages in this code-focused re-review. The paper/PDF reviewer supplies that visual assessment.

The current amendment explicitly registers the isolated compilation fix and clarifies that the 2020-fitted forest on the 2019 cohort is a retrospective diagnostic separate from primary Ridge. Source diff inspection shows no altered model predictions, loss formulas, bootstrap calculations, or numerical diagnostic fitting. Current runtime and versioned amendment copies are identical; earlier amendment versions remain in `reproducibility/amendment_history/` and the verified original backup. Original scientific source is unchanged.

## Forward models and package scope

The regenerated forward metadata now binds **all five model digests**, the original scientific freeze digest, and recorded training/configuration/feature-source digests. Every digest was independently recomputed and matched. Its specifications equal the frozen selected specifications exactly. Inference checks all required model digests before deserialization, rejects invalid or historical forecast dates, and requires nonblank identifiers and at least one row. These safeguards do not turn forward refits into independent accuracy evidence.

`package.py` retains scientific snapshots, original and revised records, models, manuscript assets, new review scripts and reports, failed/corrected audit evidence, and the retrospective seal while excluding local backup, legacy, scratch, environment, cache, and ZIP directories/files. Read-only discovery at this review stage found **359 eligible files**; the eventual final count can grow as the remaining final reports are saved. No final ZIP was constructed by this reviewer.

Final-review defect: package creation originally checked only the original freeze/receipt. **Corrected:** `package.py` now verifies the optional dated seal before copying evidence or opening the output ZIP. A synthetic changed sealed development log causes packaging to fail while the previous ZIP remains byte-identical. Fresh independent replications without a retrospective seal or publication amendment remain supported by the existing no-amendment packaging test. Original backup and legacy materials remain preserved locally and are intentionally separate from the active distribution.

The included source-license notice is not blanket rights to redistribute third-party basketball statistics. Documentation appropriately states that persistent, rights-cleared public deposition remains unresolved. Packaging is local preparation and does not assert public permission.

## Executed final focused checks

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -B -m pytest -q tests/test_revision.py tests/test_review_audit.py -p no:cacheprovider
```

**Observed: 26 passed in 2.54 seconds**, using temporary synthetic fixtures. This includes the compiler isolation test and the three final guard regression cases. The total project suite is expected to contain 43 cases after these additions; its final actual outcome must come from the coordinator's subsequent full-suite run.

Read-only final source parsing passed for the new audit/verifier/seal/packaging/test modules. Current scientific-code and configuration hashes match the original retrospective seal. Forward artifact/input digests and amendment-copy equality also passed anew.

The dependency documentation is appropriately limited to locally tested Windows Python 3.12.4. It records 44 verified installed pins and a successful coordinator `pip check`, while explicitly saying fresh online installation, Python 3.11, Linux, and macOS were not tested. The platform-specific Linux XGBoost/NCCL dependency remains outside the recorded Windows lock. No invented portability success was found.

There are no further necessary computational corrections from this final review. Final completion requires the coordinator to run the complete suite after the last guard changes, construct/check the complete ZIP, preserve this assessment in it, and finalize the executed-check and publication-readiness reports. Scientific identity/vintage/uncertainty/rights limitations should remain explicit.
