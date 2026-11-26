# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Deteksi dan status alat Cloud Code yang terpasang di workspace.

Sumber kebenaran adalah biner yang benar-benar ada di PATH. Modul ini hanya
membaca versi lewat subprocess ber-timeout dan tidak pernah menampilkan
kredensial, melakukan login, atau memanggil API cloud.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "system" / "reports" / "cloud_code.json"
INSTALL_REPORT = ROOT / "system" / "reports" / "cloud_code_install.json"

LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"
SERVICE = "cloud-code"

TOOLS: tuple[dict[str, str], ...] = (
    {"name": "claude", "label": "Claude Code", "kind": "ai-cli",
     "argv": "claude --version", "required": "ya"},
    {"name": "gcloud", "label": "Google Cloud CLI", "kind": "cloud-code-dependency",
     "argv": "gcloud version", "required": "ya"},
    {"name": "kubectl", "label": "Kubernetes CLI", "kind": "cloud-code-dependency",
     "argv": "kubectl version --client", "required": "ya"},
    {"name": "skaffold", "label": "Skaffold", "kind": "cloud-code-dependency",
     "argv": "skaffold version", "required": "ya"},
    {"name": "minikube", "label": "Minikube", "kind": "cloud-code-dependency",
     "argv": "minikube version", "required": "ya"},
    {"name": "code", "label": "VS Code (ekstensi Cloud Code)", "kind": "ide",
     "argv": "code --version", "required": "ya"},
)


def _version(tool: dict[str, str]) -> dict[str, Any]:
    path = shutil.which(tool["name"])
    result: dict[str, Any] = {
        "nama": tool["name"],
        "label": tool["label"],
        "jenis": tool["kind"],
        "wajib": tool["required"],
        "tersedia": path is not None,
        "path": path,
        "versi": None,
    }
    if not path:
        return result
    try:
        proc = subprocess.run(
            tool["argv"].split(),
            capture_output=True, text=True, timeout=12, check=False,
        )
        text = (proc.stdout or proc.stderr or "").strip()
        result["versi"] = text.splitlines()[0][:160] if text else None
    except (OSError, subprocess.SubprocessError):
        result["versi"] = None
    return result


def detect() -> list[dict[str, Any]]:
    """Kembalikan status tiap alat dari PATH saat ini."""
    return [_version(tool) for tool in TOOLS]


def _install_report() -> dict[str, Any]:
    try:
        data = json.loads(INSTALL_REPORT.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def status() -> dict[str, Any]:
    """Status read-only untuk layanan supervisor dan CLI."""
    tools = detect()
    required = [item for item in tools if item["wajib"] == "ya"]
    missing = [item["nama"] for item in required if not item["tersedia"]]
    installed = _install_report()
    payload = {
        "service": SERVICE,
        "status": "OK" if not missing else "GAGAL",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "alat": tools,
        "wajib_hilang": missing,
        "pemasangan": {
            key: installed.get(key, "TIDAK_ADA")
            for key in (
                "claude_code", "gcloud", "kubectl", "skaffold", "minikube", "code"
            )
        },
        "catatan": (
            "Keenam alat dinyatakan wajib. Ekstensi IDE Cloud Code tidak "
            "dipasang di lingkungan headless; biner `code` tetap diwajibkan "
            "dan status menjadi GAGAL bila biner itu belum tersedia."
        ),
        "license": LICENSE,
        "owner": OWNER,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return payload


def capabilities() -> dict[str, Any]:
    return {
        "service": SERVICE,
        "kind": "http",
        "port_default": 8785,
        "endpoints": ["/health", "/", "/status", "/capabilities", "/tools"],
        "mutations": [],
        "akses": "read-only, localhost, tanpa kredensial",
        "cli": [
            "bash scripts/cloud_code_install.sh",
            "python3 system/cloud_code.py",
            "python3 system/cloud_code_service.py --port 8785",
        ],
        "supervisor": SERVICE,
        "license": LICENSE,
        "owner": OWNER,
    }


def main() -> int:
    print(json.dumps(status(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
