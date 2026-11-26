#!/usr/bin/env python3
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengalihan model otomatis saat error — terbatas, deterministik, diaudit.

Fitur ini HANYA memilih model gratis lain dari katalog lokal yang sudah ada
(``config/hy4-free-models.json``). Ini bukan otorisasi baru, bukan izin tanpa
batas, dan bukan aksi jaringan: tidak ada kredensial yang dibaca/disimpan,
tidak ada lisensi/izin yang diubah, tidak ada target di luar katalog yang
dipilih. Setiap peristiwa dicatat ke ``security/reports/model_fallback.jsonl``.

Batasan keras (sesuai surat persetujuan otomatis & hy4_manager):

* kandidat harus ``status == "active"`` dan berada di katalog;
* maksimal ``MAX_ATTEMPTS`` pergantian per permintaan;
* model yang sama tidak dipilih dua kali berturut-turut;
* ``mode`` dan identitas agen tidak diubah — hanya ID model.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "config" / "hy4-free-models.json"
AUDIT = ROOT / "security" / "reports" / "model_fallback.jsonl"
MAX_ATTEMPTS = 3
ALLOWED_SCOPES = (
    "command", "chip", "cli", "model", "opencode", "clone", "supervisor",
)


def _load_models(catalog: Path = CATALOG) -> list[str]:
    """Kembalikan ID model aktif dari katalog, urut deterministik."""
    try:
        data = json.loads(catalog.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return sorted(
        item["id"]
        for item in data.get("models", [])
        if item.get("status") == "active" and item.get("id")
    )


def candidates(exclude: tuple[str, ...] = (), catalog: Path = CATALOG) -> list[str]:
    """Daftar kandidat model gratis yang boleh dipakai sebagai pengganti."""
    excluded = set(exclude)
    return [model for model in _load_models(catalog) if model not in excluded]


def choose(
    failed_model: str,
    *,
    scope: str = "model",
    attempts: int = 0,
    catalog: Path = CATALOG,
    audit: Path = AUDIT,
) -> dict[str, Any]:
    """Pilih satu model pengganti bila error, dalam batas yang ditentukan.

    Tidak pernah melempar exception untuk katalog rusak — mengembalikan
    ``status: GAGAL`` dengan alasan, tetap diaudit.
    """
    record: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "failed_model": failed_model,
        "scope": scope,
        "attempts": attempts,
        "license": "Tom05ivier-commits-1.0",
        "fabrication": "NOT_APPLICABLE",
    }
    if scope not in ALLOWED_SCOPES:
        record.update(status="DITOLAK", reason="Scope tidak dikenal.")
    elif attempts >= MAX_ATTEMPTS:
        record.update(status="DITOLAK", reason="Batas percobaan pergantian terlampaui.")
    else:
        pool = candidates(exclude=(failed_model,), catalog=catalog)
        if not pool:
            record.update(status="GAGAL", reason="Tidak ada kandidat aktif di katalog.")
        else:
            record.update(
                status="OK",
                selected=pool[0],
                alternatives=pool[1:4],
                reason="Model pengganti dipilih dari katalog gratis, terbatas & diaudit.",
            )

    audit.parent.mkdir(parents=True, exist_ok=True)
    with audit.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def apply(
    failed_model: str,
    *,
    scope: str = "model",
    attempts: int = 0,
    config: Path | None = None,
    catalog: Path = CATALOG,
    audit: Path = AUDIT,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Terapkan penggantian model ke konfigurasi OpenCode bila diizinkan.

    Hanya model yang lolos ``choose()`` (berasal dari katalog) yang ditulis.
    Backup dibuat sebelum perubahan, dan hasil tetap diaudit. Kredensial tidak
    pernah disentuh. ``dry_run`` tidak menulis apa pun.
    """
    decision = choose(failed_model, scope=scope, attempts=attempts,
                      catalog=catalog, audit=audit)
    if decision.get("status") != "OK":
        return {**decision, "applied": False, "reason_write": "Pemilihan tidak disetujui."}

    target = config or (ROOT.parent / ".config" / "opencode" / "opencode.json")
    # Pakai konfigurasi OpenCode absolut yang dikenal hy4_manager bila ada.
    known = Path("/root/.config/opencode/opencode.json")
    if config is None and known.exists():
        target = known
    selected = decision["selected"]
    if selected not in candidates(catalog=catalog):
        return {**decision, "applied": False, "reason_write": "Model tidak ada di katalog."}

    if dry_run:
        return {**decision, "applied": False, "dry_run": True,
                "would_write": str(target), "model": selected}

    data: dict[str, Any] = {}
    if target.exists():
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
    backup = target.with_suffix(".json.model-fallback-backup")
    if target.exists() and not backup.exists():
        backup.write_bytes(target.read_bytes())
    previous = data.get("model")
    data["model"] = selected
    data.setdefault("$schema", "https://opencode.ai/config.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    record = {**decision, "applied": True, "previous": previous,
              "model": selected, "config": str(target),
              "backup": str(backup) if backup.exists() else None}
    audit.parent.mkdir(parents=True, exist_ok=True)
    with audit.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"timestamp": record["timestamp"],
                                 "action": "apply_model",
                                 "previous": previous, "model": selected,
                                 "scope": scope, "config": str(target),
                                 "license": "Tom05ivier-commits-1.0"},
                                ensure_ascii=False) + "\n")
    return record


def history(limit: int = 10, audit: Path = AUDIT) -> list[dict[str, Any]]:
    """Baca jejak audit pengalihan model (tanpa nilai sensitif)."""
    if not audit.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in audit.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records[-limit:]


def _relative(path: Path) -> str:
    """Path relatif terhadap workspace, aman untuk path di luar root."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def status(catalog: Path = CATALOG, audit: Path = AUDIT) -> dict[str, Any]:
    """Ringkasan keadaan fitur pengalihan model."""
    pool = _load_models(catalog)
    return {
        "katalog": _relative(catalog),
        "model_aktif": len(pool),
        "maks_percobaan": MAX_ATTEMPTS,
        "scopes": list(ALLOWED_SCOPES),
        "audit": _relative(audit),
        "riwayat": len(history(audit=audit)),
        "catatan": "Hanya katalog gratis; tanpa jaringan, kredensial, atau perubahan lisensi.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="model_fallback.py", description=__doc__)
    parser.add_argument("command", choices=("status", "choose", "apply", "history"))
    parser.add_argument("--dry-run", action="store_true", help="apply: hanya simulasi")
    parser.add_argument("--config", type=Path, default=None, help="apply: path opencode.json")
    parser.add_argument("--failed", default="opencode/glm-5.3-flash")
    parser.add_argument("--scope", default="model", choices=ALLOWED_SCOPES)
    parser.add_argument("--attempts", type=int, default=0)
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args(argv)

    if args.command == "status":
        print(json.dumps(status(), indent=2, ensure_ascii=False))
    elif args.command == "history":
        print(json.dumps(history(args.limit), indent=2, ensure_ascii=False))
    elif args.command == "apply":
        print(json.dumps(apply(args.failed, scope=args.scope, attempts=args.attempts,
                               config=args.config, dry_run=args.dry_run),
                         indent=2, ensure_ascii=False))
    else:
        print(json.dumps(choose(args.failed, scope=args.scope, attempts=args.attempts),
                         indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
