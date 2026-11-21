# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#  Mesin alur kerja otomatis: langkah, otorisasi, audit, dan daemon.

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from security.auto_approval import AutoApproval  # noqa: E402

AUDIT = ROOT / "security" / "reports" / "workflow_runs.jsonl"

WORKFLOWS: dict[str, list[dict[str, Any]]] = {
    "harian": [
        {"name": "verifikasi", "task": "verify", "approval": "verify", "params": {}},
        {"name": "integritas", "task": "integrity", "approval": "integrity", "params": {}},
        {"name": "dlp", "task": "dlp", "approval": "dlp", "params": {}},
        {"name": "proteksi", "task": "protect", "approval": "campaign", "params": {"seconds": 3}},
    ],
    "kampanye": [
        {
            "name": "kampanye-3x",
            "task": "perfect",
            "approval": "campaign",
            "params": {"times": 3, "intensity": "moderate"},
        }
    ],
    "lengkap": [
        {"name": "verifikasi", "task": "verify", "approval": "verify", "params": {}},
        {
            "name": "sempurnakan",
            "task": "perfect",
            "approval": "campaign",
            "params": {"times": 3, "intensity": "moderate"},
        },
        {"name": "debug", "task": "debug", "approval": "debug", "params": {}},
        {"name": "efikasi", "task": "efficacy", "approval": "efficacy", "params": {}},
        {
            "name": "firewall-drill",
            "task": "firewall_drill",
            "approval": "campaign",
            "params": {},
        },
        {"name": "final", "task": "finalize", "approval": "finalize", "params": {}},
        {"name": "kirim", "task": "delivery", "approval": "delivery", "params": {}},
    ],
}


def _dispatch(step: dict[str, Any]) -> dict[str, Any]:
    task = step["task"]
    params = dict(step.get("params", {}))
    if task == "verify":
        from security.verify import ComplianceVerifier

        result = ComplianceVerifier().run()
        return {"status": result["status"], "summary": result["summary"]}
    if task == "integrity":
        from security.blue.integrity import IntegrityMonitor

        return IntegrityMonitor().check()
    if task == "dlp":
        from security.blue.dlp import exposure_report, scan_paths
        from security.common.config import LAB_ROOT

        return exposure_report(scan_paths([LAB_ROOT]))
    if task == "protect":
        from system.protection import ProtectionDaemon

        return ProtectionDaemon(seconds=params.get("seconds", 3)).run()
    if task == "perfect":
        from security.finalize import perfect

        result = perfect(**params)
        return {"status": result["status"], "fulfilled": result["fulfilled"]}
    if task == "debug":
        from security.debugging import report

        result = report()
        return {"status": result["status"], "siklus": result.get("siklus")}
    if task == "efficacy":
        from security.efficacy import evaluate

        result = evaluate()
        return {"status": result["status"], "skor": result.get("skor_rata_rata")}
    if task == "finalize":
        from security.finalize import finalize

        result = finalize()
        return {"status": result["status"], "fulfilled": result["fulfilled"]}
    if task == "firewall_drill":
        from security.firewall_drill import run_until_success

        result = run_until_success(max_attempts=3, intensity="moderate")
        return {
            "status": result["status"],
            "attempts": result["attempts"],
            "failed": result["failed"],
        }
    if task == "delivery":
        from security.data_delivery import deliver

        result = deliver(params.get("channel", "local"))
        return {"status": result["status"], "file": result.get("file")}
    return {"status": "ERROR", "error": f"tugas tidak dikenal: {task}"}


class WorkflowEngine:
    """Menjalankan alur kerja dengan izin otomatis dan jejak audit."""

    def __init__(self) -> None:
        self.approvals = AutoApproval()

    @staticmethod
    def names() -> list[str]:
        return sorted(WORKFLOWS)

    def run(self, name: str) -> dict[str, Any]:
        steps = WORKFLOWS.get(name)
        if not steps:
            return {"status": "ERROR", "error": f"alur kerja tidak dikenal: {name}"}
        started = time.monotonic()
        results: list[dict[str, Any]] = []
        for step in steps:
            approval = self.approvals.approve(step.get("approval", step["task"]))
            if not approval["approved"]:
                results.append(
                    {
                        "name": step["name"],
                        "status": "DITOLAK",
                        "reason": approval["reason"],
                        "approval_id": approval["id"],
                    }
                )
                continue
            # Retry satu kali untuk kegagalan sementara (race dengan daemon).
            attempts = 0
            while True:
                attempts += 1
                try:
                    result = _dispatch(step)
                    status = result.get("status", "OK")
                except Exception as exc:  # noqa: BLE001
                    result, status = {"error": str(exc)}, "ERROR"
                if status not in ("ERROR", "FAILED") or attempts >= 2:
                    break
                time.sleep(0.2)
            result["attempts"] = attempts
            results.append(
                {
                    "name": step["name"],
                    "status": status,
                    "result": result,
                    "approval_id": approval["id"],
                }
            )
        failed = any(
            item["status"] in ("ERROR", "DITOLAK", "FAILED", "BELUM LENGKAP")
            for item in results
        )
        report = {
            "status": "GAGAL" if failed else "SELESAI",
            "workflow": name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": round(time.monotonic() - started, 2),
            "steps": results,
        }
        AUDIT.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(report, ensure_ascii=False) + "\n")
        return report

    @staticmethod
    def history(limit: int = 10) -> list[dict[str, Any]]:
        if not AUDIT.exists():
            return []
        records = []
        for line in AUDIT.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return records[-limit:]


def daemon(name: str, interval: float) -> None:
    """Jalankan alur kerja berulang dengan jeda tertentu."""
    engine = WorkflowEngine()
    while True:
        report = engine.run(name)
        print(
            f"[{report['timestamp']}] {name}: {report['status']} "
            f"({report['duration_seconds']}s)",
            flush=True,
        )
        time.sleep(max(60.0, interval))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Infinity Workflow Engine")
    parser.add_argument("command", choices=("list", "run", "history", "daemon"))
    parser.add_argument("--name", default="harian")
    parser.add_argument("--interval", type=float, default=86400)
    args = parser.parse_args(argv)

    engine = WorkflowEngine()
    if args.command == "list":
        print(json.dumps(engine.names()))
    elif args.command == "run":
        print(json.dumps(engine.run(args.name), indent=2, ensure_ascii=False, default=str))
    elif args.command == "history":
        print(json.dumps(engine.history(), indent=2, ensure_ascii=False))
    elif args.command == "daemon":
        daemon(args.name, args.interval)
    return 0


if __name__ == "__main__":
    sys.exit(main())
