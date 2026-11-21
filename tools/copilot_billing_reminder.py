#!/usr/bin/env python3
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengingat lokal tagihan Copilot CLI — tanpa jaringan dan tanpa kredensial.

Konfigurasi disimpan di `credentials/billing.json` (mode 0600, ter-ignore).
Hanya tanggal jatuh tempo dan nama paket yang disimpan; tidak ada data kartu,
token, jumlah tagihan, atau informasi pribadi.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "credentials" / "billing.json"


def load_config() -> dict[str, Any]:
    try:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def days_until(value: str, today: date | None = None) -> int:
    target = date.fromisoformat(value)
    return (target - (today or date.today())).days


def write_config(renewal_date: str, plan: str = "") -> dict[str, Any]:
    date.fromisoformat(renewal_date)
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    data = {"renewal_date": renewal_date, "plan": plan[:60]}
    fd, tmp = tempfile.mkstemp(prefix="billing.", dir=str(CONFIG.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, 0o600)
        os.replace(tmp, CONFIG)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return data


def report(today: date | None = None) -> dict[str, Any]:
    config = load_config()
    value = config.get("renewal_date")
    if not value:
        return {
            "status": "BELUM DISETEL",
            "petunjuk": "python3 tools/copilot_billing_reminder.py --init YYYY-MM-DD",
        }
    try:
        remaining = days_until(str(value), today)
    except ValueError:
        return {"status": "TANGGAL TIDAK VALID", "petunjuk": "gunakan format YYYY-MM-DD"}
    if remaining < 0:
        status = "JATUH TEMPO"
    elif remaining <= 7:
        status = "MENDEKAT"
    else:
        status = "AMAN"
    return {
        "status": status,
        "hari_tersisa": remaining,
        "jatuh_tempo": value,
        "paket": config.get("plan", "-"),
        "catatan": "Pembayaran tetap manual; lihat docs/COPILOT-BILLING.md.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--init", metavar="YYYY-MM-DD", help="set tanggal jatuh tempo")
    parser.add_argument("--plan", default="", help="nama paket (opsional)")
    args = parser.parse_args(argv)
    if args.init:
        data = write_config(args.init, args.plan)
        print(json.dumps({"status": "TERSIMPAN", "renewal_date": data["renewal_date"]}, ensure_ascii=False))
        return 0
    print(json.dumps(report(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
