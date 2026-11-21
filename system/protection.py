# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Daemon perlindungan hardware berkelanjutan.

Menyatukan tiga kontrol: antivirus real-time (karantina otomatis), policy
firewall userspace, dan korelasi SOC. Status ditulis secara periodik sehingga
dapat diaudit oleh sistem komputer terpadu.
"""

from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(WORKSPACE))

from security.blue.defense_agent import DefenseAgent  # noqa: E402
from security.blue.monitor import FileMonitor  # noqa: E402
from security.blue.policy import FirewallPolicy  # noqa: E402
from security.common.config import LAB_ROOT  # noqa: E402

STATUS_PATH = WORKSPACE / "system" / "reports" / "protection_status.json"


class ProtectionDaemon:
    """Menjalankan perlindungan hardware selama jendela waktu tertentu."""

    def __init__(self, seconds: float = 30.0, interval: float = 0.5) -> None:
        self.seconds = max(0.5, min(seconds, 300.0))
        self.interval = max(0.1, interval)
        self.policy = FirewallPolicy()
        self.defense = DefenseAgent()
        self.monitor = FileMonitor(
            LAB_ROOT, auto_quarantine=True, interval=self.interval
        )
        self._thread: threading.Thread | None = None
        self.history: list[dict[str, Any]] = []

    def apply_baseline(self) -> dict[str, Any]:
        """Terapkan policy dasar sebelum pemantauan dimulai."""
        self.policy.deny_port(23)
        self.policy.allow_port(22)
        self.policy.save()
        return self.policy.summary()

    def _write_status(self, baseline: dict[str, Any]) -> None:
        STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "baseline": baseline,
            "monitor": self.monitor.report(),
            "history": self.history,
        }
        STATUS_PATH.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def run(self) -> dict[str, Any]:
        """Jalankan daemon hingga selesai dan kembalikan hasil akhir."""
        baseline = self.apply_baseline()
        self._thread = self.monitor.start(seconds=self.seconds)
        deadline = time.monotonic() + self.seconds
        while time.monotonic() < deadline and self._thread.is_alive():
            self.history.append(
                {
                    "time": round(time.monotonic(), 3),
                    "detections": len(self.monitor.detections),
                    "policy": self.policy.summary(),
                }
            )
            self._write_status(baseline)
            time.sleep(min(1.0, self.interval))
        self.monitor.stop()
        if self._thread:
            self._thread.join(timeout=3)
        self.monitor.poll_once()
        self._write_status(baseline)
        return {
            "seconds": self.seconds,
            "baseline": baseline,
            "monitor": self.monitor.report(),
            "samples": len(self.history),
            "status_path": str(STATUS_PATH),
        }
