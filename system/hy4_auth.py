# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#" Pemeriksa otorisasi multi-user untuk rilis publik hy4.

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COPILOT_CONFIG = Path("/root/.copilot/config.json")
PROVIDERS_CONFIG = Path("/root/.copilot/providers.json")
PUBLIC_REPOS = (ROOT / "publish" / "infinity-agentic-security", ROOT / "publish" / "hy4-agent-model")

# Pola token nyata. Placeholder dokumentasi tidak dihitung sebagai kebocoran.
TOKEN_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}"),
    re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_-]{20,}"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._-]{24,}"),
    re.compile(r"\bOPENCODE_API_KEY\s*=\s*[A-Za-z0-9._-]{24,}"),
)

PLACEHOLDER_HINTS = (
    "example.invalid",
    "<redacted>",
    "your-",
    "token-anda",
    "kunci-asli",
    "placeholder",
    "changeme",
)

SKIP_SUFFIXES = {".md", ".example", ".txt", ".license", ".png", ".jpg", ".svg", ".pdf", ".woff", ".woff2", ".ttf"}


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def local_status() -> dict[str, Any]:
    """Laporkan keberadaan kredensial lokal tanpa menyertakan nilainya."""
    opencode_auth = False
    try:
        result = subprocess.run(
            ["opencode", "auth", "list"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        opencode_auth = "stored" in (result.stdout + result.stderr).lower()
    except (OSError, subprocess.SubprocessError):
        opencode_auth = False

    copilot_auth = False
    if COPILOT_CONFIG.exists():
        try:
            text = "\n".join(
                line for line in _read(COPILOT_CONFIG).splitlines()
                if not line.strip().startswith("//")
            )
            data = json.loads(text)
            copilot_auth = bool(data.get("authTokens"))
        except json.JSONDecodeError:
            copilot_auth = False

    provider_key = False
    if PROVIDERS_CONFIG.exists():
        try:
            data = json.loads(_read(PROVIDERS_CONFIG))
            provider_key = any(bool(item.get("apiKey")) for item in data.get("providers", []))
        except json.JSONDecodeError:
            provider_key = False

    return {
        "opencode_auth": opencode_auth,
        "copilot_auth": copilot_auth,
        "bridge_provider_key": provider_key,
        "env_api_key": bool(os.environ.get("OPENCODE_API_KEY")),
        "note": "Hanya status boolean; nilai kredensial tidak pernah dikembalikan.",
    }


def scan_public() -> dict[str, Any]:
    """Pindai repo publik untuk token nyata."""
    findings: list[str] = []
    scanned = 0
    for repo in PUBLIC_REPOS:
        if not repo.exists():
            continue
        for path in repo.rglob("*"):
            if not path.is_file() or ".git" in path.parts:
                continue
            if path.suffix.lower() in SKIP_SUFFIXES:
                continue
            text = _read(path)
            if not text:
                continue
            scanned += 1
            lowered = text.lower()
            for pattern in TOKEN_PATTERNS:
                for match in pattern.finditer(text):
                    value = match.group(0)
                    if any(hint in value.lower() or hint in lowered for hint in PLACEHOLDER_HINTS):
                        continue
                    findings.append(f"{repo.name}:{path.relative_to(repo)}")
                    break
    return {
        "scanned_files": scanned,
        "findings": sorted(set(findings)),
        "status": "AMAN" if not findings else "BOCOR",
    }


def guide() -> dict[str, Any]:
    """Instruksi otorisasi per pemasangan."""
    return {
        "prinsip": "Token tidak dibagikan; setiap pemasangan login dengan akunnya sendiri.",
        "langkah": [
            "opencode auth login",
            "copilot login",
            "./manage_hy4.sh copilot-sync",
            "./hy4-auth-check.sh",
        ],
        "lokasi_token": [
            "~/.config/opencode (atau ~/.local/share/opencode)",
            "~/.copilot/config.json",
            "~/.copilot/providers.json",
        ],
        "rilis_publik": " repo hanya berisi kode + dokumentasi; tidak ada token.",
    }


def report() -> dict[str, Any]:
    local = local_status()
    public = scan_public()
    ready = local["opencode_auth"] or local["env_api_key"]
    return {
        "status": "SIAP" if ready and public["status"] == "AMAN" else "PERLU TINDAKAN",
        "lokal": local,
        "publik": public,
        "panduan": guide(),
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Hy4 public-release auth check")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    data = report()
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"Status: {data['status']}")
        print(f"Lokal: {data['lokal']}")
        print(f"Publik: {data['publik']['status']} ({data['publik']['scanned_files']} file)")
        if data["status"] != "SIAP":
            print("Ikuti panduan: " + " | ".join(data["panduan"]["langkah"]))


if __name__ == "__main__":
    main()
