# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
# CLI untuk Infinity Advanced Computer.

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from advanced.engine import AdvancedComputer  # noqa: E402
from advanced.knowledge import KnowledgeBase  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="advanced_cli.py", description="Infinity Advanced Computer"
    )
    parser.add_argument(
        "command",
        choices=("status", "knowledge", "search", "run", "until", "memory"),
        help="status, knowledge, search, run sekali, loop tanpa batas, atau memori",
    )
    parser.add_argument("goal", nargs="?", default="status sistem")
    parser.add_argument("--authorize", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args(argv)

    computer = AdvancedComputer()
    if args.command == "status":
        print(json.dumps(computer.perceive(), indent=2, ensure_ascii=False))
    elif args.command == "knowledge":
        print(json.dumps(computer.knowledge.stats(), indent=2, ensure_ascii=False))
    elif args.command == "search":
        print(json.dumps(computer.knowledge.search(args.goal), indent=2, ensure_ascii=False))
    elif args.command == "run":
        result = computer.run(args.goal, authorize=args.authorize)
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    elif args.command == "until":
        if args.limit is not None:
            import os

            os.environ["AGENTY_MAX_ITERATIONS"] = str(args.limit)
        result = computer.run_until(args.goal, authorize=args.authorize)
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    elif args.command == "memory":
        print(json.dumps(computer.history[-20:], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
