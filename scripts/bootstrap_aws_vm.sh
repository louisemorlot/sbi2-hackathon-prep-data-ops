#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
DATA_DIR="${DATA_DIR:-/mnt/hackathon-data}"
PRESET="${PRESET:-core}"
DOWNLOAD_DATA="${DOWNLOAD_DATA:-0}"

cd "$ROOT"
"$PYTHON_BIN" -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/download_data.py --preset "$PRESET" --data-dir "$DATA_DIR" --dry-run

if [[ "$DOWNLOAD_DATA" == "1" ]]; then
  python scripts/download_data.py --preset "$PRESET" --data-dir "$DATA_DIR" --yes
  python scripts/run_quality_checks.py --data-dir "$DATA_DIR" --outdir "$DATA_DIR/qc"
else
  echo "Dry run complete. Review the object sizes, mount the intended EBS volume, then rerun with DOWNLOAD_DATA=1."
fi
