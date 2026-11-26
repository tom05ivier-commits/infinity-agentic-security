# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
# Daftar tugas yang dapat dijalankan agen.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))


def _task_status(**_: Any) -> dict[str, Any]:
    from system.core import ComputerSystem

    return ComputerSystem().snapshot()


def _task_verify(**_: Any) -> dict[str, Any]:
    from security.verify import ComplianceVerifier

    return ComplianceVerifier().run()


def _task_protect(seconds: float = 2.0, **_: Any) -> dict[str, Any]:
    from system.protection import ProtectionDaemon

    return ProtectionDaemon(seconds=seconds, interval=0.2).run()


def _task_integrity(reset: bool = False, **_: Any) -> dict[str, Any]:
    from security.blue.integrity import IntegrityMonitor

    monitor = IntegrityMonitor()
    if reset:
        return {"baseline": str(monitor.create_baseline())}
    return monitor.check()


def _task_dashboard(**_: Any) -> dict[str, Any]:
    from system.dashboard import generate

    return {"dashboard": str(generate())}


def _task_capability(**_: Any) -> dict[str, Any]:
    from security.blue.capabilities import status

    return status()


def _task_perfect(seconds: float = 2.0, **_: Any) -> dict[str, Any]:
    """Siklus penyempurnaan: diagnostik → integritas → proteksi → verifikasi → dashboard."""
    results: dict[str, Any] = {}
    for name in ("capability", "integrity", "protect", "verify", "dashboard"):
        handler = TASKS.get(name)
        if handler is None:
            continue
        params = {"seconds": seconds} if name == "protect" else {}
        try:
            results[name] = {"status": "OK", "result": handler(**params)}
        except Exception as exc:  # noqa: BLE001
            results[name] = {"status": "ERROR", "error": str(exc)}
    failures = [name for name, value in results.items() if value["status"] == "ERROR"]
    verification = results.get("verify", {}).get("result", {})
    return {
        "status": "FAILED" if failures else "COMPLETED",
        "steps": list(results),
        "failures": failures,
        "compliance": verification.get("status", "unknown"),
    }


def _task_campaign(
    times: int = 3, intensity: str = "moderate", **_: Any
) -> dict[str, Any]:
    """Kampanye lengkap: proteksi → debug → serangan berulang → respons."""
    from security.campaign import run_campaign

    report = run_campaign(times=times, intensity=intensity)
    return {
        "status": report["status"],
        "times": report["times"],
        "cycles": len(report["cycles"]),
        "risk_score": report["risk_score"],
        "alerts": len(report["alerts"]),
        "report": report["report"],
        "note": report["catatan"],
    }


def _task_drill(authorize: bool = False, **_: Any) -> dict[str, Any]:
    """Latihan serangan. Hanya berjalan dengan izin eksplisit."""
    if not authorize:
        return {
            "skipped": True,
            "reason": "Serangan memerlukan authorize=True (izin tertulis + token).",
        }
    from security.blue.defense_agent import DefenseAgent
    from security.common.authorization import issue_token
    from security.red.attack_agent import AttackAgent

    token = issue_token(
        token_id="agent-drill",
        issued_by="Tomi vier",
        allowed_targets=("lab", "127.0.0.1"),
        duration_seconds=120,
    )
    defense = DefenseAgent()
    protection = defense.protect_hardware()
    attack = AttackAgent(token).full_drill()
    response = defense.respond_to_attack(attack)
    return {
        "protection": protection,
        "attack": [r.to_dict() for r in attack],
        "response": response,
    }


TASKS: dict[str, Callable[..., dict[str, Any]]] = {
    "status": _task_status,
    "verify": _task_verify,
    "protect": _task_protect,
    "integrity": _task_integrity,
    "dashboard": _task_dashboard,
    "capability": _task_capability,
    "perfect": _task_perfect,
    "campaign": _task_campaign,
    "drill": _task_drill,
}

KEYWORDS: dict[str, tuple[str, ...]] = {
    "status": ("status", "state", "keadaan", "informasi", "info"),
    "verify": ("verify", "verifikasi", "patuh", "compliance", "cek"),
    "protect": ("protect", "lindungi", "proteksi", "jaga", "antivirus"),
    "integrity": ("integrity", "integritas", "hash", "ubah", "modifikasi"),
    "dashboard": ("dashboard", "tampilan", "html", "laporkan"),
    "capability": ("capability", "caps", "cap_net_admin", "izin kernel"),
    "perfect": ("sempurnakan", "sempurna", "perfect", "optimal", "perbaiki"),
    "campaign": ("kampanye", "campaign", "rangkaian", "ulang 3", "tiga kali"),
    "drill": ("drill", "serang", "attack", "latihan", "malware"),
}
