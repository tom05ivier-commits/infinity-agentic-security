# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#  Diagnostik Copilot CLI → bridge → OpenCode hy4-flash-free.

from __future__ import annotations

import json
import os
import shutil
import subprocess
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = Path("/root/.copilot/providers.json")
INSTRUCTIONS = ROOT / ".github" / "copilot-instructions.md"
EXPECTED_MODEL = "opencode-hy4/hy4-flash-free"
BRIDGE_HEALTH = "http://127.0.0.1:8766/v1/health"
BRIDGE_MODELS = "http://127.0.0.1:8766/v1/models"


def _http_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=3) as response:
        return json.loads(response.read().decode("utf-8"))


def _cli_help() -> str:
    if not shutil.which("copilot"):
        return ""
    completed = subprocess.run(
        ["copilot", "config", "model"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    return completed.stdout.strip()


def diagnose(smoke: bool = False) -> dict[str, Any]:
    """Kumpulkan status semua komponen Copilot CLI."""
    checks: dict[str, Any] = {}

    checks["cli_version"] = ""
    if shutil.which("copilot"):
        version = subprocess.run(
            ["copilot", "version"], capture_output=True, text=True, timeout=15
        )
        checks["cli_version"] = (version.stdout or version.stderr).strip().splitlines()[0]
    checks["cli_available"] = bool(checks["cli_version"])

    checks["configured_model"] = _cli_help()
    checks["model_ok"] = checks["configured_model"] == EXPECTED_MODEL

    checks["provider_ok"] = False
    if PROVIDERS.exists():
        try:
            data = json.loads(PROVIDERS.read_text(encoding="utf-8"))
            checks["provider_ok"] = (
                any(p.get("name") == "opencode-hy4" for p in data.get("providers", []))
                and any(m.get("id") == "hy4-flash-free" for m in data.get("models", []))
            )
        except json.JSONDecodeError:
            pass

    try:
        health = _http_json(BRIDGE_HEALTH)
        checks["bridge_ok"] = health.get("status") == "OK"
        checks["bridge_model"] = health.get("model")
    except Exception as exc:  # noqa: BLE001
        checks["bridge_ok"] = False
        checks["bridge_error"] = type(exc).__name__

    try:
        models = _http_json(BRIDGE_MODELS)
        checks["bridge_models"] = [m.get("id") for m in models.get("data", [])]
    except Exception:  # noqa: BLE001
        checks["bridge_models"] = []

    checks["instructions_ok"] = (
        INSTRUCTIONS.exists()
        and "Tom05ivier-commits-1.0" in INSTRUCTIONS.read_text(encoding="utf-8")
    )
    # CLI kanonik baru adalah tom05; `hy4` hanya alias kompatibilitas lokal.
    _bin = Path("/usr/local/bin")
    _cli_installed = (_bin / "tom05").exists() or (_bin / "hy4").exists()
    checks["hy4_cli"] = ((ROOT / "tom05").exists() or (ROOT / "hy4").exists()) and _cli_installed

    if smoke:
        try:
            result = subprocess.run(
                [str(ROOT / "run_copilot.sh"), "-p", "Balas hanya: OK"],
                capture_output=True,
                text=True,
                timeout=180,
                cwd=str(ROOT),
            )
            combined = result.stdout + result.stderr
            checks["smoke_ok"] = result.returncode == 0 and "OK" in combined
            checks["smoke_exit"] = result.returncode
        except subprocess.SubprocessError as exc:
            checks["smoke_ok"] = False
            checks["smoke_exit"] = str(exc)

    core = ("cli_available", "model_ok", "provider_ok", "bridge_ok", "instructions_ok", "hy4_cli")
    checks["status"] = "OK" if all(checks.get(key) for key in core) else "DEGRADED"
    if smoke:
        checks["status"] = "OK" if checks["status"] == "OK" and checks.get("smoke_ok") else "DEGRADED"
    return checks


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Doctor Copilot CLI")
    parser.add_argument("--smoke", action="store_true", help="jalankan prompt uji")
    args = parser.parse_args()
    print(json.dumps(diagnose(args.smoke), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
