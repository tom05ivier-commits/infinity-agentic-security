# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""CLI otomatisasi surat izin tertulis (kategori rutin saja)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from security import permission_automation as pa  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Otomatisasi izin tertulis IT Agenty")
    parser.add_argument("command", choices=("issue", "list", "check", "categories"))
    parser.add_argument("--task")
    parser.add_argument("--ttl", type=int, default=pa.MAX_TTL)
    parser.add_argument("--reason", default="")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)

    if args.command == "issue":
        if not args.task:
            print(json.dumps({"status": "GAGAL", "error": "--task diperlukan"}))
            return 1
        payload = pa.issue(args.task, args.ttl, args.reason)
        code = 0 if payload["status"] == "OK" else 1
    elif args.command == "list":
        payload = {"letters": pa.letters(args.limit)}
        code = 0
    elif args.command == "check":
        payload = pa.check()
        code = 0
    else:
        payload = {
            "allowed": sorted(pa.ALLOWED),
            "denied": sorted(pa.DENIED),
            "max_ttl": pa.MAX_TTL,
            "valid_until": pa.VALID_UNTIL.isoformat(),
        }
        code = 0

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
