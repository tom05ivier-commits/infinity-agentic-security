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
            "list", "verify", "synth", "tapeout", "foundry", "iverilog", "score"
        ),
    )
    args = parser.parse_args()
    if args.command == "list":
        print(json.dumps(sorted(MODULES), indent=2))
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
