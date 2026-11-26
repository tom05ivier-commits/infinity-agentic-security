# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Verifikasi koneksi OpenCode ↔ OpenCode AI dan kesamaan data bersama.

Tidak ada kredensial yang dibaca atau dicetak. Pemeriksaan hanya memakai
status, jalur berkas, dan checksum.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLISH = ROOT / "publish" / "infinity-agentic-security"
OPENCODE_CONFIG = Path("/root/.config/opencode/opencode.json")
UPDATE_REPORT = ROOT / "system" / "reports" / "update_all.json"
MIN_MCP = 7
# `symphony-deploy.sh` membangun ulang publish/ secara berkala. Selama jendela
# itu berkas cermin bisa sementara hilang atau belum selesai disalin, jadi
# pemeriksaan melakukan beberapa percobaan singkat sebelum menyimpulkan gagal.
MIRROR_RETRIES = 3
MIRROR_RETRY_DELAY = 0.1
# `opencode mcp list` kadang menjawab sebagian saat server sibuk (mis. saat
# publish dibangun ulang). Ulangi singkat sebelum menyimpulkan MCP terputus.
MCP_RETRIES = 5
MCP_RETRY_DELAY = 0.5
# Scorecard ditulis ulang oleh make test sebelum cermin publish disegarkan;
# memasukkannya di sini akan membuat gate flaky. Kesegaran skor dijaga oleh
# update_all.py, yang membatalkan publikasi bila salah satu skor turun.
SHARED_FILES = (
    "AGENTS.md",
    "chip/reports/chip_verification.json",
    "chip/reports/chip_synthesis.json",
    "chip/reports/iverilog.json",
    "chip/reports/browser_presets.json",
)


VOLATILE_KEYS = {"generated_at", "timestamp", "duration_ms"}


def _digest(data: bytes, rel: str) -> str:
    """Hash kanonik: field waktu tidak dihitung sebagai perbedaan data."""
    if rel.endswith(".json"):
        try:
            obj = json.loads(data.decode("utf-8"))
            if isinstance(obj, dict):
                for key in VOLATILE_KEYS:
                    obj.pop(key, None)
            data = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
    return hashlib.sha256(data).hexdigest()[:16]


def check_mcp() -> dict[str, Any]:
    """Daftar MCP dengan retry singkat agar jendela sibuk tidak jadi GAGAL."""
    last: dict[str, Any] = {"status": "GAGAL", "connected": 0, "servers": []}
    for attempt in range(MCP_RETRIES):
        try:
            out = subprocess.run(
                ["opencode", "mcp", "list"], capture_output=True, text=True,
                timeout=30, cwd=str(ROOT),
            ).stdout
            names = [
                line.split()[1]
                for line in out.splitlines()
                if line.strip().startswith("✓") and len(line.split()) >= 2
            ]
            last = {
                "status": "OK" if len(names) >= MIN_MCP else "GAGAL",
                "connected": len(names),
                "servers": names,
            }
            if last["status"] == "OK":
                return last
        except (OSError, subprocess.SubprocessError) as exc:
            last = {"status": "GAGAL", "connected": 0, "error": type(exc).__name__}
        if attempt + 1 < MCP_RETRIES:
            time.sleep(MCP_RETRY_DELAY)
    return last


def check_filesystem_scope() -> dict[str, Any]:
    try:
        config = json.loads(OPENCODE_CONFIG.read_text(encoding="utf-8"))
        entry = config.get("mcp", {}).get("filesystem", {})
        args = list(entry.get("args", [])) + list(entry.get("command", []))
        allowed = str(ROOT) in args
        return {
            "status": "OK" if allowed else "GAGAL",
            "workspace": str(ROOT),
            "terdaftar": allowed,
        }
    except (OSError, json.JSONDecodeError, AttributeError) as exc:
        return {"status": "GAGAL", "error": type(exc).__name__}


def _compare_mirror_once(redact: Any) -> tuple[list[str], dict[str, str]]:
    """Satu kali perbandingan lokal ↔ cermin (tanpa retry)."""
    mismatched: list[str] = []
    digests: dict[str, str] = {}
    for rel in SHARED_FILES:
        local = ROOT / rel
        mirror = PUBLISH / rel
        if not local.is_file() or not mirror.is_file():
            mismatched.append(rel + ": berkas tidak ada")
            continue
        raw = local.read_bytes()
        if rel == "AGENTS.md":
            raw = redact(raw.decode("utf-8")).encode("utf-8")
        a, b = _digest(raw, rel), _digest(mirror.read_bytes(), rel)
        digests[rel] = a
        if a != b:
            mismatched.append(rel)
    return mismatched, digests


def check_mirror() -> dict[str, Any]:
    """Bandingkan data bersama; AGENTS.md disanitasi seperti saat rilis.

    Ulangi beberapa kali bila berkas cermin sementara hilang/berubah saat
    publish/ sedang dibangun ulang (determinisme gate di lingkungan bersama).
    """
    import sys

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from security.privacy import redact  # noqa: E402

    mismatched: list[str] = []
    digests: dict[str, str] = {}
    for attempt in range(MIRROR_RETRIES):
        mismatched, digests = _compare_mirror_once(redact)
        if not mismatched:
            break
        if attempt + 1 < MIRROR_RETRIES:
            time.sleep(MIRROR_RETRY_DELAY)
    return {
        "status": "OK" if not mismatched else "GAGAL",
        "files": len(SHARED_FILES),
        "digests": digests,
        "mismatch": mismatched,
        "catatan": "AGENTS.md dibandingkan setelah sanitasi; itu disengaja.",
    }


def check_remote() -> dict[str, Any]:
    try:
        data = json.loads(UPDATE_REPORT.read_text(encoding="utf-8"))
        ok = (
            data.get("pushed") is True
            and data.get("local_commit") == data.get("remote_commit")
            and data.get("hy4_commit") == data.get("hy4_remote_commit")
        )
        return {
            "status": "OK" if ok else "GAGAL",
            "pushed": data.get("pushed"),
            "commit_cocok": data.get("local_commit") == data.get("remote_commit"),
            "hy4_cocok": data.get("hy4_commit") == data.get("hy4_remote_commit"),
        }
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "GAGAL", "error": type(exc).__name__}


def verify() -> dict[str, Any]:
    results = {
        "mcp": check_mcp(),
        "filesystem": check_filesystem_scope(),
        "mirror": check_mirror(),
        "remote": check_remote(),
    }
    ok = all(item["status"] == "OK" for item in results.values())
    return {
        "status": "TERHUBUNG" if ok else "GAGAL",
        "workspace": str(ROOT),
        "checks": results,
        "catatan": (
            "OpenCode, model hy4-flash-free, sesi OpenChamber, dan GitHub MCP "
            "memakai /root/workspace sebagai sumber data bersama; salinan publish "
            "adalah cermin tersanitasi."
        ),
        "license": "Tom05ivier-commits-1.0",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, ensure_ascii=False))
