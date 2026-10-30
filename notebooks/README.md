# Notebook guide

`01_download_data_started.ipynb` is the participant-facing starter. It lets participants select Altair phase, Altair Biohub_OPS0077 4i, POSH, and Aconcagua; previews sizes; downloads when explicitly enabled; and runs first-pass QC. Install dependencies using `python -m pip install -r requirements.txt` from the repository root before opening it.

`00_download_preview_and_qc.ipynb` is the administrative preview/QC entry point. For unattended VM preparation, use the documented scripts instead of an interactive notebook.

The default download also extracts the 10 `*_guide_x_screen.h5ad` profiles associated with the Biohub_OPS0077 / 4i screen from Altair's marker-profile ZIP into `data/altair/ops0077_4i/`.

`02_data_inventory_and_overlap.ipynb` inventories the repository's staged files and checks Altair phase/OPS0077 guide overlap plus candidate gene-level overlap across the available profile datasets. It is safe to run with partial downloads.
