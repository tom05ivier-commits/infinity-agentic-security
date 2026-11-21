# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Agen firewall host berbasis iptables/nftables.

Secara default berjalan dalam mode ``dry_run`` sehingga tidak mengubah aturan
sistem. Perubahan nyata hanya terjadi bila operator secara eksplisit
menjalankan dengan ``dry_run=False`` dan memiliki hak root.
"""

from __future__ import annotations

import ipaddress
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any

from ..common.logging import audit, get_logger

logger = get_logger("blue.firewall")


@dataclass
class CommandResult:
    command: str
    executed: bool
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "command": self.command,
            "executed": self.executed,
            "returncode": self.returncode,
            "stdout": self.stdout[:500],
            "stderr": self.stderr[:500],
        }


class FirewallAgent:
    """Mengelola aturan firewall dengan mode kering (dry run) sebagai default."""

    def __init__(self, dry_run: bool = True, backend: str | None = None) -> None:
        self.dry_run = dry_run
        if backend:
            self.backend = backend
        else:
            self.backend = next(
                (
                    name
                    for name in ("iptables", "iptables-legacy")
                    if shutil.which(name)
                ),
                "iptables",
            )

    def _run(self, args: list[str]) -> CommandResult:
        command = " ".join([self.backend, *args])
        if self.dry_run:
            audit(logger, "firewall.dry_run", command=command)
            return CommandResult(command=command, executed=False)
        try:
            completed = subprocess.run(
                [self.backend, *args],
                check=False,
                capture_output=True,
                text=True,
                timeout=15,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            audit(logger, "firewall.error", command=command, error=str(exc))
            return CommandResult(
                command=command, executed=True, returncode=1, stderr=str(exc)
            )
        audit(
            logger,
            "firewall.applied",
            command=command,
            returncode=completed.returncode,
        )
        return CommandResult(
            command=command,
            executed=True,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    @staticmethod
    def _validate_ip(ip: str) -> str:
        try:
            return str(ipaddress.ip_address(ip))
        except ValueError as exc:
            raise ValueError(f"Alamat IP tidak valid: {ip}") from exc

    @staticmethod
    def _validate_port(port: int) -> int:
        if not 1 <= int(port) <= 65535:
            raise ValueError(f"Port tidak valid: {port}")
        return int(port)

    def list_rules(self) -> CommandResult:
        return self._run(["-S"])

    def block_ip(self, ip: str) -> CommandResult:
        return self._run(["-A", "INPUT", "-s", self._validate_ip(ip), "-j", "DROP"])

    def unblock_ip(self, ip: str) -> CommandResult:
        return self._run(["-D", "INPUT", "-s", self._validate_ip(ip), "-j", "DROP"])

    def allow_port(self, port: int, protocol: str = "tcp") -> CommandResult:
        if protocol not in ("tcp", "udp"):
            raise ValueError("Protokol harus 'tcp' atau 'udp'")
        return self._run(
            [
                "-A",
                "INPUT",
                "-p",
                protocol,
                "--dport",
                str(self._validate_port(port)),
                "-j",
                "ACCEPT",
            ]
        )

    def deny_port(self, port: int, protocol: str = "tcp") -> CommandResult:
        if protocol not in ("tcp", "udp"):
            raise ValueError("Protokol harus 'tcp' atau 'udp'")
        return self._run(
            [
                "-A",
                "INPUT",
                "-p",
                protocol,
                "--dport",
                str(self._validate_port(port)),
                "-j",
                "DROP",
            ]
        )
