# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Agen CLI dataset IT Agenty — antarmuka baris perintah.

Ini adalah alat **persiapan dan validasi data**, bukan pelatihan model.
Lihat ``dataset/dataset_agent.py`` untuk definisi peran dan batasnya.
Keluaran selalu JSON; kode keluar: 0 = berhasil, 1 = gagal, 2 = salah pakai.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dataset import builder  # noqa: E402
from dataset.dataset_agent import describe  # noqa: E402

LICENSE = "Tom05ivier-commits-1.0"


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _resolve_out(raw: str | None, default: Path) -> Path:
    path = Path(raw) if raw else default
    return path if path.is_absolute() else ROOT / path


def _load(path: Path) -> list[dict[str, Any]]:
    return builder.read_jsonl(path)


def _input_path(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else ROOT / path


def _path_arg(args: argparse.Namespace) -> Path:
    """Terima path posisional kanonik maupun alias ``--out`` (kompatibilitas)."""
    raw = getattr(args, "path", None) or getattr(args, "out", None)
    if not raw:
        raise ValueError("path dataset diperlukan (posisional atau --out)")
    return _input_path(raw)


def _drop_flagged(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Buang rekord yang masih memuat kredensial; kembalikan (bersih, dibuang)."""
    return builder.drop_flagged(records)


def _persist(
    records: list[dict[str, Any]],
    out: Path,
    command: str,
    *,
    force: bool = False,
    audit_detail: dict[str, Any] | None = None,
    extra: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], int]:
    """Saring, validasi, lalu tulis JSONL; tidak pernah menimpa tanpa ``--force``."""
    clean, dropped = _drop_flagged(records)
    validation = builder.validate_records(clean)
    if not validation["ok"]:
        payload = {
            "status": "FAIL", "perintah": command,
            "errors": validation["errors"], "dropped": dropped,
            "trained": False, "license": LICENSE,
        }
        builder.audit(command, {"status": "FAIL", "out": str(out),
                                "errors": len(validation["errors"])})
        return payload, 1
    if out.exists() and not force:
        payload = {
            "status": "GAGAL", "perintah": command,
            "error": "berkas sudah ada; gunakan --force untuk menimpa",
            "out": str(out), "license": LICENSE,
        }
        builder.audit(command, {"status": "GAGAL", "alasan": "sudah ada", "out": str(out)})
        return payload, 1
    written = builder.write_jsonl(clean, out)
    payload: dict[str, Any] = {
        "status": "OK", "perintah": command, "count": written,
        "dropped": dropped, "out": str(out),
        "trained": False, "license": LICENSE,
    }
    if extra:
        payload.update(extra)
    detail = {"status": "OK", "out": str(out), "count": written, "dropped": dropped}
    detail.update(audit_detail or {})
    builder.audit(command, detail)
    return payload, 0


def cmd_agent(_args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    payload = describe()
    payload["status"] = "OK"
    # Penegasan eksplisit: agen ini bukan model neural dan tidak melatih.
    payload["trained"] = False
    return payload, 0


def cmd_doctor(_args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    payload = builder.doctor()
    payload["status"] = "OK"
    return payload, 0


def cmd_template(_args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    example = {
        "id": "<sha256-16-hex>",
        "instruction": "Apa itu agen dataset IT Agenty?",
        "response": (
            "Agen dataset menyiapkan dan memvalidasi pasangan instruksi→jawaban "
            "dari dokumen workspace milik IT Agenty, lengkap dengan sumber dan "
            "penanda trained: false."
        ),
        "source": "manual",
        "license": LICENSE,
        "kind": builder.KIND,
        "trained": False,
    }
    return {
        "status": "TEMPLATE",
        "format": "satu objek JSON per baris (JSONL)",
        "contoh": example,
        "catatan": (
            "Field wajib: id, instruction, response, source, license, kind, "
            "trained. Jangan isi trained dengan true."
        ),
    }, 0


def cmd_build(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    records = builder.build_dataset(ROOT, sources=args.source, limit=args.limit)
    clean, dropped = _drop_flagged(records)
    validation = builder.validate_records(clean)
    privacy = builder.privacy_report(clean)
    out = _resolve_out(args.out, builder.DEFAULT_OUT)
    ok = bool(clean) and validation["ok"] and privacy["flagged"] == 0
    written = 0
    if ok and not args.dry_run:
        written = builder.write_jsonl(clean, out)
    payload: dict[str, Any] = {
        "status": ("SIMULASI" if args.dry_run else "OK") if ok else "GAGAL",
        "perintah": "build",
        "count": len(clean),
        "dropped": dropped,
        "dry_run": bool(args.dry_run),
        "out": None if args.dry_run or not ok else str(out),
        "written": written,
        "stats": builder.stats(clean),
        "privacy": privacy,
        "validation": validation,
        "trained": False,
        "license": LICENSE,
    }
    builder.audit("build", {
        "count": len(clean), "dropped": dropped, "dry_run": bool(args.dry_run),
        "status": payload["status"], "out": str(out),
    })
    return payload, 0 if ok else 1


def cmd_validate(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    path = _path_arg(args)
    records = _load(path)
    result = builder.validate_records(records)
    payload = {
        "status": "PASS" if result["ok"] else "FAIL",
        "perintah": "validate",
        "path": str(path),
        "count": result["count"],
        "errors": result["errors"],
        "trained": False,
        "license": LICENSE,
    }
    builder.audit("validate", {"path": str(path), "status": payload["status"],
                               "count": result["count"]})
    return payload, 0 if result["ok"] else 1


def cmd_stats(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    path = _path_arg(args)
    payload = {"status": "OK", "perintah": "stats", "path": str(path),
               "stats": builder.stats(_load(path)), "license": LICENSE}
    return payload, 0


def cmd_privacy(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    path = _path_arg(args)
    report = builder.privacy_report(_load(path))
    payload = {
        "status": "BERSIH" if report["flagged"] == 0 else "TEMUAN",
        "perintah": "privacy",
        "path": str(path),
        "privacy": report,
        "catatan": "Nilai temuan tidak pernah ditampilkan, hanya jumlah per jenis.",
        "license": LICENSE,
    }
    builder.audit("privacy", {"path": str(path), "status": payload["status"],
                              "flagged": report["flagged"]})
    return payload, 0 if report["flagged"] == 0 else 1


def cmd_preview(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    """Tampilkan contoh pasangan yang sudah disaring privasi (tanpa nilai sensitif)."""
    path = _path_arg(args)
    count = max(1, min(int(args.n), 25))
    items = [
        {
            "instruction": builder.redact(str(record.get("instruction", ""))),
            "response": builder.redact(str(record.get("response", ""))),
            "source": record.get("source"),
            "trained": False,
        }
        for record in _load(path)[:count]
    ]
    return {
        "status": "OK", "perintah": "preview", "path": str(path),
        "preview": items, "trained": False, "license": LICENSE,
    }, 0


def cmd_add(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    record = builder.manual_pair(args.instruction, args.response, args.source)
    if record is None:
        payload = {
            "status": "GAGAL", "perintah": "add",
            "error": "pasangan ditolak: terlalu pendek atau memuat kredensial",
            "license": LICENSE,
        }
        builder.audit("add", {"status": "GAGAL", "source": args.source})
        return payload, 1
    out = _resolve_out(args.out, builder.DEFAULT_OUT)
    records = builder.read_jsonl(out) if out.is_file() else []
    key = builder._instruction_key(record)
    records = [
        item for item in records
        if item.get("id") != record["id"] and builder._instruction_key(item) != key
    ]
    records.append(record)
    builder.write_jsonl(records, out)
    payload = {
        "status": "OK", "perintah": "add", "id": record["id"],
        "source": args.source, "total": len(records), "out": str(out),
        "trained": False, "license": LICENSE,
    }
    builder.audit("add", {"id": record["id"], "source": args.source,
                          "total": len(records), "out": str(out)})
    return payload, 0


def cmd_export(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    # Samakan dengan perintah lain: path relatif dihitung terhadap ROOT,
    # bukan terhadap direktori kerja saat CLI dipanggil.
    source = _input_path(args.path)
    records = _load(source)
    validation = builder.validate_records(records)
    if not validation["ok"]:
        payload = {"status": "FAIL", "perintah": "export", "path": args.path,
                   "errors": validation["errors"], "license": LICENSE}
        builder.audit("export", {"path": args.path, "status": "FAIL",
                                 "format": args.format})
        return payload, 1

    if args.format == "alpaca":
        converted: list[dict[str, Any]] = [
            {
                "instruction": r["instruction"],
                "input": "",
                "output": r["response"],
                "source": r["source"],
                "license": r["license"],
                "kind": r["kind"],
                "trained": False,
            }
            for r in records
        ]
    elif args.format == "sharegpt":
        converted = [
            {
                "conversations": [
                    {"from": "human", "value": r["instruction"]},
                    {"from": "gpt", "value": r["response"]},
                ],
                "source": r["source"],
                "license": r["license"],
                "kind": r["kind"],
                "trained": False,
            }
            for r in records
        ]
    else:
        converted = records

    out = _resolve_out(args.out, source.with_name(source.stem + "." + args.format + ".jsonl"))
    builder.write_jsonl(converted, out)
    payload = {
        "status": "OK", "perintah": "export", "path": args.path,
        "format": args.format, "count": len(converted), "out": str(out),
        "trained": False, "license": LICENSE,
        "catatan": "Ekspor untuk pipeline training pemilik; bukan hasil training.",
    }
    builder.audit("export", {"path": args.path, "status": "OK",
                             "format": args.format, "count": len(converted),
                             "out": str(out)})
    return payload, 0


def cmd_init(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    """Buat dataset baru: contoh sintetis (default) atau berkas kosong."""
    records: list[dict[str, Any]] = [] if args.empty else builder.sample_records()
    out = _resolve_out(args.out, ROOT / "dataset" / "examples" / "contoh-sintetis.jsonl")
    payload, code = _persist(records, out, "init", force=args.force,
                             audit_detail={"empty": bool(args.empty)})
    if code == 0:
        payload["sintetis"] = not args.empty
        payload["peringatan"] = (
            "Rekord ini CONTOH/SINTETIS, bukan data asli dan bukan hasil training."
            if not args.empty else "Berkas kosong siap diisi pasangan buatan pemilik."
        )
    return payload, code


def cmd_merge(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    paths = [_input_path(raw) for raw in args.paths]
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        builder.audit("merge", {"status": "GAGAL", "alasan": "masukan tidak ada"})
        return {"status": "GAGAL", "perintah": "merge", "error": "masukan tidak ditemukan",
                "paths": missing, "license": LICENSE}, 1
    records, duplicates = builder.merge_datasets(paths)
    out = _resolve_out(args.out, ROOT / "dataset" / "data" / "gabungan.jsonl")
    return _persist(records, out, "merge", force=args.force,
                    audit_detail={"inputs": len(paths)},
                    extra={"inputs": [str(p) for p in paths], "duplicates": duplicates})


def cmd_dedup(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    path = _input_path(args.path)
    records = _load(path)
    kept, removed = builder.dedup_records(records, args.key)
    out = _resolve_out(args.out, path.with_name(path.stem + ".dedup.jsonl"))
    return _persist(kept, out, "dedup", force=args.force,
                    audit_detail={"key": args.key},
                    extra={"source": str(path), "key": args.key, "removed": removed})


def cmd_filter(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    path = _input_path(args.path)
    records = _load(path)
    kept, removed = builder.filter_records(
        records, source=args.source, kind=args.kind, contains=args.contains,
        min_chars=args.min_chars, max_chars=args.max_chars,
    )
    out = _resolve_out(args.out, path.with_name(path.stem + ".filtered.jsonl"))
    return _persist(kept, out, "filter", force=args.force,
                    audit_detail={"removed": removed},
                    extra={"source": str(path), "removed": removed,
                           "criteria": {"source": args.source, "kind": args.kind,
                                        "contains": bool(args.contains),
                                        "min_chars": args.min_chars,
                                        "max_chars": args.max_chars}})


def cmd_split(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    path = _input_path(args.path)
    records = _load(path)
    try:
        parts = builder.split_records(records, args.val_frac, args.seed)
    except ValueError as exc:
        return {"status": "GAGAL", "perintah": "split", "error": str(exc),
                "license": LICENSE}, 1
    train_out = _resolve_out(args.train_out, path.with_name(path.stem + ".train.jsonl"))
    val_out = _resolve_out(args.val_out, path.with_name(path.stem + ".val.jsonl"))
    train, train_dropped = _drop_flagged(parts["train"])
    val, val_dropped = _drop_flagged(parts["val"])
    for part, label in ((train, "train"), (val, "val")):
        checked = builder.validate_records(part)
        if not checked["ok"]:
            builder.audit("split", {"status": "FAIL", "part": label,
                                    "errors": len(checked["errors"])})
            return {"status": "FAIL", "perintah": "split", "part": label,
                    "errors": checked["errors"], "license": LICENSE}, 1
    if not args.force and (train_out.exists() or val_out.exists()):
        builder.audit("split", {"status": "GAGAL", "alasan": "sudah ada"})
        return {"status": "GAGAL", "perintah": "split",
                "error": "berkas keluaran sudah ada; gunakan --force untuk menimpa",
                "license": LICENSE}, 1
    n_train = builder.write_jsonl(train, train_out)
    n_val = builder.write_jsonl(val, val_out)
    builder.audit("split", {"status": "OK", "train": n_train, "val": n_val,
                            "val_frac": args.val_frac, "seed": args.seed})
    return {
        "status": "OK", "perintah": "split", "source": str(path),
        "count": n_train + n_val, "train": n_train, "val": n_val,
        "train_out": str(train_out), "val_out": str(val_out),
        "dropped": train_dropped + val_dropped,
        "val_frac": args.val_frac, "seed": args.seed,
        "trained": False, "license": LICENSE,
    }, 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dataset-cli",
        description="Agen CLI dataset IT Agenty (persiapan data, bukan training).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("agent", help="profil agen dataset (JSON)").set_defaults(func=cmd_agent)
    sub.add_parser("doctor", help="prasyarat training yang jujur (read-only)").set_defaults(func=cmd_doctor)
    sub.add_parser("template", help="contoh format satu pasangan (JSON)").set_defaults(func=cmd_template)

    p_init = sub.add_parser("init", help="inisialisasi JSONL baru (CONTOH/SINTETIS)")
    p_init.add_argument("--out", help="path tujuan (default: dataset/examples/contoh-sintetis.jsonl)")
    p_init.add_argument("--empty", action="store_true", help="buat berkas kosong tanpa contoh")
    p_init.add_argument("--force", action="store_true", help="timpa berkas yang sudah ada")
    p_init.set_defaults(func=cmd_init)

    p_merge = sub.add_parser("merge", help="gabungkan beberapa JSONL menjadi satu")
    p_merge.add_argument("paths", nargs="+", help="dua atau lebih berkas JSONL masukan")
    p_merge.add_argument("--out", help="path tujuan (default: dataset/data/gabungan.jsonl)")
    p_merge.add_argument("--force", action="store_true", help="timpa berkas yang sudah ada")
    p_merge.set_defaults(func=cmd_merge)

    p_dedup = sub.add_parser("dedup", help="hapus pasangan ganda")
    p_dedup.add_argument("path", help="berkas JSONL masukan")
    p_dedup.add_argument("--key", choices=("id", "instruction", "pair"), default="id",
                         help="kunci kemiripan (default: id)")
    p_dedup.add_argument("--out", help="path tujuan (default: <nama>.dedup.jsonl)")
    p_dedup.add_argument("--force", action="store_true", help="timpa berkas yang sudah ada")
    p_dedup.set_defaults(func=cmd_dedup)

    p_filter = sub.add_parser("filter", help="saring rekord berdasarkan kriteria")
    p_filter.add_argument("path", help="berkas JSONL masukan")
    p_filter.add_argument("--source", help="nilai source persis")
    p_filter.add_argument("--kind", help="nilai kind persis")
    p_filter.add_argument("--contains", help="frasa bebas di instruksi/jawaban")
    p_filter.add_argument("--min-chars", type=int, help="panjang jawaban minimal")
    p_filter.add_argument("--max-chars", type=int, help="panjang jawaban maksimal")
    p_filter.add_argument("--out", help="path tujuan (default: <nama>.filtered.jsonl)")
    p_filter.add_argument("--force", action="store_true", help="timpa berkas yang sudah ada")
    p_filter.set_defaults(func=cmd_filter)

    p_split = sub.add_parser("split", help="bagi train/val deterministik tanpa tumpang tindih")
    p_split.add_argument("path", help="berkas JSONL masukan")
    p_split.add_argument("--train-out", help="path keluaran train (default: <nama>.train.jsonl)")
    p_split.add_argument("--val-out", help="path keluaran val (default: <nama>.val.jsonl)")
    p_split.add_argument("--val-frac", type=float, default=0.2, help="porsi val (default: 0.2)")
    p_split.add_argument("--seed", type=int, default=42, help="benih acak (default: 42)")
    p_split.add_argument("--force", action="store_true", help="timpa berkas yang sudah ada")
    p_split.set_defaults(func=cmd_split)

    # ``generate`` adalah alias kompatibilitas untuk ``build``; kanonik tetap build.
    for build_name in ("build", "generate"):
        p_build = sub.add_parser(build_name, help="bangun dataset dari dokumen workspace")
        p_build.add_argument("--source", action="append", help="direktori/berkas (relatif terhadap root)")
        p_build.add_argument("--limit", type=int, default=None, help="batasi jumlah rekord")
        p_build.add_argument("--out", help="path keluar JSONL")
        p_build.add_argument("--dry-run", action="store_true", help="hitung tanpa menulis")
        p_build.set_defaults(func=cmd_build)

    for name, func, help_text in (
        ("validate", cmd_validate, "validasi skema & etika dataset"),
        ("stats", cmd_stats, "ringkasan statistik dataset"),
        ("privacy", cmd_privacy, "laporan privasi tanpa menampilkan nilai"),
    ):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("path", nargs="?", help="path berkas JSONL")
        p.add_argument("--out", help="alias untuk path (kompatibilitas)")
        p.set_defaults(func=func)

    p_preview = sub.add_parser("preview", help="contoh pasangan yang sudah disaring privasi")
    p_preview.add_argument("path", nargs="?", help="path berkas JSONL")
    p_preview.add_argument("--out", help="alias untuk path (kompatibilitas)")
    p_preview.add_argument("--n", type=int, default=3, help="jumlah contoh (maks. 25)")
    p_preview.set_defaults(func=cmd_preview)

    p_add = sub.add_parser("add", help="tambah pasangan buatan pemilik")
    p_add.add_argument("instruction")
    p_add.add_argument("response")
    p_add.add_argument("--source", default="manual")
    p_add.add_argument("--out", help="path berkas JSONL tujuan")
    p_add.set_defaults(func=cmd_add)

    p_export = sub.add_parser("export", help="ekspor ke alpaca/sharegpt/jsonl")
    p_export.add_argument("path", help="path dataset JSONL masukan")
    p_export.add_argument("--format", choices=("alpaca", "sharegpt", "jsonl"), default="alpaca")
    p_export.add_argument("--out", help="path berkas JSONL keluar")
    p_export.set_defaults(func=cmd_export)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload, code = args.func(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        _emit({"status": "ERROR", "error": type(exc).__name__, "license": LICENSE})
        return 1
    _emit(payload)
    return code


if __name__ == "__main__":
    sys.exit(main())
