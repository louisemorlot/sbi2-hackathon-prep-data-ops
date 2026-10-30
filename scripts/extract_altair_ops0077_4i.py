#!/usr/bin/env python3
"""Extract the screen-specific guide profiles for Altair Biohub_OPS0077 (4i)."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

EXPERIMENT_ID = "ops0144_20260406"
BIOHUB_DATASET_ID = "Biohub_OPS0077"
MARKERS = ("b-catenin", "c-myc", "gh2ax", "nfkb", "p21", "p53", "prb", "ps6", "rb", "rsp6")


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def extract_profiles(archive_path: Path, output_dir: Path, force: bool = False) -> list[dict]:
    if not archive_path.is_file():
        raise FileNotFoundError(f"Altair marker archive not found: {archive_path}")
    output_dir.mkdir(parents=True, exist_ok=True)
    extracted = []
    with zipfile.ZipFile(archive_path) as archive:
        for marker in MARKERS:
            member = f"{marker}_guide_x_screen.h5ad"
            info = archive.getinfo(member)
            target = output_dir / member
            partial = target.with_name(target.name + ".part")
            partial.unlink(missing_ok=True)
            written = 0
            with archive.open(info, "r") as source, partial.open("wb") as destination:
                while block := source.read(2 * 1024 * 1024):
                    destination.write(block)
                    written += len(block)
            if written != info.file_size:
                partial.unlink(missing_ok=True)
                raise IOError(f"Incomplete ZIP member {member}: got {written}, expected {info.file_size}")
            # Reading each ZIP member to EOF also makes zipfile validate that member's CRC.
            member_sha = digest(partial)
            same_as_existing = (target.is_file() and target.stat().st_size == written and digest(target) == member_sha)
            if same_as_existing and not force:
                partial.unlink()
                reused = True
            else:
                partial.replace(target)
                reused = False
            extracted.append({"name": member, "path": str(target), "size_bytes": written,
                              "sha256": member_sha, "reused": reused, "zip_crc_checked": True})
    return extracted


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", default="data/altair/markers_guide.zip")
    parser.add_argument("--outdir", default="data/altair/ops0077_4i")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    archive_path = Path(args.archive).expanduser().resolve()
    output_dir = Path(args.outdir).expanduser().resolve()
    profiles = extract_profiles(archive_path, output_dir, args.force)
    summary = {"biohub_dataset_id": BIOHUB_DATASET_ID, "altair_experiment_id": EXPERIMENT_ID,
               "profiles": profiles, "profile_count": len(profiles),
               "total_bytes": sum(item["size_bytes"] for item in profiles)}
    manifest = output_dir / "extraction_manifest.json"
    manifest.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"dataset": BIOHUB_DATASET_ID, "experiment": EXPERIMENT_ID,
                      "profile_count": len(profiles), "total_bytes": summary["total_bytes"],
                      "manifest": str(manifest)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
