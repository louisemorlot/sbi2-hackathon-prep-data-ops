# Staging on an AWS VM

Use a persistent EBS volume mounted at `/mnt/hackathon-data` (or another approved shared data path). The repo itself can live on the VM root volume; the dataset payloads and QC reports should live on the mounted data volume.

```bash
git clone <your-github-url> sbi2-hackathon-prep-data-ops
cd sbi2-hackathon-prep-data-ops

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python scripts/download_data.py --preset core --data-dir /mnt/hackathon-data --dry-run
python scripts/download_data.py --preset core --data-dir /mnt/hackathon-data
python scripts/run_quality_checks.py --data-dir /mnt/hackathon-data --outdir /mnt/hackathon-data/reports/qc
```

The default run is interactive and asks before downloading. For an already-reviewed provisioning job, `--yes` skips that prompt. The shell helper `scripts/bootstrap_aws_vm.sh` creates a virtual environment, prints a size plan, and downloads only when `DOWNLOAD_DATA=1` is set. It never formats or mounts storage; attach and mount the correct EBS volume before running it.

Outbound HTTPS access is required. Downloads use public endpoints; AWS credentials are not required for the selected objects. The VM should have at least 5 GB free for the core bundle plus temporary download files and QC outputs; more free space is needed if the POSH full preset is selected. Keep `/mnt/hackathon-data` outside the Git checkout and consider read-only participant access after QC completes.
