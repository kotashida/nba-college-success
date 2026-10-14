# Public repository contents and reproduction scope

This repository contains the research source, manuscript/PDF, publication tables and figures, dependencies, tests, frozen specifications/models, all recorded predictions and scores, candidate logs, and concise provenance/verification evidence. Local archives, backups, environments, execution transcripts, duplicate figures, forward deployment refits, and private inventories are ignored. Files are not deleted when excluded from Git.

## Data licensing and the remaining reproducibility limit

The author confirmed that redistribution permissions have not been verified for the source snapshots. Consequently, provider JSON/CSV snapshots and full processed copies (`college_seasons.csv`, `nba_seasons.csv`, `prospects.csv`, `draft_universe.csv`) are not included in the public index. Merely being downloadable or present in somebody else's GitHub repository is not an established redistribution grant. The included MIT notice covers the archived schema-reference script; it does not independently license the underlying basketball data.

Provider policies checked during repository preparation include [Sports Reference data use](https://www.sports-reference.com/data_use.html), [Disney/ESPN terms](https://disneytermsofuse.com/english/), and [NBA terms](https://www.nba.com/termsofuse). These checks establish a permission gap, not a legal determination about every scholarly use. Torvik and mirror data rights also remain unverified. No blanket data license or permission is invented.

This creates a material boundary: **a public clone can reproduce the published score and interval calculations, inspect the frozen experiment and build the manuscript; it cannot independently reconstruct every raw label or refit the models until the licensed inputs are supplied.** Do not describe the current public repository as a complete raw-data replication deposit. Changing `.gitignore` cannot resolve unavailable redistribution rights.

## What a researcher can do using a clone alone

Use Python 3.12 and the pinned dependencies. The recorded environment is Windows/Python 3.12.4; installation on a fresh online environment or another platform was not independently verified.

```sh
python -m venv .venv
# Activate .venv using your platform's standard command.
python -m pip install -r requirements-lock.txt
python -m pytest -q
python verify_results.py
python run.py paper
```

TeX Live or MiKTeX providing `pdflatex` is needed for the final command; set `PDFLATEX` to the executable path if it is not on PATH. No R installation is required: the `.R` file is a licensed schema reference only.

`verify_results.py` reads only retained public evidence. It verifies the receipt-bound freeze/predictions/scores/summary, the public subset of the retrospective seal, and all 130 frozen model hashes without deserializing them. It independently recomputes 195 final metric rows, 90 nested metric rows, and all five paired bootstrap summaries. It deliberately does not read licensed provider inputs, reconstruct ground truth, refit estimators or claim provider accuracy. The complete 203-file check `review_evidence.py` is reserved for a licensed full-data workspace.

Two preexisting tests require the full college/prospect tables and explicitly skip when those data are absent. A successful public test run must retain and report those skips; it is not proof of full-data reproduction. Synthetic inference tests are fixtures, not accuracy evidence. Saved joblib files are hashed for inspection; deserialize only trusted research artifacts in the recorded environment.

## Exact inputs needed for full independent reproduction

The source URLs, retrieval dates, byte counts and SHA-256 values are retained unchanged in `data/raw/manifest.json` and `reproducibility/source_manifest.json`. The original scientific freeze and supplemental evidence seal additionally bind processed inputs and models. There is no undocumented parent-directory dependency.

1. Obtain permission or another documented lawful access basis for the recorded source families before restoring them. This repository does not supply credentials or grant access.
2. Restore the provider files named in `data/raw/manifest.json` at exactly their recorded paths and verify their hashes. The collector can request missing recorded sources once access is authorized, but mutable ESPN responses may differ and must not replace frozen provenance.
3. **The recorded `combine.csv` is a particular undated local snapshot.** Its origin lists NBA endpoints, but no public persistent URL for these exact bytes is available. Its expected SHA-256 is `7e772e52b97d1371916827ba6c36d7bfc73d89a48e693c7080be49cd5651e361`. Current API data cannot honestly be asserted to restore this snapshot. Author-arranged, rights-cleared access or a lawful archival deposit is still required.
4. Run `python run.py data` to rebuild the processed tables. The recorded `source_quality_policy.json` and schema reference are included. Run `python verify_sources.py`, `python review_evidence.py`, `python audit_research.py`, `python verify_review.py`, and `python run.py verify`. These perform full-data reconstruction/refitting checks without retuning the consumed test.
5. Optional source-audit replay requires the 30 ESPN responses listed in the retained external-source manifest. Those raw responses are also excluded; published identities/comparisons/summary remain available. Empty provider responses are not proof of nonparticipation.

The frozen 2020–2021 evaluation must not be overwritten or used to choose a new winner. A new from-scratch replication belongs in a separate workspace with the recorded inputs and configuration, and must preserve the original receipt as historical evidence. `train_final.py`/`smoke_inference.py` are optional forward-research tools that require the licensed inputs; their generated deployment files are not necessary to review the paper and stay local.

`package.py` remains a **private full-workspace bundler** and may include unlicensed source snapshots that exist locally. Its ignored ZIP is not a rights-cleared public release. Do not distribute it as a substitute for the absent licensed deposit.

## Contents retained versus excluded

| Category | Public repository treatment | Reason |
|---|---|---|
| Research entry points, `research/`, tests, configuration and dependency files | Retained | Inspect implementation and run documented checks |
| `paper/` source, final PDF, generated tables and nine vector figures | Retained | Review and rebuild the manuscript |
| All frozen model files, final/nested/selection predictions, scores and candidate logs | Retained | Verify the actual recorded experiment and numerical comparisons |
| Original and later freeze/receipt/amendment evidence, preserved original publication code | Retained | Interpret post-evaluation corrections without erasing history |
| Source manifests, licensed schema reference, authored mask/linkage/exclusion/audit tables | Retained | Provenance and scientific limitations without wholesale source copies |
| Peer-review reports, issue register, literature verification and final assessments | Retained | Substantive review evidence, including remaining limitations |
| Raw provider snapshots and full processed source tables | Excluded, preserved locally | No verified redistribution permission |
| Raw external ESPN audit JSON | Excluded, manifests and derived comparisons retained | Same permission boundary |
| `legacy/`, backups, `tmp/`, environments, logs, review diary/private inventory | Excluded, preserved locally | Superseded/unrelated or transient material |
| Duplicate `output/figures/`, SHAP encoded data array, forward models and synthetic output CSVs | Excluded, reproducible with licensed inputs | Duplicate publication assets or optional deployment/diagnostic products |

The original 62 tracked files were individually checked; they are research-relevant, so no arbitrary removal is needed merely to produce a removal count. New essential evidence is added to the index; `.gitignore` excludes unnecessary/unlicensed local files. `git ls-files -ci --exclude-standard` must be empty after preparation, and a clean index-only export is used to test the documented public scope. Nothing is committed or pushed.

## Executed repository checks

The curated index contains 255 files, including all 130 frozen model artifacts. All 62 previously tracked research files remain included; none required arbitrary untracking. No provider snapshot, full processed source copy, backup, environment, private inventory, execution log or temporary build file is in the index.

An index-only export, containing no excluded inputs or parent-project data, passed **44 tests with two explicitly reported dataset-dependent skips**. `verify_results.py` reproduced 195 final metric rows, 90 nested metric rows and all five paired bootstrap summaries, checked 130 model digests and 162 retained sealed files, and deliberately did not read 41 licensed input files. These runs used the existing recorded Python environment; they do not establish a clean dependency installation or full-data replication.

All 18,998 local paths inventoried before index operations still exist. The original scientific/evaluation evidence is unchanged. Active README/public-guide links resolve to retained files, tracked-but-ignored paths are absent, and whitespace checks preserve the hash-bound upstream reference file without reformatting it. Changes are staged for inspection, with no commit or push.
