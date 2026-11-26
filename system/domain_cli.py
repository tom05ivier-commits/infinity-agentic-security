# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""CLI manajer domain lokal `*.agenty.local`."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system import domain_manager as dm  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manajer domain lokal IT Agenty")
    parser.add_argument(
        "command",
        choices=(
            "suggest", "list", "add", "remove", "hosts", "install", "status",
            "guide", "ddns-status", "ddns-update",
        ),
    )
    parser.add_argument("--name")
    parser.add_argument("--seed", default="agenty")
    parser.add_argument("--count", type=int, default=8)
    parser.add_argument("--target", default="127.0.0.1")
    parser.add_argument("--path")
    parser.add_argument("--provider", default="duckdns")
    parser.add_argument("--domain")
    parser.add_argument("--ttl", type=int, default=300)
    parser.add_argument("--authorize", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.command == "suggest":
            payload = {"domains": dm.suggest(args.seed, args.count)}
        elif args.command == "list":
            payload = {"domains": dm.list_domains()}
        elif args.command == "add":
            if not args.name:
                raise ValueError("--name diperlukan")
            payload = dm.add(args.name, args.target)
        elif args.command == "remove":
            if not args.name:
                raise ValueError("--name diperlukan")
            payload = {"removed": dm.remove(args.name)}
        elif args.command == "hosts":
            payload = {"lines": dm.hosts_block()}
        elif args.command == "install":
            payload = dm.install_hosts(
                Path(args.path) if args.path else None, args.authorize
            )
        elif args.command == "status":
            payload = dm.status()
        elif args.command == "guide":
            payload = {"providers": dm.guide()}
        elif args.command == "ddns-status":
            from system.ddns_client import status as ddns_status

            payload = ddns_status()
        else:
            from system.ddns_client import update as ddns_update

            if not args.domain:
                raise ValueError("--domain diperlukan")
            payload = ddns_update(args.provider, args.domain, args.authorize, args.ttl)
    except (ValueError, PermissionError, OSError) as exc:
        print(json.dumps({"status": "GAGAL", "error": str(exc)}, ensure_ascii=False))
        return 1

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
