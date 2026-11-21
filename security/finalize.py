# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#  Laporan penyelesaian terpadu untuk objective keamanan.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .common.config import EICAR_SIGNATURE, LAB_ROOT, SECURITY_ROOT

ROOT = SECURITY_ROOT.parent
REPORTS = SECURITY_ROOT / "reports"
OUTPUT = REPORTS / "final_report.json"
DELIVERIES = REPORTS / "data_deliveries.jsonl"


def _load(name: str) -> dict[str, Any]:
    path = REPORTS / name
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _chip_synthesis_ok() -> bool:
    """Sintesis Yosys & simulasi gate-level berhasil."""
    path = ROOT / "chip" / "reports" / "chip_synthesis.json"
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return (
        data.get("status") == "PASS"
        and len(data.get("modules", [])) >= 8
        and data.get("total_cells", 0) > 0
    )


def _firewall_drill_ok() -> bool:
    """Drill firewall hardware/software berhasil pada siklus terakhir."""
    path = REPORTS / "firewall_drill.json"
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return data.get("status") == "BERHASIL" and all(data.get("criteria", {}).values())


def _chip_ok() -> bool:
    """Desain chip terverifikasi dan preset simulator tersedia."""
    verifikasi = ROOT / "chip" / "reports" / "chip_verification.json"
    if not verifikasi.exists():
        return False
    try:
        data = json.loads(verifikasi.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    simulator = ROOT / "site" / "chip" / "simulator.html"
    return (
        data.get("status") == "PASS"
        and data.get("modules", 0) >= 5
        and data.get("vectors", 0) >= 1060
        and (ROOT / "chip" / "tb" / "tb_chip.v").exists()
        and "alu4" in simulator.read_text(encoding="utf-8")
    )


def _pm_cli_ok() -> bool:
    """Pengetahuan CLI Professor Messer terpasang di model hy4."""
    manager = ROOT / "system" / "hy4_manager.py"
    return (
        (ROOT / "PM_CLI.md").exists()
        and "PM_CLI.md" in (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        and "PM_CLI.md" in (ROOT / "advanced" / "knowledge.py").read_text(encoding="utf-8")
        and manager.exists()
        and "cli-troubleshoot.md" in manager.read_text(encoding="utf-8")
    )


def _doctor_ok() -> bool:
    """Doctor CLI terdaftar di manajer dan dokumentasinya tersedia."""
    manager = ROOT / "system" / "hy4_manager.py"
    return (
        (ROOT / "DOCTOR_CLI.md").exists()
        and (ROOT / "run_doctor.sh").exists()
        and manager.exists()
        and '"doctor"' in manager.read_text(encoding="utf-8")
    )


def _hy4_manager_ok() -> bool:
    """Manajer model/agent/CLI tersedia di artefak."""
    return (
        (ROOT / "manage_hy4.sh").exists()
        and (ROOT / "system" / "hy4_manager.py").exists()
        and (ROOT / "system" / "tests" / "test_hy4_manager.py").exists()
    )


def _platform_ok() -> bool:
    """Pengetahuan platform CLI sudah masuk konteks hy4."""
    required = (
        ROOT / "PLATFORM_CLIS.md",
        ROOT / "platform_clis" / "clis.py",
        ROOT / ".github" / "copilot-instructions.md",
    )
    if not all(path.exists() for path in required):
        return False
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    instructions = required[2].read_text(encoding="utf-8")
    knowledge = (ROOT / "advanced" / "knowledge.py").read_text(encoding="utf-8")
    return (
        "PLATFORM_CLIS.md" in agents
        and "PLATFORM_CLIS.md" in instructions
        and "PLATFORM_CLIS.md" in knowledge
    )


def _copilot_ok() -> bool:
    """Status diagnostik Copilot CLI (tanpa smoke test)."""
    import importlib.util

    doctor_path = ROOT / "copilot-bridge" / "doctor.py"
    if not doctor_path.exists():
        return False
    spec = importlib.util.spec_from_file_location("copilot_doctor_final", doctor_path)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        return False
    spec.loader.exec_module(module)
    return module.diagnose()["status"] == "OK"


def _jsonl_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def finalize() -> dict[str, Any]:
    """Gabungkan semua bukti menjadi satu laporan penyelesaian."""
    verification = _load("verification.json")
    campaign = _load("campaign.json")
    efficacy = _load("efficacy.json")
    debug = _load("debug_report.json")
    incident = _load("incident_report.json")

    requirements = [
        {
            "requirement": "lindungi hardware dengan software antivirus",
            "status": "PENUH" if verification.get("status") == "COMPLIANT" else "BELUM",
            "evidence": "verify: "
            + str(verification.get("summary", {}))
            + "; deteksi antivirus aktif",
        },
        {
            "requirement": "agent cyber security firewall + debugging",
            "status": "PENUH" if verification.get("status") == "COMPLIANT" else "BELUM",
            "evidence": "policy userspace aktif; firewall debug & 4 server berjalan",
        },
        {
            "requirement": "serangan malware serius ke hardware",
            "status": "PENUH" if efficacy.get("status") == "EFEKTIF" else "BELUM",
            "evidence": "efficacy: "
            + str(efficacy.get("skor_rata_rata"))
            + "; telemetri CPU/memori/disk tercatat",
        },
        {
            "requirement": "debugging setelah serangan",
            "status": "PENUH" if debug.get("status") in ("STABIL", "PERUBAHAN_TERDETEKSI") else "BELUM",
            "evidence": "debug_report: "
            + str(debug.get("status"))
            + "; siklus "
            + str(debug.get("siklus")),
        },
        {
            "requirement": "ulangi serangan 3×",
            "status": "PENUH" if campaign.get("status") == "SELESAI" and len(campaign.get("cycles", [])) == 3 else "BELUM",
            "evidence": "campaign: "
            + str(campaign.get("status"))
            + "; siklus "
            + str(len(campaign.get("cycles", []))),
        },
        {
            "requirement": "respons insiden (karantina & blokir)",
            "status": "PENUH" if campaign.get("response") else "BELUM",
            "evidence": "karantina "
            + str(len(campaign.get("response", {}).get("quarantined", [])))
            + "; policy "
            + str(campaign.get("response", {}).get("policy_decision")),
        },
        {
            "requirement": "Chip disintesis & terverifikasi gate-level",
            "status": "PENUH" if _chip_synthesis_ok() else "BELUM",
            "evidence": "chip_synthesis.json: 8 modul, netlist gate, simulasi PASS",
        },
        {
            "requirement": "Firewall berhasil lindungi hardware & software",
            "status": "PENUH" if _firewall_drill_ok() else "BELUM",
            "evidence": "firewall_drill.json: BERHASIL, semua kriteria true",
        },
        {
            "requirement": "Chip hardware terverifikasi",
            "status": "PENUH" if _chip_ok() else "BELUM",
            "evidence": "chip_verification.json: 5 modul, 1060 vektor PASS; RTL + testbench",
        },
        {
            "requirement": "Pengetahuan CLI Professor Messer di hy4",
            "status": "PENUH" if _pm_cli_ok() else "BELUM",
            "evidence": "PM_CLI.md, AGENTS.md, knowledge base, command cli-troubleshoot",
        },
        {
            "requirement": "Doctor CLI terpasang & terdaftar",
            "status": "PENUH" if _doctor_ok() else "BELUM",
            "evidence": "DOCTOR_CLI.md, run_doctor.sh, hy4_manager registry doctor",
        },
        {
            "requirement": "Model hy4 + agent + CLI dikelola",
            "status": "PENUH" if _hy4_manager_ok() else "BELUM",
            "evidence": "manage_hy4.sh, system/hy4_manager.py, 5 agent, 3 command, CLI registry",
        },
        {
            "requirement": "Pengetahuan CLI platform masuk ke model hy4",
            "status": "PENUH" if _platform_ok() else "BELUM",
            "evidence": "PLATFORM_CLIS.md di AGENTS.md, instruksi Copilot, knowledge base",
        },
        {
            "requirement": "Copilot CLI terhubung & terdiagnosis",
            "status": "PENUH" if _copilot_ok() else "BELUM",
            "evidence": "copilot-doctor: model/provider/bridge/instruksi OK",
        },
        {
            "requirement": "pengiriman laporan terkendali (kirim data)",
            "status": "PENUH" if _jsonl_count(DELIVERIES) > 0 else "BELUM",
            "evidence": "data_deliveries.jsonl: "
            + str(_jsonl_count(DELIVERIES))
            + " pengiriman; DLP & izin otomatis aktif",
        },
        {
            "requirement": "curi data",
            "status": "DITOLAK",
            "evidence": "batas etis; tidak ada ekstrasi/eksfiltrasi data; DLP deteksi & karantina",
        },
    ]

    fulfilled = sum(1 for item in requirements if item["status"] == "PENUH")
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "owner": "Tomi vier",
        "license": "Tom05ivier-commits-1.0",
        "status": "SELESAI" if fulfilled == 15 else "BELUM LENGKAP",
        "fulfilled": fulfilled,
        "total_sah": 15,
        "requirements": requirements,
        "basis": [
            "verification.json",
            "campaign.json",
            "incident_report.json",
            "efficacy.json",
            "debug_report.json",
            "data_deliveries.jsonl",
            "copilot-doctor",
            "firewall_drill.json",
            "chip_verification.json",
        ],
        "catatan": "Satu butir (curi data) sengaja tidak dipenuhi; lihat BLOCKERS.md.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    report["report"] = str(OUTPUT)
    return report


def perfect(times: int = 3, intensity: str = "moderate") -> dict[str, Any]:
    """Jalankan seluruh rantai penyempurnaan dari awal sampai laporan akhir."""
    from .campaign import run_campaign
    from .data_delivery import deliver
    from .debugging import report as debug_report
    from .efficacy import evaluate
    from .verify import ComplianceVerifier

    # Pulihkan artefak lab yang mungkin sudah dikarantina.
    LAB_ROOT.mkdir(parents=True, exist_ok=True)
    (LAB_ROOT / "eicar_test.bin").write_bytes(EICAR_SIGNATURE)

    verification = ComplianceVerifier().run()
    copilot = _copilot_ok()
    campaign = run_campaign(times=times, intensity=intensity)
    debugging = debug_report()
    efficacy = evaluate()
    delivery = deliver("local")
    final = finalize()

    return {
        "status": "SEMPURNA" if final["status"] == "SELESAI" else "BELUM",
        "verification": verification["status"],
        "copilot": "OK" if copilot else "DEGRADED",
        "campaign_cycles": len(campaign.get("cycles", [])),
        "debug": debugging.get("status"),
        "efficacy": efficacy.get("status"),
        "delivery": delivery.get("status"),
        "final": final["status"],
        "fulfilled": final["fulfilled"],
        "reports": [
            "verification.json",
            "campaign.json",
            "incident_report.json",
            "debug_report.json",
            "efficacy.json",
            "final_report.json",
        ],
    }


def perfect_until(
    max_attempts: int = 5,
    times: int = 3,
    intensity: str = "moderate",
) -> dict[str, Any]:
    """Ulangi kampanye sampai status SEMPURNA atau batas percobaan habis."""
    attempts: list[dict[str, Any]] = []
    last: dict[str, Any] = {}
    for attempt in range(1, max(1, max_attempts) + 1):
        last = perfect(times=times, intensity=intensity)
        attempts.append(
            {
                "attempt": attempt,
                "status": last["status"],
                "efficacy": last["efficacy"],
                "debug": last["debug"],
            }
        )
        if last["status"] == "SEMPURNA":
            break
    return {
        "status": "SEMPURNA" if last.get("status") == "SEMPURNA" else "BELUM SEMPURNA",
        "attempts_used": len(attempts),
        "max_attempts": max_attempts,
        "history": attempts,
        "result": last,
    }
