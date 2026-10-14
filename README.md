# NBA College Success

Forecasting five-year NBA value and participation among school-confirmed NCAA draftees under retrospective chronological validation. The reported predictive gains are negative or inconclusive; frozen 2020-2021 outcomes have not been used to retune the study.

[Paper](paper/five_year_nba_outcomes.pdf) | [Source](paper/five_year_nba_outcomes.tex) | [Protocol](docs/PROTOCOL.md) | [Data](docs/DATA.md) | [Public review and data access](docs/PUBLIC_REVIEW.md)

## Reproduce the public numerical evidence

The repository includes code, dependencies, publication assets, all recorded predictions/scores/candidate logs, and 130 frozen model artifacts. Provider snapshots and full processed copies are excluded because the author has no verified redistribution permissions. **A clone can reproduce published metrics/intervals and build the paper; complete raw-label reconstruction and model refitting remain blocked on licensed source access.** The exact missing inputs and the undated combine snapshot limitation are documented in [PUBLIC_REVIEW.md](docs/PUBLIC_REVIEW.md).

Python 3.12 is required. The tested environment is Windows/Python 3.12.4 with the exact lockfile; clean installation and other platforms remain unverified.

```sh
python -m venv .venv
# Activate .venv, then:
python -m pip install -r requirements-lock.txt
python -m pytest -q
python verify_results.py
```

The public-only verifier recalculates 195 final and 90 nested metric rows and all five paired bootstrap summaries, verifies public evidence hashes, and checks 130 frozen model digests. It reads no excluded source table and performs no retuning. Two dataset-dependent tests explicitly skip in a source-free clone; those skips are expected and must not be presented as full-data verification.

To rebuild the manuscript, install TeX Live or MiKTeX providing `pdflatex` (or set `PDFLATEX`), then run `python run.py paper`. The source, all generated tables, and vector figures are included. Build intermediates/previews are temporary or ignored.

## Full-data reproduction after authorized access

Obtain the exact source snapshots using the manifest and access instructions in [PUBLIC_REVIEW.md](docs/PUBLIC_REVIEW.md), then follow [REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md). No undocumented local file or parent project is an acceptable substitute. A public archive for the exact recorded combine bytes is still missing; no current API response is claimed equivalent. `package.py` creates a private local bundle and may include restricted inputs; its ignored ZIP is not a rights-cleared public release.

## Research and review records

`research/` contains the scientific pipeline; root scripts provide collection, auditing, manuscript and inference entry points; `tests/` verifies methodology and safeguards. `paper/` holds the manuscript and publication assets. `output/experiments/` retains frozen results/models/logs; `reproducibility/` binds provenance and evaluation integrity; `docs/` explains the protocol, licensing/access boundary, and review findings.

[Peer review](docs/review_2026-10-13/PEER_REVIEW.md) | [Issue register](docs/review_2026-10-13/ISSUE_REGISTER.csv) | [Executed verification](docs/review_2026-10-13/VERIFICATION.md) | [Change log](docs/review_2026-10-13/CHANGELOG.md) | [Final assessment](docs/review_2026-10-13/FINAL_ASSESSMENT.md)

Historical review reports describe their dated complete local workspace. This public-repository preparation changes Git inclusion and documentation, not scientific inputs, fitted choices, predictions or the consumed receipt. Backups, retired experiments, temporary review files, duplicate outputs, environments and logs stay local and are not part of the public index. No blanket license for third-party data is asserted; see `data/licenses/` and the provider links in the public-review guide.
