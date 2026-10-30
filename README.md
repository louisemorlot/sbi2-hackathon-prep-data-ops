# SBI2 Hackathon: processed imaging data starter

This repository stages processed phenotypic profiles for the SBI2 hackathon. It includes guide-level phase and fluorescence profiles from Altair, processed morphology profiles from POSH, and aggregate profiles from Aconcagua. The data are intended for participant analysis on a shared AWS VM; the scripts download only the selected processed tables and metadata, not raw microscopy images.

The starter flow is modeled on the [Cytodata hackathon prep OPS repository](https://github.com/timtreis/cytodata-hackathon-prep-ops): preview what will be fetched, download selected data, run first-pass checks, then explore profile overlap before designing an analysis.

## Start here

1. Install the Python dependencies from the repository root: `python -m pip install -r requirements.txt`.
2. Open [`notebooks/01_download_data_started.ipynb`](notebooks/01_download_data_started.ipynb). Select the datasets needed for your project, inspect the size preview, and enable the download cell when ready. In a terminal, the same downloader supports `python scripts/download_data.py --datasets altair-phase altair-4i posh aconcagua --dry-run` followed by the same command without `--dry-run`.
3. Run [`notebooks/02_data_inventory_and_overlap.ipynb`](notebooks/09_preflight_dataset_inventory_and_overlap.ipynb) to inventory staged files, inspect schemas, compare Altair phase and 4i guide identifiers, and measure candidate gene overlap. It also works with a partial download.
4. For a compact administrative integrity/schema report, run `python scripts/run_quality_checks.py --data-dir data --allow-incomplete`. The report and the downloader's `data/download_manifest.json` help the VM operator confirm what was staged.

All data files are excluded from Git. Keep the code, notebooks, and descriptive metadata in the public repository; stage the downloaded data on the VM's mounted storage. For VM setup, see [`docs/AWS_VM.md`](docs/AWS_VM.md). For exact object inventory and source byte counts, see [`docs/DATASETS.md`](docs/DATASETS.md).

## Dataset overview

The default `core` download is approximately **2.10 billion bytes (1.96 GiB) transferred**. Extracting the 10 OPS0077 guide-by-screen H5AD profiles adds about **96.3 MB (91.9 MiB)** of local files from the already-downloaded marker archive, for approximately **2.20 billion bytes (2.05 GiB) of staged content**. These are measured source sizes; the downloader checks live sizes where possible and records actual downloaded sizes and SHA-256 checksums in its manifest.

| Dataset | Screen and experimental context | Downloaded processed data | Approximate size |
|---|---|---|---:|
| **Altair phase** | A549 optical pooled CRISPR perturbation screen. Phase-contrast phenotypes are summarized per guide; screen and guide annotations accompany the profile. | `phase_guide.h5ad`, screen map, unexpressed-gene metadata | 48.0 MB (45.8 MiB) |
| **Altair Biohub_OPS0077 4i** | Altair's Biohub_OPS0077 screen maps to experiment `ops0144_20260406`. The four-dimensional imaging assay includes ten antibody marker readouts: β-catenin, c-Myc, γH2AX, NFκB, p21, p53, pRB, pS6, RB, and RPS6. | Marker archive plus ten extracted guide-by-screen H5AD profiles and marker/manifest metadata | 2.04 GB (1.90 GiB) transfer; extracted profiles 96.3 MB (91.9 MiB) |
| **POSH morphology-124** | A549 CRISPR imaging screen with processed cell-painting morphology profiles for a 124-gene subset. | Zenodo `morphology_124.pq` Parquet profile table | 4.69 MB (4.47 MiB) |
| **Aconcagua** | HeLa optical pooled CRISPR screen. Public aggregate profiles are provided separately for interphase and mitotic populations; experiment metadata, feature definitions, and the perturbation library support interpretation. | Two `aggregated_data.h5ad` files plus three metadata files | 10.9 MB profiles and 1.81 MB metadata (about 12.7 MB total) |

Altair's marker archive is large because it contains many profile and sampled-cell files. Only the ten guide-by-screen profiles for the selected Biohub_OPS0077 experiment are extracted into `data/altair/ops0077_4i/`; no extra network transfer is needed for those profiles. Individual sampled-cell files are not part of this starter bundle. Aconcagua's raw `cell_data.parquet` (about 323 GB in the inspected public inventory) and raw/image data are excluded. POSH's optional MoA-300 and Druggable Genome-1640 profile tables can be added with `--preset full`; see the inventory for sizes.

## What can be compared?

- **Altair phase versus Altair 4i:** this is the clearest guide-level integration opportunity. The prepared phase table has 4,211 distinct guides; the ten OPS0077 profiles each have 4,208. The staged quality report found 4,208 shared guides, three phase-only guides, no 4i-only guides, and no target mismatches among shared guides. Compare phenotypes by shared guide (or target after checking guide consistency). Measurements are from different assay modalities and feature spaces, so do not concatenate their columns as if they were the same measurements. The shared guide index supports cross-modal comparisons and multimodal modeling.
- **Altair and POSH:** both use A549 cells, which makes shared-target phenotype comparisons a reasonable exploratory path. POSH's library is smaller and its Parquet row semantics and identifiers should be verified before joining. Use the preflight notebook to inspect candidate fields and quantify symbol overlap; compare at shared targets only after mapping names and aggregation levels.
- **Altair/POSH and Aconcagua:** cross-atlas conservation can be explored for shared target genes, but Aconcagua uses HeLa cells while Altair and POSH use A549. Aconcagua's downloaded matrices are gene/perturbation aggregates, not guide-level profiles; the perturbation library cannot recover guide-specific phenotypes from an already aggregated profile. Treat agreement as a cross-cell-line, cross-assay hypothesis, not a direct replicate.
- **Feature overlap:** feature names and units are assay-specific. A matching feature label alone does not guarantee equivalent measurements. Normalize and compare within each dataset first, then compare target-level effects or representation similarity with assay-aware methods.

The exact overlaps depend on the particular staged files and identifier columns. `02_data_inventory_and_overlap.ipynb` reports measured overlaps from the files available in `SBI2_DATA_DIR` (or `data/` by default); it does not infer missing values or download files.

## File layout

```text
data/
  altair/
    phase_guide.h5ad
    screen_map.csv
    unexpressed_genes.csv
    markers.csv
    manifest.csv
    markers_guide.zip
    ops0077_4i/                 # ten extracted guide-by-screen H5ADs
  posh/
    morphology_124.pq
  aconcagua/
    interphase/aggregated_data.h5ad
    mitotic/aggregated_data.h5ad
    metadata/
      experimental_metadata.yaml
      feature_definitions.csv
      perturbation_library.csv
  download_manifest.json
```

The downloaded filenames and checksums are captured in `data/download_manifest.json`. The source and contents inventory, optional POSH files, and known limitations are described in [`docs/DATASETS.md`](docs/DATASETS.md). Initial 4i guide-overlap checks are documented in [`docs/OPS0077_QC.md`](docs/OPS0077_QC.md).

## Sources and experimental references

- **Altair prepared profiles and schema:** [Cytodata hackathon prep OPS](https://github.com/timtreis/cytodata-hackathon-prep-ops); the release base is listed in [`docs/DATASETS.md`](docs/DATASETS.md). Altair's `screen_map.csv` links the human-readable screen label to the experiment identifier used by the marker profiles.
- **POSH processed profiles:** [Zenodo record 17470307](https://doi.org/10.5281/zenodo.17470307) and [insitro/cp-posh](https://github.com/insitro/cp-posh). The prepared Zenodo Parquet files are the source used by this downloader. Consult the record and repository for attribution and use conditions; the source materials state CC BY-NC-SA 4.0.
- **Aconcagua profiles and metadata:** [OPS Explorer collection](https://biohub.ai/ops-explorer?collection=3b32c693-a8b6-46d2-8f42-d4511a07f2f7), [Aconcagua screen portal](https://screens.wi.mit.edu/aconcagua/), and the public object prefix documented in [`docs/DATASETS.md`](docs/DATASETS.md). The downloader retrieves the available interphase and mitotic aggregate profiles; it does not synthesize an all-population matrix.

Before redistribution, check the source records for dataset-specific attribution and license requirements. For Aconcagua object details and the current download commands, consult [`docs/DATASETS.md`](docs/DATASETS.md); for AWS disk sizing and setup, use [`docs/AWS_VM.md`](docs/AWS_VM.md).
