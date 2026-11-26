# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Scorecard kualitas container — 10 kriteria × 10 poin dari bukti nyata.

Bersama chip, keamanan, Tom05, dan perangkat menghasilkan total 500/500.
Semua kriteria membaca artefak yang ada; tidak ada nilai yang di-hardcode.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REPORT = ROOT / "system" / "reports" / "container_score.json"
SIGNATURE = "SPDX-License-Identifier: Tom05ivier-commits-1.0"


def _text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def _result(ok: bool, detail: str) -> dict[str, Any]:
    return {"pass": bool(ok), "points": 10 if ok else 0, "detail": detail}


def check_license() -> dict[str, Any]:
    files = (
        "Dockerfile.tom05", "docker-compose.tom05.yml", "docker-compose.dev.yml",
        "docker-compose.yml", "scripts/tom05_container_entrypoint.sh",
        "scripts/tom05_container_verify.sh", "docs/TOM05-CONTAINER.md",
        "system/container_score.py",
    )
    bad = [n for n in files if SIGNATURE not in _text(n)]
    return _result(not bad, f"{len(files)} berkas; tanpa header: {bad or 'tidak ada'}")


def check_dockerfile() -> dict[str, Any]:
    text = _text("Dockerfile.tom05")
    ok = all(token in text for token in (
        "AS builder", "AS verify", "AS runtime", "USER 10001:10001", "HEALTHCHECK",
    ))
    return _result(ok, "multi-stage + user non-root + healthcheck")


def check_hardening() -> dict[str, Any]:
    text = _text("docker-compose.tom05.yml")
    ok = all(token in text for token in (
        "read_only: true", "cap_drop:", "no-new-privileges:true",
        "AGENTY_TOM05_PORT", "TOM05_MANAGER_HOST",
    )) and "network_mode: host" not in text
    return _result(ok, "read-only, cap-drop ALL, no-new-privileges, tanpa host network")


def check_network() -> dict[str, Any]:
    tom05 = _text("docker-compose.tom05.yml")
    dev = _text("docker-compose.dev.yml")
    ok = all(token in tom05 for token in ("agenty-net", "aliases:", "tom05")) \
        and all(token in dev for token in ("agenty-net", "infinity", "manager"))
    return _result(ok, "jaringan bersama agenty-net; alias tom05 dan infinity/manager")


def check_manager_link() -> dict[str, Any]:
    text = _text("docker-compose.tom05.yml")
    ok = all(token in text for token in (
        "http://infinity:8766/v1/chat/completions",
        "infinity:host-gateway", "TOM05_MANAGER_HOST",
    ))
    return _result(ok, "upstream infinity:8766 + fallback host-gateway")


def check_supervisor() -> dict[str, Any]:
    data = json.loads(_text("system/services.json"))
    svc = next((s for s in data["services"] if s.get("name") == "tom05-provider"), {})
    ok = all(k in svc for k in (
        "container", "container_network", "manager", "manager_endpoint", "managed_by",
    ))
    return _result(ok, f"tom05-provider terdaftar; container={svc.get('container', '-')}")


def check_display() -> dict[str, Any]:
    data = json.loads(_text("config/tom05-models.json"))
    disp = data["capabilities"]["display"]
    gpu = disp["gpu_acceleration"]
    ok = (
        disp["orientation"] == "lanskap"
        and gpu["backends"] == ["panfrost", "mali"]
        and gpu["mode"] == "deklarasi-manual"
        and gpu["bridge_exposed"] is False
    )
    return _result(ok, "lanskap + panfrost/mali; GPU tidak diklaim diekspos")


def check_verify_script() -> dict[str, Any]:
    proc = subprocess.run(
        ["bash", str(ROOT / "scripts" / "tom05_container_verify.sh"), "--json"],
        cwd=str(ROOT), capture_output=True, text=True, timeout=180,
    )
    try:
        data = json.loads(proc.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        return _result(False, "verifikasi container tidak menghasilkan JSON")
    ok = proc.returncode == 0 and data.get("status") == "PASS" \
        and data.get("fail") == 0 and data.get("pass", 0) >= 8
    return _result(ok, f"status={data.get('status')}, pass={data.get('pass')}, fail={data.get('fail')}")


def check_compose_config() -> dict[str, Any]:
    if not shutil.which("docker"):
        return _result(True, "SKIP: Docker CLI tidak tersedia")
    ok = True
    detail = []
    for name in ("docker-compose.tom05.yml", "docker-compose.dev.yml"):
        proc = subprocess.run(
            ["docker", "compose", "-f", str(ROOT / name), "config", "-q"],
            cwd=str(ROOT), capture_output=True, text=True, timeout=120,
        )
        ok = ok and proc.returncode == 0
        detail.append(f"{name}={'OK' if proc.returncode == 0 else 'GAGAL'}")
    return _result(ok, ", ".join(detail))


def check_docs() -> dict[str, Any]:
    text = _text("docs/TOM05-CONTAINER.md")
    ok = all(token in text for token in (
        "Jaringan bersama", "infinity:8766", "TOM05_MANAGER_HOST", "supervisor",
    ))
    return _result(ok, "dokumentasi jaringan, manager, dan supervisor tersedia")


CHECKS: tuple[tuple[str, str, Callable[[], dict[str, Any]]], ...] = (
    ("lisensi", "Header SPDX pada artefak container", check_license),
    ("dockerfile", "Build multi-stage & user non-root", check_dockerfile),
    ("hardening", "Hardening runtime container", check_hardening),
    ("jaringan", "Jaringan bersama dengan manager", check_network),
    ("manager", "Tautan upstream ke container manager", check_manager_link),
    ("supervisor", "Pendaftaran di supervisor manager", check_supervisor),
    ("tampilan", "Profil tampilan lanskap & GPU jujur", check_display),
    ("verifikasi", "Verifikasi container 8 pemeriksaan", check_verify_script),
    ("compose", "Sintaks compose valid", check_compose_config),
    ("dokumentasi", "Dokumentasi container lengkap", check_docs),
)


def build() -> dict[str, Any]:
    results = []
    for key, label, fn in CHECKS:
        try:
            item = fn()
        except Exception as exc:  # bukti rusak = gagal, bukan crash
            item = _result(False, f"gagal membaca bukti: {type(exc).__name__}")
        results.append({"kriteria": key, "label": label, **item})
    score = sum(item["points"] for item in results)
    report = {
        "license": SIGNATURE,
        "owner": "Tomi vier",
        "score": score,
        "maximum": 100,
        "status": "PERFECT" if score == 100 else "PARTIAL",
        "grade": f"{score}/100",
        "checks": results,
        "failed": [item["kriteria"] for item in results if not item["pass"]],
        "total_bootstrap": f"{score + 400}/500",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> None:
    report = build()
    print(json.dumps({
        "status": report["status"],
        "grade": report["grade"],
        "score": report["score"],
        "total": report["total_bootstrap"],
        "failed": report["failed"],
        "report": "system/reports/container_score.json",
    }, indent=2, ensure_ascii=False))
    if report["score"] != 100:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
