# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
# Pemeriksaan capability kernel untuk enforcement firewall nyata.

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

CAP_NET_ADMIN = 12

CAP_NAMES: dict[int, str] = {
    0: "CAP_CHOWN",
    1: "CAP_DAC_OVERRIDE",
    2: "CAP_DAC_READ_SEARCH",
    3: "CAP_FOWNER",
    4: "CAP_FSETID",
    5: "CAP_KILL",
    6: "CAP_SETGID",
    7: "CAP_SETUID",
    8: "CAP_SETPCAP",
    9: "CAP_LINUX_IMMUTABLE",
    10: "CAP_NET_BIND_SERVICE",
    11: "CAP_NET_BROADCAST",
    12: "CAP_NET_ADMIN",
    13: "CAP_NET_RAW",
    14: "CAP_IPC_LOCK",
    15: "CAP_IPC_OWNER",
    16: "CAP_SYS_MODULE",
    17: "CAP_SYS_RAWIO",
    18: "CAP_SYS_CHROOT",
    19: "CAP_SYS_PTRACE",
    20: "CAP_SYS_PACCT",
    21: "CAP_SYS_BOOT",
    22: "CAP_SYS_NICE",
    23: "CAP_SYS_RESOURCE",
    24: "CAP_SYS_TIME",
    25: "CAP_SYS_TTY_CONFIG",
    26: "CAP_MKNOD",
    27: "CAP_LEASE",
    28: "CAP_AUDIT_WRITE",
    29: "CAP_AUDIT_CONTROL",
    30: "CAP_SETFCAP",
    31: "CAP_MAC_OVERRIDE",
    32: "CAP_MAC_ADMIN",
    33: "CAP_SYSLOG",
    34: "CAP_WAKE_ALARM",
    35: "CAP_BLOCK_SUSPEND",
    36: "CAP_AUDIT_READ",
}


def read_capabilities() -> dict[str, str]:
    """Baca capability dari /proc/self/status."""
    result: dict[str, str] = {}
    try:
        lines = Path("/proc/self/status").read_text().splitlines()
    except OSError:
        return result
    for line in lines:
        if line.startswith("Cap"):
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


def bounding_capabilities() -> list[str]:
    """Daftar capability yang masih mungkin diperoleh proses ini."""
    caps = read_capabilities()
    try:
        bounded = int(caps.get("CapBnd", "0"), 16)
    except ValueError:
        return []
    return [
        name
        for bit, name in CAP_NAMES.items()
        if bounded & (1 << bit)
    ]


def has_cap_net_admin() -> bool:
    """Cek apakah CAP_NET_ADMIN tersedia pada proses saat ini."""
    caps = read_capabilities()
    effective = caps.get("CapEff", "0")
    try:
        return bool(int(effective, 16) & (1 << CAP_NET_ADMIN))
    except ValueError:
        return False


def can_gain_capability() -> bool:
    """Cek apakah capability mungkin diperoleh sama sekali (bounding set)."""
    caps = read_capabilities()
    bounded = caps.get("CapBnd", "0")
    try:
        return bool(int(bounded, 16) & (1 << CAP_NET_ADMIN))
    except ValueError:
        return False


def backend_available() -> bool:
    """Cek keberadaan biner firewall."""
    return any(
        shutil.which(name)
        for name in ("iptables", "iptables-legacy", "nft", "ip6tables")
    )


def status() -> dict[str, Any]:
    """Laporan lengkap kesiapan firewall kernel."""
    caps = read_capabilities()
    capable = has_cap_net_admin()
    gainable = can_gain_capability()
    backend = backend_available()
    enforced = capable and backend
    if enforced:
        remediation = "Firewall kernel siap; jalankan FirewallAgent(dry_run=False)."
    elif not gainable:
        remediation = (
            "CapBnd tidak memuat CAP_NET_ADMIN. Capability harus diberikan "
            "oleh host/container runtime; tidak bisa ditambahkan dari dalam."
        )
    elif not capable:
        remediation = (
            "Berikan CAP_NET_ADMIN pada proses, mis. via "
            "docker run --cap-add=NET_ADMIN atau setcap file capability."
        )
    else:
        remediation = "Pasang iptables atau nftables pada sistem."
    return {
        "cap_net_admin": capable,
        "can_gain": gainable,
        "bounding_capabilities": bounding_capabilities(),
        "backend_available": backend,
        "kernel_enforcement": enforced,
        "effective_mode": "kernel-iptables" if enforced else "userspace-policy",
        "capabilities": caps,
        "remediation": remediation,
    }
