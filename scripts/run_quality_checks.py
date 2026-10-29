#!/usr/bin/env python3
"""Check staged file integrity, schemas, metadata coverage, and tentative gene overlap."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import re
import zipfile

GENE_FIELDS = ("gene_symbol", "target_gene", "gene_name", "target", "gene")
GUIDE_FIELDS = ("barcode", "guide_id", "guide_sequence", "sgrna", "sgRNA", "protospacer_sequence")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def normalize(values) -> set[str]:
    out = set()
    for value in values:
        if value is None:
            continue
        text = str(value).strip().upper()
        if text and text not in {"NAN", "NONE", "NULL"}:
            out.add(text)
    return out


def best_gene_field(frame, known_genes: set[str] | None = None):
    candidates = [c for c in frame.columns if str(c).lower() in {x.lower() for x in GENE_FIELDS}]
    if known_genes:
        candidates += [c for c in frame.columns if str(c).lower() in {"aggregate_id", "gene_id"}]
        scored = []
        for col in dict.fromkeys(candidates):
            values = normalize(frame[col].dropna().astype(str).head(50000))
            scored.append((len(values & known_genes), col))
        if scored:
            score, col = max(scored)
            if score:
                return col, score
    return (candidates[0], None) if candidates else (None, None)


def inspect_h5ad(path: Path, known_genes: set[str] | None = None) -> dict:
    import anndata as ad
    data = ad.read_h5ad(path, backed="r")
    obs = data.obs
    gene_field, matched = best_gene_field(obs, known_genes)
    genes = normalize(obs[gene_field].dropna()) if gene_field else set()
    result = {"format": "H5AD", "observations": int(data.n_obs), "features": int(data.n_vars),
              "obs_columns": list(map(str, obs.columns)), "var_columns": list(map(str, data.var.columns)),
              "gene_field": str(gene_field) if gene_field is not None else None,
              "unique_gene_labels": len(genes) if gene_field else None,
              "gene_labels_matching_library": matched,
              "duplicate_observation_names": int(obs.index.duplicated().sum()),
              "duplicate_feature_names": int(data.var.index.duplicated().sum())}
    data.file.close()
    if genes:
        result["_gene_symbols"] = sorted(genes)
    return result


def inspect_parquet(path: Path, known_genes: set[str] | None = None) -> dict:
    import pyarrow.parquet as pq
    parquet = pq.ParquetFile(path)
    names = parquet.schema.names
    result = {"format": "Parquet", "rows": parquet.metadata.num_rows,
              "columns": len(names), "row_groups": parquet.metadata.num_row_groups,
              "column_names": names}
    lookup = {name.lower(): name for name in names}
    gene_col = next((lookup[x] for x in GENE_FIELDS if x in lookup), None)
    guide_col = next((lookup[x.lower()] for x in GUIDE_FIELDS if x.lower() in lookup), None)
    result["gene_field"] = gene_col
    result["guide_field"] = guide_col
    if gene_col:
        sample = parquet.read_row_group(0, columns=[gene_col]).to_pandas()[gene_col]
        genes = normalize(sample.dropna())
        result["sample_unique_gene_labels"] = len(genes)
        if known_genes:
            result["sample_gene_labels_matching_library"] = len(genes & known_genes)
            if genes:
                result["_gene_symbols"] = sorted(genes)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--outdir", help="Defaults to <data-dir>/qc")
    args = parser.parse_args()
    root = Path(args.data_dir).expanduser().resolve()
    out = Path(args.outdir).expanduser().resolve() if args.outdir else root / "qc"
    report = {"created_utc": datetime.now(timezone.utc).isoformat(), "data_dir": str(root), "files": [],
              "gene_overlap": {}, "limits": [
                  "Integrity and schema checks do not validate biological correctness or prove guide-to-target assignments.",
                  "Aconcagua is HeLa; Altair and POSH are A549. Cross-dataset agreement remains exploratory.",
                  "Aconcagua profiles are gene/perturbation aggregates and cannot be converted to guide-level profiles from the library map alone."]}

    library = root / "aconcagua" / "metadata" / "perturbation_library.csv"
    known_genes = set()
    if library.exists():
        import pandas as pd
        lib = pd.read_csv(library, low_memory=False)
        gene_col = next((c for c in lib.columns if str(c).lower() == "gene_symbol"), None)
        if gene_col:
            known_genes = normalize(lib[gene_col].dropna())
            report["aconcagua_library"] = {"rows": len(lib), "unique_gene_symbols": len(known_genes),
                                             "columns": list(map(str, lib.columns))}

    files = sorted(p for p in root.rglob("*") if p.is_file() and ".part" not in p.name and "qc" not in p.parts)
    expected_core = [
        "altair/phase_guide.h5ad", "altair/markers_guide.zip", "altair/screen_map.csv",
        "altair/unexpressed_genes.csv", "altair/markers.csv", "altair/manifest.csv",
        "posh/morphology_124.pq", "aconcagua/interphase_aggregated_data.h5ad",
        "aconcagua/mitotic_aggregated_data.h5ad", "aconcagua/metadata/experimental_metadata.yaml",
        "aconcagua/metadata/feature_definitions.csv", "aconcagua/metadata/perturbation_library.csv",
    ]
    report["missing_core_files"] = [relative for relative in expected_core if not (root / relative).is_file()]
    gene_sets: dict[str, set[str]] = {}
    for path in files:
        rel = str(path.relative_to(root))
        item = {"path": rel, "exists": True, "size_bytes": path.stat().st_size, "sha256": digest(path)}
        try:
            if path.suffix == ".h5ad":
                item.update(inspect_h5ad(path, known_genes or None))
            elif path.suffix == ".pq" or path.suffix == ".parquet":
                item.update(inspect_parquet(path, known_genes or None))
            elif path.suffix.lower() == ".zip":
                with zipfile.ZipFile(path) as archive:
                    members = [m for m in archive.infolist() if not m.is_dir()]
                    item.update({"format": "ZIP", "members": len(members),
                                 "h5ad_members": sum(m.filename.lower().endswith(".h5ad") for m in members),
                                 "uncompressed_bytes": sum(m.file_size for m in members),
                                 "crc_test": "not run (use unzip -t for full archive check)"})
            elif path.suffix.lower() == ".csv":
                import pandas as pd
                head = pd.read_csv(path, nrows=5)
                item.update({"format": "CSV", "columns": list(map(str, head.columns))})
            elif path.suffix.lower() in {".yaml", ".yml"}:
                item["format"] = "YAML"
            if "_gene_symbols" in item:
                gene_sets[rel] = set(item.pop("_gene_symbols"))
            if item.get("size_bytes", 0) == 0:
                item["error"] = "empty file"
        except Exception as exc:
            item["error"] = f"{type(exc).__name__}: {exc}"
        report["files"].append(item)

    labels = list(gene_sets)
    for i, left in enumerate(labels):
        for right in labels[i + 1:]:
            shared = sorted(gene_sets[left] & gene_sets[right])
            report["gene_overlap"][f"{left} vs {right}"] = {"shared_count": len(shared), "examples": shared[:50]}

    out.mkdir(parents=True, exist_ok=True)
    report_path = out / "quality_report.json"
    report_path.write_text(json.dumps(report, indent=2, default=str) + "\n")
    total = sum(x["size_bytes"] for x in report["files"])
    errors = sum("error" in x for x in report["files"])
    print(json.dumps({"report": str(report_path), "files_found": len(report["files"]),
                      "total_bytes": total, "inspection_errors": errors,
                      "missing_core_files": report["missing_core_files"],
                      "gene_overlap_pairs": len(report["gene_overlap"])}, indent=2))
    return 1 if errors or report["missing_core_files"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
