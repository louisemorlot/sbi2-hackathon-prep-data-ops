# SBI2 hackathon data preparation

Download and stage the processed Altair, CellPaint-POSH, and Aconcagua profiles on a laptop or a shared AWS VM volume. This repository contains code and documentation only; downloaded datasets are stored under `data/` and excluded from Git.

## What the default bundle includes

- **Altair, A549:** guide-level phase profiles, small metadata files, and the guide-level marker profile archive used for phase-versus-fluorescence work.
- **CellPaint-POSH, A549:** the published 124-gene morphology profile table from Zenodo.
- **Aconcagua, HeLa:** processed interphase and mitotic aggregate H5AD profiles plus experimental metadata, feature definitions, and guide/perturbation library.

The Aconcagua OPS Explorer bucket publishes interphase and mitotic aggregate H5AD files; an `all` H5AD object was not found. The online viewer has an `all` population view, but it does not expose a stable direct file URL. Profiles are gene-level and should not be described as guide-level. The repository does not download raw images, single-cell images, or the 323 GB Aconcagua `cell_data.parquet`.

The 1.5 GB POSH `well_normalized_profiles.pq` present elsewhere in the parent workspace has no recorded source URL. The repository instead downloads the source-identified processed POSH tables from the POSH Zenodo record; see the reconciliation note in `docs/DATASETS.md`.

See [dataset inventory and sizes](docs/DATASETS.md) for source links, row level, contents, and size accounting. See [VM staging](docs/AWS_VM.md) for the shared-volume workflow.

## Quick start

Python 3.10 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Inspect current source sizes and the output plan. No files are written.
python scripts/download_data.py --preset core --data-dir ./data --dry-run

# Download after reviewing the plan.
python scripts/download_data.py --preset core --data-dir ./data

# Run first-pass integrity, schema, and overlap checks.
python scripts/run_quality_checks.py --data-dir ./data --outdir ./reports/qc
```

`core` stages files relevant to the planned analyses. `full` also stages the published POSH MoA-300 and Druggable Genome-1640 processed tables. The downloader prompts before writing unless `--yes` is supplied. Re-running it reuses complete files and checks known sizes and checksums. A SHA-256 download manifest is written after a successful run.

An entry-point notebook is available at `notebooks/00_download_preview_and_qc.ipynb`. It previews by default; set `RUN_DOWNLOAD = True` in the designated cell after reviewing the plan.

## Output layout

```text
data/
  altair/       # guide profiles, marker archive, and metadata
  posh/         # Zenodo processed profiles
  aconcagua/    # interphase/mitotic profiles and metadata
  download_manifest.json
reports/qc/     # machine-readable and human-readable QC reports
```

## Sharing and use

Do not commit downloaded data to GitHub. The POSH dataset is distributed under CC BY-NC-SA 4.0; check the original source terms and event-use permissions before redistribution. Altair and Aconcagua source pages should be cited as listed in the dataset inventory. A549/HeLa and assay differences mean that direct cross-dataset results are exploratory. QC checks confirm basic file/schema integrity and report overlap; they do not validate biology or prove guide-to-target identities.
