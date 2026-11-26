# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#" Generator email penawaran fabrikasi + tracker status (tanpa pengiriman otomatis).

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "OUTREACH_EMAIL.md"
TRACKER = HERE / "TRACKER.md"

PARTNERS: tuple[dict[str, str], ...] = (
    {
        "id": "tinytapeout",
        "name": "Tiny Tapeout",
        "program": "TTSKY26e / TTGF26c",
        "channel": "https://tinytapeout.com/chips/",
        "contact": "official submission portal",
        "priority": "1",
    },
    {
        "id": "chipfoundry",
        "name": "ChipFoundry / chipIgnite",
        "program": "CI2612 / CI2705",
        "channel": "https://chipfoundry.io/reservations",
        "contact": "official reservation/contact form",
        "priority": "2",
    },
    {
        "id": "skywater",
        "name": "SkyWater Technology",
        "program": "MPW S130 / S90LN",
        "channel": "https://www.skywatertechnology.com/services/multi-project-wafer-servies",
        "contact": "official MPW contact",
        "priority": "3",
    },
    {
        "id": "globalfoundries",
        "name": "GlobalFoundries",
        "program": "GlobalShuttle MPW",
        "channel": "https://gf.com/manufacturing/services/multi-project-wafer-program",
        "contact": "official contact us",
        "priority": "4",
    },
    {
        "id": "tower",
        "name": "Tower Semiconductor",
        "program": "MPW Shuttle",
        "channel": "https://towersemi.com/manufacturing/mpw-shuttle-program",
        "contact": "official contact form",
        "priority": "5",
    },
)


def generate(
    partner_id: str,
    owner: str = "",
    email: str = "",
) -> dict[str, Any]:
    partner = next((p for p in PARTNERS if p["id"] == partner_id), None)
    if not partner:
        raise ValueError(f"Mitra tidak dikenal: {partner_id}")
    owner = owner or os.environ.get("AGENTY_OUTREACH_OWNER", "")
    email = email or os.environ.get("AGENTY_OUTREACH_EMAIL", "")
    template = TEMPLATE.read_text(encoding="utf-8")
    text = (
        template.replace("[PARTNER NAME / MPW PROGRAM TEAM]", partner["name"])
        .replace("[YOUR NAME]", owner or "[NAME TO BE FILLED BY OWNER]")
        .replace("[YOUR EMAIL]", email or "[EMAIL TO BE FILLED BY OWNER]")
    )
    out = HERE / f"outreach_{partner_id}.md"
    out.write_text(text, encoding="utf-8")
    return {
        "partner": partner["name"],
        "file": str(out),
        "channel": partner["channel"],
        "owner_filled": bool(owner),
        "email_filled": bool(email),
    }


def list_partners() -> list[dict[str, str]]:
    return list(PARTNERS)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Foundry outreach generator")
    parser.add_argument("command", choices=("list", "generate", "all"))
    parser.add_argument("--id")
    parser.add_argument("--owner")
    parser.add_argument("--email")
    args = parser.parse_args()
    if args.command == "list":
        print(json.dumps(list_partners(), indent=2, ensure_ascii=False))
    elif args.command == "generate":
        print(
            json.dumps(
                generate(args.id or "", args.owner or "", args.email or ""),
                indent=2,
                ensure_ascii=False,
            )
        )
    elif args.command == "all":
        print(
            json.dumps(
                [
                    generate(p["id"], args.owner or "", args.email or "")
                    for p in PARTNERS
                ],
                indent=2,
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()
