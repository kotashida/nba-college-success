# Reproducing the Research

## Public repository scope (current)

Read [PUBLIC_REVIEW.md](PUBLIC_REVIEW.md) first. The repository now retains frozen models, predictions, scores and trial logs; the older statement below that all large outputs are excluded describes the prior local-bundle arrangement. Source snapshots and wholesale processed copies still remain outside Git because the author confirmed no verified redistribution permissions.

Use `python verify_results.py` for repository-only verification of published metrics and intervals. It deliberately reads no excluded provider input. The full-data commands below require the exact licensed source files listed in the included manifests. The undated combine snapshot has no persistent exact public download, so complete raw-data/model reproduction cannot presently be accomplished using a public clone alone. This limitation is explicit, not a dependency on an undocumented local file. The private ZIP and raw external-source audit caches are not public release artifacts.


## October 13 verification additions

The [executed-check report](review_2026-10-13/VERIFICATION.md) distinguishes this review from prior audit claims. Use the recorded Windows Python 3.12.4 environment and exact lockfile. All 44 listed versions were checked locally and `pip check` passed; a fresh online installation, Python 3.11, and Linux/macOS were not tested. The lock reflects Windows dependency resolution and does not pin platform-specific dependencies such as Linux CUDA/NCCL additions.

```sh
python review_evidence.py
python audit_research.py
python verify_review.py
python docs/review_2026-10-13/verify_methods.py
python audit_external_sources.py
python -m pytest -q
python train_final.py
python smoke_inference.py
python run.py report
python run.py paper
python package.py
```

`review_evidence.py` checks a dated retrospective seal covering 203 unchanged inputs, scientific modules, frozen models, evaluation records, development logs, and splits. The original freeze and receipt are not rewritten. `verify_review.py` independently rejects missing or duplicate player/model/cohort records, checks candidate/finalist coverage, temporal sizes, versioned evidence agreement, and installed dependency versions. The methods replay is a separate numerical and ascertainment check. `audit_external_sources.py` reads cached post-evaluation ESPN evidence by default; `--fetch` only retrieves missing responses into its separate audit folder and requires network access. A missing endpoint does not prove a zero outcome.

`train_final.py` refits fixed specifications for forward research use and seals saved forward artifacts. It creates no new accuracy result. `predict.py` rejects invalid dates, blank names, absent hash metadata, and mismatched model artifacts. Data-dependent tests explicitly skip missing snapshots instead of silently reporting a pass. Full checks require the bundle.

The private original backup covers all readable files; ten legacy OneDrive placeholders could not be hydrated and are recorded in its manifest and the retrospective seal. They are not active inputs. `package.py` excludes backups, legacy history, temporary previews, environments, and caches; these remain preserved locally. A fresh replication without publication amendments can now be packaged. Preserve the recorded experiment in its own directory; a new from-scratch experiment is separate replication evidence and must not overwrite this seal or consumed receipt.

## Manuscript

Install `requirements-lock.txt` under Python 3.12 (the recorded interpreter is 3.12.4) and a LaTeX distribution providing `pdflatex`. Set `PDFLATEX` to an absolute executable path if necessary. Edit `paper/five_year_nba_outcomes.tex`, then run `python run.py paper`. The only publication PDF is `paper/five_year_nba_outcomes.pdf`. Compilation and page rendering use a temporary directory that is removed after the build; the layout summary is retained at `output/audit/paper_layout_checks.json`. For visual inspection, Python callers can pass a `preview_dir` to `research.report.compile_paper` to retain PNG previews explicitly.

## Recorded Experiments

Git excludes large snapshots, processed datasets, fitted models, and generated experiment outputs. Exact numerical reproduction requires the recorded `data/` and `output/` directories, not merely a Git clone. `python package.py` creates `output/nba_college_success.zip` from a complete local workspace, including these inputs and artifacts but excluding archives, environments, and caches. Bundle contents use the repository layout; extract them before running the commands below. No hosted release is assumed to exist.

```sh
python collect.py
python run.py data
python verify_sources.py
python run.py verify
python run.py all
```

Collection verifies existing snapshots and retrieves missing public sources. Repository sources are commit-pinned, but mutable ESPN responses may differ from recorded hashes; those responses are rejected. Restore the original bundle rather than replacing recorded provenance. The undated combine snapshot must also be restored from the bundle. Third-party data rights remain with their providers; the bundled source-license notice is in `data/licenses/` and does not grant blanket redistribution rights.

`all` rebuilds deterministic data, retains an existing freeze and consumed evaluation receipt, regenerates tables and figures, compiles the paper, and independently refits ten selected models. The original final-test predictions must not be used to select a new winner. For an independent from-scratch replication, use an empty experiment-output directory with the recorded snapshots and configuration; `python run.py develop` then `python run.py evaluate` executes the specified experiment. Independently trained artifacts can differ across package versions, platforms, or thread implementations and are not replacements for the recorded receipt.

`reproducibility/` contains small, versioned copies of the configuration freeze, test receipt, temporal splits, and publication-integrity records. Runtime originals remain under `output/experiments/`, where their exact bytes are checked along with data, models, predictions, scores, and scientific code. Publication and input-access corrections are explicitly recorded; preserved source snapshots support integrity checks. `register_integrity.py` refuses scientific experiment changes outside the integrity-check routine. It is not permission to modify features, fitting, targets, or model selection after evaluation.

## Tests and Inference

Run `python -m pytest -q`. Checks cover identity and traded-season handling, the fixed target window, maturity-gap folds, training-only preprocessing, and evaluation integrity. `python train_final.py` refits frozen choices on mature labels without retuning. `python predict.py INPUT.csv OUTPUT.csv` scores canonical pre-draft features; `python smoke_inference.py` checks the interface with a clearly synthetic record. Forward refits have no new out-of-sample accuracy claim.

## Independent Audit

Run `python audit_research.py` with the recorded bundle restored. This reconstructs all 3,315 target fields directly from raw NBA rows, recalculates 195 final-test and 90 nested metric rows, checks all 130 stored model/cohort prediction groups, reproduces the five paired bootstrap summaries, and checks final selection against the development logs. It writes `output/audit/verification.json` and refuses to change protected evaluation artifacts. The versioned audit evidence copy is `reproducibility/audit_verification.json`. It does not tune, select a test winner, or replace any recorded score. `python run.py verify` separately refits the ten selected target/year models. Together these verify numerical consistency with the recorded snapshots, not independent provider accuracy.

The integrity guard now checks all four receipt-bound artifacts before retaining an evaluation or generating reports, and rejects evaluation artifacts without a receipt. This correction is registered as an integrity-only amendment; the original scientific routines, freeze, predictions, scores, and test receipt are preserved. The 2018--2019 cohorts were consumed by an earlier project reconstruction and are retrospective diagnostics in this paper. The local 2020--2021 freeze is not evidence of public preregistration or proof of no prior human exposure to historical outcomes.
