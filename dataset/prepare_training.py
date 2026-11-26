#!/usr/bin/env python3
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
"""Persiapan pipeline training IT Agenty — TIDAK menjalankan training.

Skrip ini hanya:
* memeriksa server proxy LLM lokal (read-only, loopback, tanpa kredensial);
* memvalidasi dan memeriksa privasi dataset;
* membagi train/val deterministik dan mengekspor format alpaca;
* menulis manifest dan laporan prasyarat training (doctor).

Training nyata dilarang di sini. Ia membutuhkan pustaka ML, bobot model dasar
berlisensi milik pemilik, GPU, dan izin tertulis. ``tom05-flash-free`` adalah
alias/proxy, bukan model yang dilatih oleh skrip ini.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dataset import builder  # noqa: E402

DATA = ROOT / "dataset" / "data" / "tom05_dataset_full.jsonl"
TRAIN = ROOT / "dataset" / "data" / "tom05_dataset_full.train.jsonl"
VAL = ROOT / "dataset" / "data" / "tom05_dataset_full.val.jsonl"
ALPACA = ROOT / "dataset" / "data" / "tom05_alpaca.jsonl"
REPORT = ROOT / "dataset" / "reports" / "training_pipeline.json"
PROXY_HEALTH = "http://127.0.0.1:8772/health"
CLI = ROOT / "dataset" / "dataset_cli.py"


def check_proxy() -> dict[str, Any]:
    """Health check proxy LLM lokal. Tidak mengirim prompt atau kredensial."""
    try:
        with urllib.request.urlopen(PROXY_HEALTH, timeout=3) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return {
            "status": "AKTIF",
            "provider": payload.get("provider", ""),
            "model": payload.get("model", ""),
            "proxied_models": payload.get("proxied_models", 0),
        }
    except Exception as exc:  # pragma: no cover - bergantung lingkungan
        return {"status": "MATI", "error": type(exc).__name__}


def export_alpaca(force: bool) -> dict[str, Any]:
    """Pakai ulang exporter resmi agen dataset."""
    command = [
        sys.executable, str(CLI), "export", str(DATA),
        "--format", "alpaca", "--out", str(ALPACA),
    ]
    proc = subprocess.run(
        command, cwd=str(ROOT), capture_output=True, text=True, timeout=120
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "ekspor gagal").strip()[:300])
    return json.loads(proc.stdout)


def prepare(force: bool = False, skip_proxy: bool = False) -> dict[str, Any]:
    """Siapkan artefak pipeline tanpa melatih model apa pun."""
    if not DATA.exists():
        raise FileNotFoundError(f"dataset tidak ditemukan: {DATA}")

    records = builder.read_jsonl(DATA)
    validation = builder.validate_records(records)
    privacy = builder.privacy_report(records)
    stats = builder.stats(records)

    if not validation.get("ok") or validation.get("errors"):
        raise ValueError("validasi dataset gagal; pipeline dihentikan")
    flagged = privacy.get("flagged", 0)
    if flagged:
        raise ValueError("dataset mengandung temuan privasi; pipeline dihentikan")

    split = builder.split_records(records)
    for path, items in ((TRAIN, split["train"]), (VAL, split["val"])):
        if force or not path.exists():
            builder.write_jsonl(items, path)

    exported = export_alpaca(force)
    proxy = {"status": "DILEWATI"} if skip_proxy else check_proxy()
    doctor = builder.doctor()

    manifest = {
        "status": "SIAP",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "perintah": "prepare_training",
        "performs_training": False,
        "dataset": str(DATA.relative_to(ROOT)),
        "records": len(records),
        "validation": validation,
        "privacy": privacy,
        "stats": stats,
        "split": {
            "seed": 42,
            "val_frac": 0.2,
            "train": len(split["train"]),
            "val": len(split["val"]),
            "train_file": str(TRAIN.relative_to(ROOT)),
            "val_file": str(VAL.relative_to(ROOT)),
        },
        "alpaca": {
            "file": str(ALPACA.relative_to(ROOT)),
            "records": exported.get("count", len(records)),
        },
        "proxy": proxy,
        "prasyarat_training": doctor,
        "catatan": (
            "Ini persiapan data, bukan training. tom05-flash-free tetap alias/proxy. "
            "Training nyata hanya dengan pustaka ML, bobot model dasar berlisensi "
            "milik pemilik, GPU, dan izin tertulis."
        ),
        "trained": False,
        "license": builder.LICENSE,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    builder.audit("pipeline-prepare", {
        "records": len(records),
        "train": len(split["train"]),
        "val": len(split["val"]),
        "proxy": proxy.get("status"),
        "training_siap": doctor.get("training_siap"),
    })
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="timpa artefak split")
    parser.add_argument("--no-proxy", action="store_true", help="lewatkan health check")
    args = parser.parse_args()
    manifest = prepare(force=args.force, skip_proxy=args.no_proxy)
    print(json.dumps({
        "status": manifest["status"],
        "records": manifest["records"],
        "train": manifest["split"]["train"],
        "val": manifest["split"]["val"],
        "proxy": manifest["proxy"]["status"],
        "training_siap": manifest["prasyarat_training"]["training_siap"],
        "performs_training": manifest["performs_training"],
        "report": str(REPORT.relative_to(ROOT)),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
