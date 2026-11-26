# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Kelola read-only 23 chip agen kustom + status chip NEURO-25.

Modul ini hanya membaca laporan yang sudah diverifikasi. Ia tidak menjalankan
agen, tidak mengubah status fabrikasi/validasi, tidak mengakses jaringan, dan
tidak menyimpan kredensial atau data subjek.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AGENTS_REPORT = ROOT / "chip" / "reports" / "custom_agents_verify.json"
NEURO_REPORT = ROOT / "chip" / "reports" / "neuro25.json"

LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"
EXPECTED_AGENTS = 23

ALLOWED = ("verify", "status", "report")
DENIED = (
    "change_fabrication",
    "change_clinical_validation",
    "medical_claim",
    "subject_data",
    "network_transmission",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def report() -> dict[str, Any]:
    """Gabungkan bukti 23 chip kustom dan NEURO-25 menjadi satu status baca saja."""
    agents = _load(AGENTS_REPORT)
    neuro = _load(NEURO_REPORT)
    safety = neuro.get("safety", {})

    gate_ok = all((
        safety.get("consent_gate") is True,
        safety.get("action_blocked_without_gate") is True,
        safety.get("neural_interface") is False,
        safety.get("implantable") is False,
        safety.get("stimulation") is False,
        safety.get("subject_data") is False,
        safety.get("network_transmission") is False,
        safety.get("offline_verification") is True,
    ))

    entries = agents.get("results", [])
    agent_ok = (
        agents.get("status") == "PASS"
        and len(entries) == EXPECTED_AGENTS
        and all(item["status"] == "PASS" for item in entries)
    )
    neuro_ok = neuro.get("status") == "PASS" and gate_ok
    status = "PASS" if agent_ok and neuro_ok else "FAIL"

    return {
        "schema": "tom05-neuro25-fleet/1",
        "status": status,
        "agents": {
            "count": len(entries),
            "expected": EXPECTED_AGENTS,
            "vectors": agents.get("vectors", 0),
            "fabrication": agents.get("fabrication", "NOT_READY"),
            "items": [
                {"agent": item["agent"], "chip": item["chip"],
                 "acc": item["acc"], "status": item["status"]}
                for item in entries
            ],
        },
        "neuro25": {
            "status": neuro.get("status"),
            "fabrication": neuro.get("fabrication"),
            "clinical_validation": neuro.get("clinical_validation"),
            "medical_device": neuro.get("medical_device"),
            "safety_gate": gate_ok,
        },
        "allowed": list(ALLOWED),
        "denied": list(DENIED),
        "note": (
            "23 entri adalah chip logika gate per agen (termasuk hy4 yang "
            "diaktifkan kembali dan agenty-1..6), bukan 1000 agen LLM "
            "mandiri. Status PASS hanya berarti RTL cocok model dan aman "
            "dalam batas simulasi."
        ),
        "license": LICENSE,
        "owner": OWNER,
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, ensure_ascii=False))
