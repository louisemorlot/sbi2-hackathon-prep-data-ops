# Dataset inventory, contents, and sizes

Object sizes below are source object sizes observed on 2026-10-29 where available. The downloader queries current HTTP/S3 sizes at run time and records actual downloaded sizes and SHA-256 values in `data/download_manifest.json`. Some small Altair CSV endpoints do not return a `Content-Length` header; those sizes are determined from the completed download.

## Default `core` bundle

| Dataset | File(s) | Contents / unit | Source size | Download destination |
|---|---|---|---:|---|
| Altair | `phase_guide.h5ad` | A549 phase-imaging profile, guide-level; metadata and feature matrix | 47,992,569 B (45.8 MiB) | `altair/` |
| Altair | `markers_guide.zip` | Guide-level fluorescence marker profiles and guide-by-screen profiles for marker assays | 2,037,832,363 B (1.90 GiB) | `altair/` |
| Altair metadata | `screen_map.csv`, `unexpressed_genes.csv`, `markers.csv`, `manifest.csv` | Screen IDs, expression context, marker inventory, prepared-release file manifest | Small; queried/download-measured at run time | `altair/` |
| POSH | `morphology_124.pq` | Published processed 124-gene CRISPR KO morphology profile table; no imagery | 4,686,984 B (4.47 MiB) | `posh/` |
| Aconcagua | `interphase/aggregated_data.h5ad` | HeLa aggregate feature profiles, interphase population | 5,428,564 B (5.18 MiB) | `aconcagua/` |
| Aconcagua | `mitotic/aggregated_data.h5ad` | HeLa aggregate feature profiles, mitotic population | 5,423,724 B (5.17 MiB) | `aconcagua/` |
| Aconcagua metadata | `experimental_metadata.yaml`, `feature_definitions.csv`, `perturbation_library.csv` | Experiment description, feature names/definitions, guide and target library | 1,809,436 B combined (1.73 MiB) | `aconcagua/metadata/` |

The Aconcagua perturbation library contains 20,445 records and 5,299 distinct gene symbols in the copy already inspected for this project. It includes both targeting and control guides.

Known-size total for core is about **2,103,173,640 bytes (1.96 GiB)**, plus small Altair metadata CSVs. Exact sizes vary if source files are updated.

## Optional files in `full`

| Dataset | File | Contents / unit | Source size |
|---|---|---|---:|
| POSH | `moa_300.pq` | Processed 300-gene MoA screen profile table | 31,421,848 B (29.97 MiB) |
| POSH | `druggable_genome_1640.pq` | Processed 1,640-gene screen profile table | 54,547,608 B (52.02 MiB) |

## Source locations

- **Altair prepared profiles and metadata:** [Cytodata hackathon prep OPS release](https://exampledata.scverse.org/sbi2-cytodata/ops/) and its schema/guide at [cytodata-hackathon-prep-ops](https://github.com/timtreis/cytodata-hackathon-prep-ops). The marker ZIP is optional in analyses that do not need fluorescence; it is included in `core` for the phase-versus-fluorescence workstream.
- **POSH:** [Zenodo record 17470307](https://doi.org/10.5281/zenodo.17470307) and [insitro/cp-posh](https://github.com/insitro/cp-posh). The Zenodo record provides the processed Parquet tables and is a more stable source for this repo than an S3 aggregate key that currently returned 404. Do not confuse these small processed profiles with the much larger POSH single-cell/tile imagery in the S3 bucket.
- **Aconcagua:** public bucket prefix `s3://ops-explorer-public/aconcagua/aconcagua/`; exact profile keys are under `visualizations/{interphase,mitotic}/aggregated_data.h5ad`; metadata is under `metadata/`. The [OPS Explorer collection](https://biohub.ai/ops-explorer?collection=3b32c693-a8b6-46d2-8f42-d4511a07f2f7) also describes the collection. The portal is [screens.wi.mit.edu/aconcagua](https://screens.wi.mit.edu/aconcagua/).

## Contents and analysis limits

- Altair phase/marker prepared tables are guide-level and include screen and target metadata. Marker archive contents include profile-level tables; it is not an image archive.
- POSH Zenodo profiles are processed numeric profiles. Inspect the Parquet schema and library identifiers with `run_quality_checks.py` before treating their rows as guide-level or assuming their target column is a gene symbol.
- Aconcagua `aggregated_data.h5ad` is a gene/perturbation aggregate representation, not one row per guide. `perturbation_library.csv` maps target symbols to guide/barcode records, but this mapping cannot split an already gene-aggregated profile back into guide-specific profiles.
- The Aconcagua portal exposes an `all` population in its interactive interface. No `all/aggregated_data.h5ad` was present at the public OPS Explorer prefix when checked. This repo therefore downloads both available public split profiles (interphase and mitotic); it does not construct an `all` profile by averaging them.
- Aconcagua raw cell data (`cell_data.parquet`, observed at 323,471,309,291 B) and image/Zarr content are intentionally excluded from `core` and `full`.
- POSH is CC BY-NC-SA 4.0 according to its source materials. Confirm the applicable terms for the hackathon and any later data redistribution. Keep data files out of GitHub.

### Previously staged POSH preflight files

The parent workspace contains `well_normalized_profiles.pq` (about 1.5 GB) and `124_gene_library.csv`. Their original download URL/source manifest is not recorded in the files available here, so the new downloader does not silently claim to reproduce them. Direct requests to the previously documented POSH S3 profile keys returned 404 during preparation. This repository uses the smaller, source-identified POSH Parquet files in the Zenodo record. If the 1.5 GB local profile is required for a particular analysis, transfer it separately and record its original source and checksum in the VM's `download_manifest.json` before distribution.
