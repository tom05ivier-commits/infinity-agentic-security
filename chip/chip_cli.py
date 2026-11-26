# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""CLI verifikasi desain chip."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from chip.reference import MODULES, verify_all  # noqa: E402


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Chip verification CLI")
    parser.add_argument(
        "command",
        choices=(
            "list", "agent", "verify", "synth", "tapeout", "foundry", "iverilog",
            "score", "soc", "firewall", "server-chip", "ai-chip", "neuro25",
            "neuro25-agent", "custom-agents", "fleet",
        ),
    )
    parser.add_argument(
        "--force", action="store_true",
        help="paksa verifikasi ulang chip kustom (abaikan cache)",
    )
    args = parser.parse_args()
    if args.command == "server-chip":
        # Alias diperlukan: tanpa ini, impor lokal menimpa ``verify_all``
        # global di seluruh fungsi dan cabang ``verify`` gagal dengan
        # UnboundLocalError (Python mengikat nama impor ke scope fungsi).
        from chip.server_chip_reference import verify_all as server_verify_all

        report = server_verify_all()
        print(json.dumps({
            "status": report["status"],
            "servers": report["servers"],
            "vectors": report["vectors"],
            "fabrication": report["fabrication"],
            "license": "Tom05ivier-commits-1.0",
        }, indent=2, ensure_ascii=False))
        if report["status"] != "PASS":
            raise SystemExit(1)
    elif args.command == "firewall":
        from chip.firewall_drill import run as drill
        from chip.firewall_iverilog import run as sim

        d = drill()
        s = sim()
        report = {
            "drill": {
                "status": d["status"],
                "vectors": d["verifikasi"]["vektor"],
                "mutants_detected": d["mutation_testing"]["terdeteksi"],
            },
            "iverilog": {
                "status": s["status"],
                "vectors": s["vectors"],
                "errors": s["errors"],
                "reasons": s["reasons"],
            },
            "status": "PASS" if d["status"] == "PASS" and s["status"] in ("PASS", "SKIP") else "FAIL",
            "fabrication": "NOT_READY",
            "license": "Tom05ivier-commits-1.0",
        }
        print(json.dumps(report, indent=2, ensure_ascii=False))
        if report["status"] == "FAIL":
            raise SystemExit(1)
    elif args.command == "soc":
        from chip.reference import verify_module

        result = verify_module("tom05_soc")
        meta = json.loads((ROOT / "hy4_chip.json").read_text(encoding="utf-8"))
        entry = next(m for m in meta["modules"] if m["name"] == "tom05_soc")
        print(
            json.dumps(
                {
                    "name": "tom05_soc",
                    "target": entry.get("target"),
                    "rtl": entry["rtl"],
                    "function": entry["function"],
                    "description": entry.get("description"),
                    "status": result["status"],
                    "vectors": result["vectors"],
                    "mismatches": result["mismatches"],
                    "license": "Tom05ivier-commits-1.0",
                    "fabrication": "NOT_READY",
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        if result["status"] != "PASS":
            raise SystemExit(1)
    elif args.command == "ai-chip":
        from chip.reference import verify_module

        result = verify_module("tom05_ai_accel")
        meta = json.loads((ROOT / "hy4_chip.json").read_text(encoding="utf-8"))
        entry = next(m for m in meta["modules"] if m["name"] == "tom05_ai_accel")
        print(
            json.dumps(
                {
                    "name": "tom05_ai_accel",
                    "target": entry.get("target"),
                    "inspiration": entry.get("inspiration"),
                    "rtl": entry["rtl"],
                    "function": entry["function"],
                    "description": entry.get("description"),
                    "status": result["status"],
                    "vectors": result["vectors"],
                    "mismatches": result["mismatches"],
                    "license": "Tom05ivier-commits-1.0",
                    "fabrication": entry.get("fabrication", "NOT_READY"),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        if result["status"] != "PASS":
            raise SystemExit(1)
    elif args.command == "neuro25-agent":
        from chip.neuro25_agent import AGENT_MARKDOWN, describe

        print(json.dumps({**describe(), "definition": AGENT_MARKDOWN},
                         indent=2, ensure_ascii=False))
    elif args.command == "fleet":
        from chip.neuro25_fleet import report

        data = report()
        print(json.dumps({
            "status": data["status"],
            "agents": data["agents"]["count"],
            "neuro25": data["neuro25"],
            "allowed": data["allowed"],
            "denied": data["denied"],
            "note": data["note"],
            "license": data["license"],
        }, indent=2, ensure_ascii=False))
        if data["status"] != "PASS":
            raise SystemExit(1)
    elif args.command == "custom-agents":
        # Alias wajib: impor lokal `verify_all` akan menimpa global dan
        # membuat cabang `verify` gagal dengan UnboundLocalError.
        from chip.custom_agents_reference import verify_all as custom_verify_all

        report = custom_verify_all(force=args.force)
        print(json.dumps({
            "status": report["status"],
            "agents": report["agents"],
            "vectors": report["vectors"],
            "cached": report.get("cached", False),
            "fabrication": report["fabrication"],
            "license": "Tom05ivier-commits-1.0",
            "results": [
                {"agent": item["agent"], "chip": item["chip"],
                 "acc": item["acc"], "status": item["status"],
                 "mismatches": item["mismatches"]}
                for item in report["results"]
            ],
        }, indent=2, ensure_ascii=False))
        if report["status"] != "PASS":
            raise SystemExit(1)
    elif args.command == "neuro25":
        from chip.neuro25_verify import build

        report = build()
        print(
            json.dumps(
                {
                    "name": report["name"],
                    "module": report["module"],
                    "status": report["status"],
                    "cognitive_stages": report["cognitive_stages"],
                    "profile": report["profile"],
                    "evidence": report["evidence"],
                    "safety": report["safety"],
                    "fabrication": report["fabrication"],
                    "clinical_validation": report["clinical_validation"],
                    "medical_device": report["medical_device"],
                    "disclaimer": report["disclaimer"],
                    "report": "chip/reports/neuro25.json",
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        if report["status"] != "PASS":
            raise SystemExit(1)
    elif args.command == "list":
        print(json.dumps(sorted(MODULES), indent=2))
    elif args.command == "agent":
        from chip.chip_agent import AGENT_MARKDOWN, describe

        print(
            json.dumps(
                {**describe(), "definition": AGENT_MARKDOWN},
                indent=2,
                ensure_ascii=False,
            )
        )
    elif args.command == "score":
        from chip.scorecard import build

        report = build()
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "grade": report["grade"],
                    "score": report["score"],
                    "failed": report["failed"],
                    "report": "chip/reports/chip_score.json",
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        if report["score"] != 100:
            raise SystemExit(1)
    elif args.command == "foundry":
        from chip.foundry.outreach import list_partners

        print(json.dumps(list_partners(), indent=2, ensure_ascii=False))
    elif args.command == "tapeout":
        from chip.tapeout.build_tapeout import build

        result = build()
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "archive": result["archive"],
                    "files": result["files"],
                    "fabrication_status": "NOT_READY",
                },
                indent=2,
            )
        )
    elif args.command == "iverilog":
        from chip.iverilog_check import run

        result = run()
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "compiler": result["compiler"],
                    "lint_warnings": result["lint_warnings"],
                    "compile_warnings": result["compile_warnings"],
                    "modules": len(result["modules"]),
                    "vectors": result["vectors"],
                    "checks": result["checks"],
                    "errors": result["errors"],
                    "vcd": (result["vcd"] or {}).get("path"),
                    "duration_ms": result["duration_ms"],
                    "reasons": result["reasons"],
                    "report": "chip/reports/iverilog.json",
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        if result["status"] == "FAIL":
            raise SystemExit(1)
    elif args.command == "synth":
        from chip.synth_report import write

        report = write()
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "modules": len(report["modules"]),
                    "total_cells": report["total_cells"],
                    "report": "chip/reports/chip_synthesis.json",
                },
                indent=2,
            )
        )
    else:
        print(json.dumps(verify_all(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
