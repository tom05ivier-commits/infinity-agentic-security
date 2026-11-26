# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Model pengetahuan tom05 berbasis retrieval dari data workspace.

Ini BUKAN model neural terlatih. Tidak ada bobot, dataset training, atau
pelatihan. Artefak ini mengindeks berkas teks milik IT Agenty, menyaringnya
dengan ``security.privacy.redact``, lalu menjawab dengan mengambil potongan
ter relevan (TF-IDF ringan, tanpa dependensi eksternal).

Tujuan: menyediakan responder nyata untuk identitas ``tom05-flash-free``
tanpa terhubung ke model pihak ketiga, sekaligus jujur tentang sifatnya.

Perbaikan 2026-11-23:
- Kata kerja umum ("status", "cek", "lihat", "berikan") tidak lagi dibuang
  sebagai stop word, sehingga pertanyaan singkat tidak dianggap kosong.
- Dokumen Markdown diprioritaskan; potongan kode dibersihkan dari baris
  terpotong supaya tidak muncul sampah seperti "ocessError) as exc:".
- Ada ambang relevansi (coverage + bobot spesifik); kalau tidak ada bukti
  kuat, jawaban jujur "tidak menemukan" lebih baik daripada kode acak.
"""

from __future__ import annotations

import math
import os
import re
import sys
import uuid
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from security.privacy import redact
except Exception:  # pragma: no cover
    def redact(text: str) -> str:  # type: ignore[misc]
        return text

MODEL_ID = "tom05-flash-free"
KIND = "retrieval-grounded"
TRAINED = False
LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"

EXCLUDE_DIRS = {
    ".git", "node_modules", "opencode-src", "src", "symphony-src",
    "publish", "credentials", "reports", "quarantine", "__pycache__",
    ".playwright-mcp", "site", "chip", "security", "tests", "output",
    # Klon repo GitHub (26 repo) dan SDK pihak ketiga bukan data pengetahuan
    # IT Agenty. Mengindeksnya membuat startup selfhost lambat > 90 detik.
    "github-tools", "antigravity-sdk-python",
}
ALLOWED_EXT = {".md", ".py", ".json", ".txt", ".sh", ".yml", ".yaml", ".v", ".html", ".css"}
DOC_EXT = {".md", ".txt"}
MAX_FILE = 200_000
CHARS = 900
OVERLAP = 150
TOP_N = 3
MIN_COVERAGE = 0.40
MIN_RATIO = 0.22
SNIPPET_LIMIT = 360

# Katafungsi saja. Jangan masukkan kata kerja perintah ("status", "cek", ...).
STOP = {
    "yang", "dan", "atau", "di", "ke", "dari", "untuk", "pada", "dengan", "ini", "itu",
    "adalah", "ada", "bagaimana", "apa", "mengapa", "kapan", "dimana", "siapa", "the",
    "a", "an", "is", "are", "of", "to", "in", "for", "and", "or", "on", "with", "how",
    "what", "why", "when", "where", "who", "can", "do", "does", "tolong", "jelaskan",
    "saya", "kamu", "nya", "kan", "lah",
}
# Token umum dalam sumber kode: tidak boleh jadi satu-satunya bukti relevansi.
GENERIC = {
    "error", "errors", "file", "files", "data", "code", "line", "lines",
    "value", "return", "class", "def", "import", "self", "print", "json",
    "http", "url", "api", "name", "type", "run", "test", "info", "true",
    "false", "none", "int", "str", "bool", "write", "read", "open", "get",
}
TOKEN_RE = re.compile(r"[a-z0-9_./-]{2,}")


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOP]


def _iter_files() -> list[Path]:
    """Telusuri file teks, memangkas direktori besar sejak awal (cepat)."""
    out: list[Path] = []
    for current, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        base = Path(current)
        for name in files:
            path = base / name
            if path.suffix.lower() not in ALLOWED_EXT:
                continue
            try:
                if path.stat().st_size > MAX_FILE:
                    continue
                out.append(path)
            except OSError:
                continue
    return sorted(out)


BROKEN_PREFIX = re.compile(r"^[a-z]{2,8}[A-Z)]|^[a-z]{1,3}$")


def clean_snippet(piece: str, limit: int = SNIPPET_LIMIT) -> str:
    """Buang baris terpotong dan normalkan potongan sebelum ditampilkan."""
    lines = piece.splitlines()
    if len(lines) > 9:
        lines = lines[:9]
    if lines:
        first = lines[0].strip()
        # Hanya buang jika jelas potongan ekor, bukan baris huruf kecil biasa.
        if first and (first[0] in ")}]>" or BROKEN_PREFIX.match(first)):
            lines = lines[1:]
    if lines:
        last = lines[-1].rstrip()
        if last and last[-1] not in ".:;!?)]}`'\"≥>":
            lines = lines[:-1]
    out = "\n".join(lines).strip()
    # Komentar header SPDX/lisensi tidak membantu jawaban.
    if out.startswith("<!--"):
        end = out.find("-->")
        if 0 <= end < 400:
            out = out[end + 3:].strip()
    out = re.sub(r"[ \t]+", " ", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    if len(out) > limit:
        cut = out[:limit].rsplit(" ", 1)[0]
        out = cut.rstrip(" \n") + " …"
    return out


def split_prose(text: str, size: int = CHARS) -> list[str]:
    """Potong dokumen per paragraf utuh, bukan per karakter."""
    chunks: list[str] = []
    buf = ""
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if not para:
            continue
        if len(buf) + len(para) + 2 <= size:
            buf = (buf + "\n\n" + para).strip()
            continue
        if buf:
            chunks.append(buf)
        while len(para) > size:
            cut = para[:size].rsplit("\n", 1)[0] or para[:size]
            chunks.append(cut.strip())
            para = para[len(cut):].strip()
        buf = para
    if buf:
        chunks.append(buf)
    return chunks or [text[:size].strip()]


def split_code(text: str, size: int = CHARS) -> list[str]:
    """Potong kode per baris utuh supaya tidak ada baris setengah."""
    chunks: list[str] = []
    buf: list[str] = []
    used = 0
    for line in text.splitlines():
        if buf and used + len(line) + 1 > size:
            chunks.append("\n".join(buf).strip())
            buf, used = [], 0
        buf.append(line)
        used += len(line) + 1
    if buf:
        chunks.append("\n".join(buf).strip())
    return chunks


class KnowledgeModel:
    """Indeks retrieval ringan dari data workspace yang sudah disaring privasi."""

    def __init__(self) -> None:
        self.chunks: list[str] = []
        self.sources: list[str] = []
        self.doc_freq: Counter[str] = Counter()
        self.postings: dict[str, list[int]] = {}
        self._build()

    def _build(self) -> None:
        for path in _iter_files():
            try:
                raw = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            clean = redact(raw)
            rel = str(path.relative_to(ROOT))
            is_doc = path.suffix.lower() in DOC_EXT
            pieces = split_prose(clean) if is_doc else split_code(clean)
            for piece in pieces:
                piece = piece.strip()
                if not piece:
                    continue
                idx = len(self.chunks)
                self.chunks.append(piece)
                self.sources.append(rel)
                for token in set(tokenize(piece)):
                    self.postings.setdefault(token, []).append(idx)
                    self.doc_freq[token] += 1

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "kind": KIND, "trained": TRAINED,
            "chunks": len(self.chunks), "berkas": len(set(self.sources)),
            "model": MODEL_ID, "license": LICENSE, "owner": OWNER,
            "catatan": "Model pengetahuan berbasis retrieval; bukan model neural terlatih.",
        }

    def answer(self, question: str) -> dict[str, Any]:
        tokens = tokenize(question)
        if not tokens:
            return self._wrap(
                "Pertanyaan kosong. Saya adalah model pengetahuan berbasis retrieval "
                "dari data workspace IT Agenty, bukan model neural terlatih.", [])

        n = max(1, len(self.chunks))
        scores: Counter[int] = Counter()
        matched: list[str] = []
        weights: dict[str, float] = {}
        for token in tokens:
            postings = self.postings.get(token, [])
            if not postings:
                continue
            matched.append(token)
            weight = math.log(1 + n / (1 + len(postings)))
            if token in GENERIC:
                weight *= 0.35
            weights[token] = weight
            for idx in postings:
                boost = 1.6 if Path(self.sources[idx]).suffix.lower() in DOC_EXT else 1.0
                tf = 1 + math.log(1 + self.chunks[idx].lower().count(token))
                scores[idx] += weight * boost * tf

        best = scores.most_common(TOP_N)
        coverage = len(matched) / len(tokens)
        specific = [t for t in matched if t not in GENERIC]
        ratio = (best[0][1] / max(sum(weights.values()), 1e-9)) if best else 0.0
        if not best or coverage < MIN_COVERAGE or ratio < MIN_RATIO or (
            not specific and coverage < 0.99
        ):
            return self._wrap(
                "Saya tidak menemukan potongan data workspace yang relevan dan "
                "spesifik untuk pertanyaan ini. Saya hanya menjawab dari data IT "
                "Agenty yang tersedia secara lokal (retrieval), bukan model neural "
                "terlatih. Coba sebutkan topik atau nama berkas yang lebih spesifik.", [])

        parts: list[str] = []
        used: list[str] = []
        for idx, _score in best:
            src = self.sources[idx]
            if src in used:  # satu potongan per berkas cukup
                continue
            snippet = clean_snippet(self.chunks[idx])
            if not snippet:
                continue
            used.append(src)
            parts.append(f"[{src}]\n{snippet}")
        if not parts:
            return self._wrap(
                "Saya tidak menemukan potongan data workspace yang dapat "
                "ditampilkan untuk pertanyaan ini (retrieval lokal, bukan model "
                "neural terlatih).", [])

        content = (
            "Dari data workspace IT Agenty yang tersedia (retrieval, bukan model "
            "neural terlatih):\n\n" + "\n\n---\n\n".join(parts)
        )
        return self._wrap(content, used)

    def _wrap(self, content: str, sources: list[str]) -> dict[str, Any]:
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
            "object": "chat.completion",
            "model": MODEL_ID,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }],
            "tom05": {
                "kind": KIND, "trained": TRAINED, "sources": sources,
                "license": LICENSE, "owner": OWNER,
                "catatan": "Dihasilkan dari data workspace via retrieval; bukan model neural terlatih.",
            },
        }


_MODEL: KnowledgeModel | None = None


def get_model() -> KnowledgeModel:
    global _MODEL
    if _MODEL is None:
        _MODEL = KnowledgeModel()
    return _MODEL


if __name__ == "__main__":
    import argparse
    import json
    ap = argparse.ArgumentParser(description="Model pengetahuan tom05 (retrieval)")
    ap.add_argument("question", nargs="?")
    ap.add_argument("--stats", action="store_true")
    args = ap.parse_args()
    model = get_model()
    print(json.dumps(model.stats if args.stats else model.answer(args.question or "status"),
                     indent=2, ensure_ascii=False))
