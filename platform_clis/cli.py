# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#" CLI untuk Platform Engineering Scorecard.

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from platform_clis.clis import CRITERIA, TOP10, inventory, score  # noqa: E402


def context_markdown() -> str:
    """Keluaran yang bisa ditempel ke konteks model hy4."""
    lines = [
        "## Platform Engineering CLIs (AI Agent Era)",
        "",
        "Sumber: https://stackgen.com/blog/top-10-clis-for-platform-engineers (3 Jul 2026).",
        "",
        "Top 10: "
        + ", ".join(f"{i['rank']}. {i['name']}" for i in TOP10),
        "",
        "Kriteria automation-friendly: " + ", ".join(CRITERIA) + ".",
        "",
        "Model aktif: **hy4-flash-free** (opencode/hy4-flash-free) — CLI ini adalah",
        "contoh nyata kategori #10 dan dipakai untuk memahami konteks ini.",
        "",
        "Prinsip: agents memakai CLI sebagai execution layer; utamakan JSON/YAML,",
        "plan/dry-run, idempotensi, exit code yang dapat diprediksi, kredensial",
        "berjangka, dan review manusia sebelum perubahan infra.",
        "",
    ]
    for item in inventory():
        status = item["installed_binary"] or "tidak terpasang"
        lines.append(f"- {item['rank']}. {item['name']}: {status} — {item['note']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Platform CLI Scorecard")
    parser.add_argument("command", choices=("list", "doctor", "score", "context"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.command == "context":
        print(context_markdown())
    elif args.command == "list":
        data = inventory()
        if args.json:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            for item in data:
                print(f"{item['rank']:2}. {item['name']:26} {item['installed_binary'] or '-'}")
    elif args.command == "doctor":
        data = inventory()
        installed = [i["name"] for i in data if i["installed"]]
        print(
            json.dumps(
                {
                    "status": "OK" if installed else "DEGRADED",
                    "total": len(data),
                    "installed": installed,
                    "missing": [i["name"] for i in data if not i["installed"]],
                    "criteria": list(CRITERIA),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    elif args.command == "score":
        data = [score(item) for item in inventory()]
        print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
