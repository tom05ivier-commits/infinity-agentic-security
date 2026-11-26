# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Agen inventaris hardware & antarmuka jaringan.

Membaca informasi dari /sys dan /proc tanpa dependensi eksternal, sehingga
tetap bekerja pada lingkungan container minimal.
"""

from __future__ import annotations

import platform
from pathlib import Path
from typing import Any

from ..common.logging import audit, get_logger

logger = get_logger("blue.hardware")


class HardwareAgent:
    """Mengumpulkan informasi hardware dan antarmuka jaringan."""

    def system_info(self) -> dict[str, Any]:
        info = {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor() or "unknown",
            "python": platform.python_version(),
        }
        audit(logger, "hardware.system_info", **info)
        return info

    def network_interfaces(self) -> list[dict[str, str]]:
        """Enumerasi antarmuka jaringan dari /sys/class/net."""
        interfaces: list[dict[str, str]] = []
        base = Path("/sys/class/net")
        if not base.exists():
            audit(logger, "hardware.net.unavailable")
            return interfaces

        try:
            entries = sorted(base.iterdir())
        except (PermissionError, OSError) as exc:
            # Container sering membatasi /sys; gunakan fallback /proc/net/dev.
            audit(logger, "hardware.net.restricted", reason=str(exc))
            return self._fallback_interfaces()

        for path in entries:
            name = path.name
            try:
                address = (path / "address").read_text().strip()
                state = (path / "operstate").read_text().strip()
            except (PermissionError, OSError):
                continue
            interfaces.append(
                {"name": name, "mac": address, "state": state}
            )
        audit(logger, "hardware.net.enumerated", count=len(interfaces))
        return interfaces

    @staticmethod
    def _fallback_interfaces() -> list[dict[str, str]]:
        """Fallback ketika /sys/class/net tidak dapat dibaca."""
        import socket

        interfaces: list[dict[str, str]] = []
        dev = Path("/proc/net/dev")
        try:
            lines = dev.read_text().splitlines()[2:]
        except (PermissionError, OSError, IndexError):
            lines = []
        for line in lines:
            if ":" not in line:
                continue
            name = line.split(":", 1)[0].strip()
            interfaces.append({"name": name, "mac": "n/a", "state": "unknown"})

        if not interfaces:
            # Container Android membatasi /proc/net; pakai alamat lokal.
            try:
                address = socket.gethostbyname(socket.gethostname())
            except OSError:
                address = "127.0.0.1"
            interfaces.append(
                {
                    "name": "loopback(local)",
                    "mac": address,
                    "state": "up",
                    "source": "socket-fallback",
                }
            )
            audit(logger, "hardware.net.socket_fallback", address=address)
        return interfaces

    def cpu_summary(self) -> dict[str, Any]:
        """Ringkasan CPU dari /proc/cpuinfo."""
        physical = 0
        try:
            for line in Path("/proc/cpuinfo").read_text().splitlines():
                if line.lower().startswith("physical id"):
                    physical += 1
        except OSError:
            pass
        return {
            "logical_cpus": physical or 1,
            "architecture": platform.machine(),
        }

    def report(self) -> dict[str, Any]:
        return {
            "system": self.system_info(),
            "cpu": self.cpu_summary(),
            "interfaces": self.network_interfaces(),
        }
