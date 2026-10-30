# Biohub_OPS0077 / 4i download and first-pass QC

Checked 2026-10-30 using the Altair prepared release and the already staged Altair phase guide profile.

## Download path and size

Altair's `screen_map.csv` maps Biohub dataset `Biohub_OPS0077` to experiment `ops0144_20260406` with `match=marker_identity`. The individual guide-profile H5AD files are members of `markers_guide.zip`; a guessed standalone profile URL returned 403. The targeted downloader therefore retrieves the archive and extracts the relevant entries.

The actual OPS0077-only download completed and matched the release manifest:

- `markers_guide.zip`: 2,037,832,363 bytes (1.90 GiB), SHA-256 `8a7257138d26c2dfec7414c17ef9f3fee27f64e6b1f7178a957ea78c24311930`.
- Extracted guide-by-screen files: 10 H5AD profiles, 96,314,183 bytes total (91.85 MiB).
- Each selected ZIP member was read fully and passed the ZIP CRC check; the individual file SHA-256 values are recorded in the runtime download manifest.

The marker inventory lists ten readouts for this experiment: b-catenin, c-myc, γH2AX, NFκB, p21, p53, pRB, pS6, RB, and RPS6. The processed guide profiles are small. The separate sampled cell-level marker files are approximately 1.2–1.6 GB each and are not included in this subset.

## Profile checks

All ten extracted H5AD files opened successfully with AnnData and report `experiment=ops0144_20260406`. Each profile contains 4,208 observations (unique guide records), with no duplicate observation or feature names. b-catenin and c-myc have 436 features each; the other eight profiles have 657 features each. Profiles are marked fluorescent and use channels named `4i_r4_<marker>`.

Compared with the prepared Altair phase profile:

- Phase profile: 4,211 unique guides.
- Each 4i marker profile: 4,208 unique guides.
- Shared: 4,208 guide IDs per marker; three guides occur in phase only, and none occur only in this 4i screen.
- Shared guide IDs have no target-gene disagreements, and neither profile has internal guide-to-target conflicts.

This supports guide-level phase-versus-fluorescence comparisons for the overlapping perturbations. These checks establish file integrity, schema readability, screen identity, and internal mapping consistency; they do not independently prove the original guide library annotation or biological validity.

The reusable checks are in `scripts/extract_altair_ops0077_4i.py` and `scripts/run_quality_checks.py`. Runtime outputs are written under `data/download_manifest.json`, `data/altair/ops0077_4i/extraction_manifest.json`, and `reports/ops0077_4i_qc/quality_report.json`; downloaded data and reports are ignored by Git.
