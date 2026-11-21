# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Perlindungan antivirus real-time untuk hardware.

Memantau direktori yang diamankan, memindai berkas baru/berubah, dan
mengarantina artefak terinfeksi secara otomatis. Berjalan dengan polling
terbatas agar aman di lingkungan laboratorium.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any

from ..common.logging import audit, get_logger
from .antivirus_agent import AntivirusAgent

logger = get_logger("blue.monitor")

MAX_SECONDS = 60.0
MIN_INTERVAL = 0.1


class FileMonitor:
    """Pemantau filesystem dengan deteksi & karantina otomatis."""

    def __init__(
        self,
        directory: Path,
        antivirus: AntivirusAgent | None = None,
        auto_quarantine: bool = True,
        interval: float = 0.5,
    ) -> None:
        self.directory = Path(directory)
        self.antivirus = antivirus or AntivirusAgent()
        self.auto_quarantine = auto_quarantine
        self.interval = max(interval, MIN_INTERVAL)
        self.detections: list[dict[str, Any]] = []
        self._baseline = self._snapshot()
        self._stop = threading.Event()

    def _snapshot(self) -> dict[str, tuple[int, int]]:
        snapshot: dict[str, tuple[int, int]] = {}
        if not self.directory.exists():
            return snapshot
        for path in self.directory.rglob("*"):
            if path.is_file():
                try:
                    stat = path.stat()
                    snapshot[str(path)] = (stat.st_mtime_ns, stat.st_size)
                except OSError:
                    continue
        return snapshot

    def poll_once(self) -> list[dict[str, Any]]:
        """Satu siklus pemindaian; kembalikan deteksi baru."""
        current = self._snapshot()
        changes = set(current) - set(self._baseline)
        changed = [
            path
            for path in current
            if path in self._baseline and current[path] != self._baseline[path]
        ]
        self._baseline = current
        found: list[dict[str, Any]] = []

        for raw in sorted(set(changes) | set(changed)):
            path = Path(raw)
            result = self.antivirus.scan_file(path)
            if not result.infected:
                continue
            quarantined = None
            if self.auto_quarantine:
                moved = self.antivirus.quarantine(path)
                quarantined = str(moved) if moved else None
            entry = {
                "file": str(path),
                "findings": [f.to_dict() for f in result.findings],
                "quarantined": quarantined,
                "timestamp": time.time(),
            }
            self.detections.append(entry)
            found.append(entry)
            audit(
                logger,
                "monitor.detected",
                file=str(path),
                quarantined=quarantined,
                findings=len(result.findings),
            )
        return found

    def run(self, seconds: float) -> None:
        """Jalankan pemantauan selama ``seconds`` atau sampai ``stop()``."""
        seconds = min(max(seconds, 0.0), MAX_SECONDS)
        deadline = time.monotonic() + seconds
        while not self._stop.is_set() and time.monotonic() < deadline:
            self.poll_once()
            self._stop.wait(self.interval)
        audit(logger, "monitor.stopped", detections=len(self.detections))

    def start(self, seconds: float) -> threading.Thread:
        """Jalankan monitor di thread latar belakang."""
        thread = threading.Thread(
            target=self.run, args=(seconds,), daemon=True, name="av-monitor"
        )
        thread.start()
        return thread

    def stop(self) -> None:
        self._stop.set()

    def report(self) -> dict[str, Any]:
        return {
            "directory": str(self.directory),
            "detections": len(self.detections),
            "auto_quarantine": self.auto_quarantine,
            "events": self.detections,
        }
