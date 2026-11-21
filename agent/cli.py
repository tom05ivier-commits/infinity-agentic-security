# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
# CLI untuk Agent Computer.

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.brain import AgentBrain  # noqa: E402
from agent.runtime import STATE_PATH, AgentRuntime  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agent_cli.py", description="Agent Computer — IT Agenty"
    )
    parser.add_argument(
        "command",
        choices=("run", "plan", "tasks", "history"),
        help="jalankan tujuan, lihat rencana, daftar tugas, atau riwayat",
    )
    parser.add_argument("goal", nargs="?", default="status sistem")
    parser.add_argument(
        "--authorize",
        action="store_true",
        help="izinkan tugas ofensif (serangan) — butuh izin tertulis",
    )
    args = parser.parse_args(argv)

    if args.command == "tasks":
        print(json.dumps(AgentBrain.available_tasks(), indent=2))
    elif args.command == "plan":
        steps = AgentBrain().plan(args.goal, authorize=args.authorize)
        print(json.dumps([s.__dict__ for s in steps], indent=2, ensure_ascii=False))
    elif args.command == "history":
        if STATE_PATH.exists():
            data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
            summary = [
                {
                    "goal": run["goal"],
                    "status": run["status"],
                    "plan": run["plan"],
                }
                for run in data.get("runs", [])
            ]
            print(json.dumps(summary, indent=2, ensure_ascii=False))
        else:
            print("[]")
    elif args.command == "run":
        result = AgentRuntime().run(args.goal, authorize=args.authorize)
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
