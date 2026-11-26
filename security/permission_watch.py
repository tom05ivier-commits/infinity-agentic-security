# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Penjadwal read-only pemeriksa kedaluwarsa izin tertulis.

Layanan `process` ini dijalankan supervisor. Ia tidak menerbitkan izin,
tidak memperpanjang masa berlaku, dan tidak menyalin tanda tangan baru.
"""

from __future__ import annotations

import argparse
import signal
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from security.permission_automation import check, write_report  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Watchdog izin tertulis")
    parser.add_argument("--interval", type=float, default=3600.0)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args(argv)

    stop = False

    def handle(_signum: int, _frame: object) -> None:
        nonlocal stop
        stop = True

    signal.signal(signal.SIGTERM, handle)
    signal.signal(signal.SIGINT, handle)

    interval = max(60.0, args.interval)
    while not stop:
        report = check()
        write_report(report)
        if args.once:
            return 0
        deadline = time.monotonic() + interval
        while not stop and time.monotonic() < deadline:
            time.sleep(min(1.0, deadline - time.monotonic()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
