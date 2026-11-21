# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Policy engine firewall userspace.

Ketika kernel firewall tidak tersedia (container tanpa CAP_NET_ADMIN), aturan
tetap disimpan, dievaluasi, dan dipakai oleh agen pertahanan. Ini BUKAN
pengganti packet filtering kernel; ini lapisan kebijakan yang dapat diaudit.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from ..common.config import SECURITY_ROOT

DEFAULT_POLICY_PATH = SECURITY_ROOT / "firewall" / "rules.json"


class FirewallPolicy:
    """Kumpulan aturan yang dipersistenkan dalam JSON."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path) if path else DEFAULT_POLICY_PATH
        self.rules: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        empty: dict[str, Any] = {
            "version": 1,
            "license": "Tom05ivier-commits-1.0",
            "blocked_ips": [],
            "denied_ports": [],
            "allowed_ports": [],
        }
        if not self.path.exists():
            return empty
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return empty
        for key in ("blocked_ips", "denied_ports", "allowed_ports"):
            data.setdefault(key, [])
        return data

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(self.rules, handle, indent=2, ensure_ascii=False)
            os.replace(temp_name, self.path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    def block_ip(self, ip: str) -> None:
        if ip not in self.rules["blocked_ips"]:
            self.rules["blocked_ips"].append(ip)
            self.save()

    def unblock_ip(self, ip: str) -> None:
        if ip in self.rules["blocked_ips"]:
            self.rules["blocked_ips"].remove(ip)
            self.save()

    def deny_port(self, port: int, protocol: str = "tcp") -> None:
        entry = f"{protocol}/{port}"
        if entry not in self.rules["denied_ports"]:
            self.rules["denied_ports"].append(entry)
            self.save()

    def allow_port(self, port: int, protocol: str = "tcp") -> None:
        entry = f"{protocol}/{port}"
        if entry not in self.rules["allowed_ports"]:
            self.rules["allowed_ports"].append(entry)
            self.save()

    def evaluate(self, ip: str, port: int, protocol: str = "tcp") -> str:
        """Kembalikan 'DENY' atau 'ALLOW' sesuai aturan tersimpan."""
        if ip in self.rules["blocked_ips"]:
            return "DENY"
        if f"{protocol}/{port}" in self.rules["denied_ports"]:
            return "DENY"
        if f"{protocol}/{port}" in self.rules["allowed_ports"]:
            return "ALLOW"
        return "ALLOW"

    def summary(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "blocked_ips": len(self.rules["blocked_ips"]),
            "denied_ports": len(self.rules["denied_ports"]),
            "allowed_ports": len(self.rules["allowed_ports"]),
        }
