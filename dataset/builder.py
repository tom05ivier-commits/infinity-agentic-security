# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pembangun dataset instruksi→jawaban dari dokumentasi workspace IT Agenty.

Alat ini adalah **persiapan data**, bukan pelatihan model:

* setiap pasangan berasal dari berkas teks milik IT Agenty sendiri;
* semua teks disaring lewat ``security.privacy.redact`` sebelum disimpan;
* pasangan yang masih memuat kredensial dibuang, bukan dicatat;
* setiap rekord ditandai ``trained: false`` — tidak ada bobot/model baru.

Tidak ada pihak ketiga, tidak ada unduhan, tidak ada training yang
dilakukan di sini. Pipeline training tetap membutuhkan compute + dataset
valid dari pemilik (lihat ``dataset-cli doctor``).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:  # redaksi privasi adalah sumber kebenaran yang sama dengan modul lain.
    from security.privacy import redact, scan, scan_secrets  # noqa: E402
except Exception:  # pragma: no cover - fallback hanya bila modul tidak ada
    def redact(text: str) -> str:  # type: ignore[misc]
        return text

    def scan(text: str) -> dict[str, int]:  # type: ignore[misc]
        return {}

    def scan_secrets(text: str) -> dict[str, int]:  # type: ignore[misc]
        return {}

LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"
MODEL_ID = "tom05-flash-free"
KIND = "doc-derived"
TRAINED = False

EXCLUDE_DIRS = {
    ".git", "node_modules", "opencode-src", "src", "symphony-src", "publish",
    "credentials", "reports", "quarantine", "__pycache__", ".playwright-mcp",
    "site", "security", "inbox", "monetisasi", "chip", "dataset",
}
ALLOWED_EXT = {".md", ".txt"}
MAX_FILE = 120_000
MAX_RESPONSE = 1_200
MIN_RESPONSE = 40
MIN_HEADING = 3
# Ambang validasi untuk data yang sudah jadi (lebih longgar dari MIN_RESPONSE
# yang dipakai saat memotong dokumen, agar dataset lama tetap lolos).
MIN_INSTRUCTION = 3
MIN_RESPONSE_STRICT = 20
MAX_RESPONSE_STRICT = 8_000
SAMPLE_KIND = "contoh-sintetis"
SAMPLE_SOURCE = "sintetis"

HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
NOISE_RE = re.compile(r"^\s*(---+|<!--|\|[\s:|-]+\|)\s*$")
WS_RE = re.compile(r"\s+")
AUDIT_PATH = ROOT / "security" / "reports" / "dataset_actions.jsonl"
DEFAULT_OUT = ROOT / "dataset" / "data" / "tom05_dataset.jsonl"

TEMPLATES = (
    "Jelaskan tentang {head}",
    "Apa yang dimaksud dengan {head}?",
    "Ringkas informasi mengenai {head}",
    "Berikan penjelasan singkat tentang {head}",
)


def iter_documents(root: Path, sources: Iterable[str] | None = None) -> list[Path]:
    """Kumpulkan berkas teks tepercaya dari *sources* (relatif terhadap root)."""
    if sources is None:
        sources = ["docs"] + [
            str(p.relative_to(root)) for p in sorted(root.glob("*.md"))
        ]
    root = root.resolve()
    found: set[Path] = set()
    for item in sources:
        target = (root / item).resolve()
        if not target.is_relative_to(root):
            continue
        if target.is_file() and target.suffix.lower() in ALLOWED_EXT:
            if target.stat().st_size <= MAX_FILE:
                found.add(target)
        elif target.is_dir():
            for current, dirs, files in os.walk(target):
                dirs[:] = [
                    d for d in dirs
                    if d not in EXCLUDE_DIRS and not d.startswith(".")
                ]
                for name in files:
                    path = Path(current) / name
                    if path.suffix.lower() not in ALLOWED_EXT:
                        continue
                    try:
                        if path.stat().st_size <= MAX_FILE:
                            found.add(path)
                    except OSError:
                        continue
    return sorted(found)


def _clean_heading(raw: str) -> str:
    text = WS_RE.sub(" ", raw).strip(" #*`")
    text = re.sub(r"^\d+(?:\.\d+)*[.)]?\s*", "", text).strip()
    return text


def _instruction(head: str, seed: str) -> str:
    if head.endswith("?"):
        return head
    index = int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16) % len(TEMPLATES)
    return TEMPLATES[index].format(head=head)


def _make_record(instruction: str, response: str, source: str) -> dict[str, Any] | None:
    """Buat satu pasangan yang sudah disaring privasi; ``None`` bila dibuang."""
    head = redact(instruction).strip()
    body = WS_RE.sub(" ", redact(response)).strip()
    if len(head) < MIN_HEADING or len(body) < MIN_RESPONSE:
        return None
    # Tolak pasangan yang masih mengandung PII atau kredensial setelah redaksi.
    # ``scan`` menghitung data pribadi (email, telepon, dll), ``scan_secrets``
    # menghitung bentuk kredensial. Keduanya tidak pernah mengembalikan nilai.
    findings = scan(head + "\n" + body)
    secrets = scan_secrets(head + "\n" + body)
    if any(findings.values()) or any(secrets.values()):
        return None
    if len(body) > MAX_RESPONSE:
        cut = body[:MAX_RESPONSE].rsplit(" ", 1)[0]
        body = cut.rstrip(" ,.;:") + " …"
    uid = hashlib.sha256((head + "\0" + source).encode("utf-8")).hexdigest()[:16]
    return {
        "id": uid,
        "instruction": head,
        "response": body,
        "source": source,
        "license": LICENSE,
        "kind": KIND,
        "trained": TRAINED,
    }


def pairs_from_text(text: str, source: str) -> list[dict[str, Any]]:
    """Ubah satu dokumen Markdown menjadi pasangan instruksi→jawaban."""
    out: list[dict[str, Any]] = []
    head: str | None = None
    body: list[str] = []

    def flush() -> None:
        nonlocal head, body
        if head:
            record = _make_record(_instruction(head, source + head), " ".join(body), source)
            if record:
                out.append(record)
        head, body = None, []

    for line in text.splitlines():
        match = HEADING_RE.match(line)
        if match:
            flush()
            candidate = _clean_heading(match.group(2))
            if len(candidate) >= MIN_HEADING:
                head = candidate
            continue
        if NOISE_RE.match(line):
            continue
        if head:
            body.append(line.strip())
    flush()
    return out


def build_dataset(
    root: Path,
    sources: Iterable[str] | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Bangun dataset dari dokumen workspace, tanpa duplikat instruksi.

    Kunci dedup harus sama dengan ``validate_records`` (normalisasi spasi +
    casefold), kalau tidak hasil build bisa ditolak oleh validator sendiri.
    """
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in iter_documents(root, sources):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(path.relative_to(root))
        for record in pairs_from_text(text, rel):
            key = _instruction_key(record)
            if key in seen:
                continue
            seen.add(key)
            records.append(record)
            if limit is not None and len(records) >= limit:
                return records
    return records


def manual_pair(instruction: str, response: str, source: str = "manual") -> dict[str, Any] | None:
    """Buat satu pasangan buatan pemilik (tetap disaring privasi)."""
    return _make_record(instruction, response, source)


# Pasangan di bawah ini sengaja dibuat-buat untuk menunjukkan format. Bukan data
# asli, bukan hasil observasi, dan bukan hasil training — ditandai di setiap
# rekord lewat source="sintetis", kind="contoh-sintetis", dan trained=false.
SAMPLE_PAIRS: tuple[tuple[str, str], ...] = (
    (
        "Contoh: Apa fungsi agen dataset IT Agenty?",
        "Ini CONTOH SINTETIS, bukan data asli dan bukan hasil training. Agen dataset "
        "hanya menyiapkan serta memvalidasi pasangan instruksi dan jawaban beserta "
        "sumber dan lisensinya.",
    ),
    (
        "Contoh: Bagaimana cara menambah pasangan buatan pemilik?",
        "Ini CONTOH SINTETIS. Gunakan perintah add dengan instruksi dan jawaban buatan "
        "pemilik; teks tetap disaring privasi sebelum disimpan ke berkas JSONL.",
    ),
    (
        "Contoh: Apakah agen dataset melakukan pelatihan model?",
        "Ini CONTOH SINTETIS. Tidak. Agen ini hanya menyiapkan dan memvalidasi data. "
        "Pelatihan memerlukan dataset berlabel milik pemilik serta komputasi yang memadai.",
    ),
)


def sample_records() -> list[dict[str, Any]]:
    """Kembalikan rekord CONTOH/SINTETIS yang lolos penyaringan privasi."""
    out: list[dict[str, Any]] = []
    for instruction, response in SAMPLE_PAIRS:
        record = _make_record(instruction, response, SAMPLE_SOURCE)
        if record is None:
            continue
        record["kind"] = SAMPLE_KIND
        record["catatan"] = "CONTOH/SINTETIS — bukan data asli, bukan hasil training."
        out.append(record)
    return out


def drop_flagged(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Buang rekord dengan PII/kredensial; kembalikan (bersih, dibuang).

    Nilai temuan tidak pernah dikembalikan atau dicetak — hanya jumlah rekord
    yang dibuang yang dilaporkan ke pemanggil.
    """
    clean: list[dict[str, Any]] = []
    dropped = 0
    for record in records:
        text = str(record.get("instruction", "")) + "\n" + str(record.get("response", ""))
        if any(scan(text).values()) or any(scan_secrets(text).values()):
            dropped += 1
            continue
        clean.append(record)
    return clean, dropped


def _instruction_key(record: dict[str, Any]) -> str:
    return WS_RE.sub(" ", str(record.get("instruction", ""))).strip().casefold()


def dedup_records(
    records: list[dict[str, Any]], key: str = "id"
) -> tuple[list[dict[str, Any]], int]:
    """Hapus duplikat, pertahankan kemunculan pertama.

    ``key``: ``id`` (default), ``instruction`` (norm + casefold), atau ``pair``
    (instruksi + jawaban).
    """
    if key not in ("id", "instruction", "pair"):
        raise ValueError(f"kunci dedup tidak dikenal: {key}")
    seen: set[str] = set()
    kept: list[dict[str, Any]] = []
    removed = 0
    for record in records:
        if key == "id":
            marker = str(record.get("id", "")).strip()
        elif key == "instruction":
            marker = _instruction_key(record)
        else:
            marker = _instruction_key(record) + "\0" + WS_RE.sub(
                " ", str(record.get("response", ""))
            ).strip().casefold()
        if marker in seen:
            removed += 1
            continue
        seen.add(marker)
        kept.append(record)
    return kept, removed


def merge_datasets(paths: list[Path]) -> tuple[list[dict[str, Any]], int]:
    """Gabungkan JSONL; duplikat id dan instruksi dibuang (first wins).

    Dedup hanya berdasarkan id tidak cukup: dua berkas boleh memuat id unik
    dengan instruksi yang sama setelah dinormalisasi, yang akan ditolak
    ``validate_records``. Keduanya dipakai agar hasil merge selalu valid.
    """
    merged: list[dict[str, Any]] = []
    for path in paths:
        merged.extend(read_jsonl(path))
    merged, by_id = dedup_records(merged, "id")
    merged, by_instruction = dedup_records(merged, "instruction")
    return merged, by_id + by_instruction


def filter_records(
    records: list[dict[str, Any]],
    *,
    source: str | None = None,
    kind: str | None = None,
    contains: str | None = None,
    min_chars: int | None = None,
    max_chars: int | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """Saring rekord berdasarkan sumber, jenis, teks, dan panjang jawaban."""
    needle = contains.strip().casefold() if contains else None
    kept: list[dict[str, Any]] = []
    for record in records:
        if source and str(record.get("source", "")) != source:
            continue
        if kind and str(record.get("kind", "")) != kind:
            continue
        if needle and needle not in (
            str(record.get("instruction", "")) + "\n" + str(record.get("response", ""))
        ).casefold():
            continue
        length = len(str(record.get("response", "")))
        if min_chars is not None and length < min_chars:
            continue
        if max_chars is not None and length > max_chars:
            continue
        kept.append(record)
    return kept, len(records) - len(kept)


def split_records(
    records: list[dict[str, Any]], val_frac: float = 0.2, seed: int = 42
) -> dict[str, list[dict[str, Any]]]:
    """Bagi train/val secara deterministik tanpa instruksi yang tumpang tindih."""
    if not 0.0 < val_frac < 1.0:
        raise ValueError("val_frac harus antara 0 dan 1")
    groups: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    for index, record in enumerate(records):
        groups.setdefault(_instruction_key(record), []).append((index, record))
    keys = sorted(groups)
    random.Random(seed).shuffle(keys)
    n_val = int(round(len(keys) * val_frac)) if len(keys) > 1 else 0
    n_val = min(max(n_val, 0), len(keys) - 1)
    val_keys = set(keys[:n_val])

    def ordered(selected: bool) -> list[dict[str, Any]]:
        items = [item for key, group in groups.items() if (key in val_keys) is selected
                 for item in group]
        return [record for _, record in sorted(items, key=lambda pair: pair[0])]

    return {"train": ordered(False), "val": ordered(True)}


def validate_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Periksa skema, panjang, duplikat, dan konsistensi etis dataset."""
    errors: list[str] = []
    required = {"id", "instruction", "response", "source", "license", "kind", "trained"}
    seen_ids: set[str] = set()
    seen_instructions: set[str] = set()
    for i, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"baris {i}: bukan objek JSON")
            continue
        missing = sorted(required - set(record))
        if missing:
            errors.append(f"baris {i}: field kurang: {', '.join(missing)}")
            continue
        for field in ("id", "instruction", "response", "source", "license", "kind"):
            if not isinstance(record[field], str) or not record[field].strip():
                errors.append(f"baris {i}: '{field}' kosong")
        if record["trained"] is not False:
            errors.append(f"baris {i}: 'trained' harus false")
        if record["license"] != LICENSE:
            errors.append(f"baris {i}: lisensi tidak dikenal")
        instruction = str(record.get("instruction", "")).strip()
        response = str(record.get("response", "")).strip()
        instruction_key = _instruction_key(record)
        if len(instruction) < MIN_INSTRUCTION:
            errors.append(f"baris {i}: 'instruction' terlalu pendek")
        if len(response) < MIN_RESPONSE_STRICT:
            errors.append(f"baris {i}: 'response' terlalu pendek")
        elif len(response) > MAX_RESPONSE_STRICT:
            errors.append(f"baris {i}: 'response' terlalu panjang")
        if instruction_key in seen_instructions:
            errors.append(f"baris {i}: instruksi duplikat")
        seen_instructions.add(instruction_key)
        if str(record.get("id", "")) in seen_ids:
            errors.append(f"baris {i}: id duplikat")
        seen_ids.add(str(record.get("id", "")))
    return {"ok": not errors, "count": len(records), "errors": errors[:50]}


def privacy_report(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Hitung temuan privasi tanpa pernah menampilkan nilainya."""
    totals: dict[str, int] = {}
    flagged = 0
    for record in records:
        text = str(record.get("instruction", "")) + "\n" + str(record.get("response", ""))
        findings = {**scan(text), **scan_secrets(text)}
        if any(findings.values()):
            flagged += 1
        for key, value in findings.items():
            totals[key] = totals.get(key, 0) + int(value)
    return {"records": len(records), "flagged": flagged, "findings": totals}


def stats(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        return {"records": 0, "sources": 0, "unique_instructions": 0, "avg_response_chars": 0}
    sources = {r.get("source") for r in records}
    instructions = {r.get("instruction") for r in records}
    avg = sum(len(str(r.get("response", ""))) for r in records) / len(records)
    return {
        "records": len(records),
        "sources": len(sources),
        "unique_instructions": len(instructions),
        "avg_response_chars": round(avg, 1),
        "trained": any(bool(r.get("trained")) for r in records),
        "license": LICENSE,
    }


def write_jsonl(records: list[dict[str, Any]], path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return len(records)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def audit(action: str, detail: dict[str, Any]) -> None:
    """Tulis jejak audit ringkas — tanpa teks prompt atau kredensial."""
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": "dataset-cli",
        "action": action,
        "detail": detail,
        "license": LICENSE,
    }
    with AUDIT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


_LIBS = ("torch", "tensorflow", "jax", "transformers", "datasets", "llama_cpp", "onnxruntime")


def _find_weights(root: Path) -> list[str]:
    """Cari bobot hanya di direktori workspace ringan (tanpa source clone)."""
    out: set[str] = set()
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for name in files:
            if name.endswith((".gguf", ".safetensors", ".bin")):
                try:
                    out.add(str((Path(current) / name).relative_to(root)))
                except ValueError:
                    continue
    return sorted(out)[:20]


def doctor() -> dict[str, Any]:
    """Laporan jujur tentang prasyarat training (read-only, tanpa aksi)."""
    libs = {name: importlib.util.find_spec(name) is not None for name in _LIBS}
    weights = _find_weights(ROOT)
    gpu = any(Path(f"/dev/nvidia{i}").exists() for i in range(8))
    ready = any(libs.values()) and bool(weights) and gpu
    return {
        "dataset_agent": "tersedia",
        "training_siap": ready,
        "pustaka_ml": libs,
        "bobot_ditemukan": weights,
        "gpu_terdeteksi": gpu,
        "catatan": (
            "Agen CLI ini hanya menyiapkan/memvalidasi dataset. Training nyata "
            "membutuhkan pustaka ML, bobot dasar milik pemilik, dan GPU — "
            "semuanya tidak tersedia di lingkungan ini saat pemeriksaan."
        ),
        "license": LICENSE,
    }
