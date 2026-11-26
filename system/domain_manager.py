# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Manajer domain lokal `*.agenty.local` untuk layanan workspace IT Agenty.

Tidak mendaftar domain publik, tidak menghubungi DNS eksternal, dan tidak
membaca kredensial. Data disimpan di `system/reports/local_domains.json`.
Pemasangan ke `/etc/hosts` hanya terjadi lewat `--authorize` eksplisit.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "system" / "reports" / "local_domains.json"
HOSTS = Path("/etc/hosts")
AUDIT = ROOT / "security" / "reports" / "domain_actions.jsonl"
ROOT_DOMAIN = "agenty.local"
BEGIN = "# BEGIN AGENTY-LOCAL-DOMAINS"
END = "# END AGENTY-LOCAL-DOMAINS"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,31}$")
LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _valid_name(name: str) -> str:
    value = str(name).strip().lower()
    if not NAME_RE.match(value):
        raise ValueError("nama harus a-z0-9 dan tanda hubung, maksimal 32 karakter")
    return value


def _load() -> dict[str, Any]:
    try:
        data = json.loads(STORE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    if not isinstance(data, dict) or not isinstance(data.get("domains"), list):
        data = {"domains": []}
    data.setdefault("domains", [])
    return data


def _write(data: dict[str, Any]) -> None:
    STORE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STORE.with_suffix(".tmp")
    payload = {
        "license": LICENSE,
        "owner": OWNER,
        "root_domain": ROOT_DOMAIN,
        "domains": data["domains"],
    }
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(STORE)


def _audit(action: str, detail: dict[str, Any]) -> None:
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    entry = {"timestamp": _now(), "action": action, **detail,
             "license": LICENSE, "owner": OWNER}
    with AUDIT.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def fqdn(name: str) -> str:
    return f"{_valid_name(name)}.{ROOT_DOMAIN}"


def list_domains() -> list[dict[str, Any]]:
    """Daftar domain lokal yang dikelola (tanpa kredensial)."""
    return list(_load()["domains"])


def available(name: str) -> bool:
    try:
        host = fqdn(name)
    except ValueError:
        return False
    return not any(item.get("host") == host for item in list_domains())


def suggest(seed: str = "agenty", count: int = 8) -> list[dict[str, Any]]:
    """Saran nama unik dan deterministik dari seed, lengkap dengan status lokal."""
    amount = max(1, min(int(count), 24))
    results: list[dict[str, Any]] = []
    for index in range(amount):
        digest = hashlib.sha256(f"{seed}:{index}".encode("utf-8")).hexdigest()
        name = f"ai-{digest[:6]}"
        host = fqdn(name)
        results.append({
            "name": name,
            "host": host,
            "available": available(name),
            "seed": str(seed),
        })
    return results


def add(name: str, target: str = "127.0.0.1") -> dict[str, Any]:
    """Daftarkan subdomain lokal. Target harus alamat loopback."""
    host = fqdn(name)
    if not available(name):
        raise ValueError(f"{host} sudah terdaftar")
    if target not in ("127.0.0.1", "::1"):
        raise ValueError("target harus loopback (127.0.0.1 atau ::1)")
    data = _load()
    entry = {
        "name": _valid_name(name),
        "host": host,
        "target": target,
        "created_at": _now(),
    }
    data["domains"].append(entry)
    _write(data)
    _audit("domain-add", {"host": host, "target": target})
    return entry


def remove(name: str) -> bool:
    host = fqdn(name)
    data = _load()
    before = len(data["domains"])
    data["domains"] = [item for item in data["domains"] if item.get("host") != host]
    if len(data["domains"]) == before:
        return False
    _write(data)
    _audit("domain-remove", {"host": host})
    return True


def hosts_block() -> list[str]:
    """Baris blok `/etc/hosts` yang dikelola manajer ini."""
    lines = [BEGIN]
    for item in sorted(list_domains(), key=lambda row: row["host"]):
        lines.append(f"{item['target']}\t{item['host']}")
    lines.append(END)
    return lines


def install_hosts(path: Path | None = None, authorize: bool = False) -> dict[str, Any]:
    """Pasang blok ke hosts file. Mbutuhkan `--authorize` eksplisit."""
    if not authorize:
        raise PermissionError("pemasangan /etc/hosts memerlukan authorize eksplisit")
    target = Path(path) if path is not None else HOSTS
    original = target.read_text(encoding="utf-8") if target.exists() else ""
    kept: list[str] = []
    skip = False
    for line in original.splitlines():
        if line.strip() == BEGIN:
            skip = True
            continue
        if line.strip() == END:
            skip = False
            continue
        if not skip:
            kept.append(line)
    updated = "\n".join(kept + hosts_block()).rstrip("\n") + "\n"
    backup = target.with_suffix(target.suffix + ".agenty-backup")
    if target.exists() and not backup.exists():
        shutil.copy2(target, backup)
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(updated, encoding="utf-8")
    tmp.replace(target)
    _audit("hosts-install", {"path": str(target), "domains": len(list_domains())})
    return {
        "status": "OK",
        "path": str(target),
        "backup": str(backup) if backup.exists() else None,
        "domains": len(list_domains()),
    }


def status() -> dict[str, Any]:
    domains = list_domains()
    installed = False
    try:
        installed = BEGIN in HOSTS.read_text(encoding="utf-8")
    except OSError:
        installed = False
    return {
        "service": "domain",
        "root_domain": ROOT_DOMAIN,
        "domains": domains,
        "count": len(domains),
        "hosts_installed": installed,
        "fabrication": "NOT_APPLICABLE",
        "license": LICENSE,
        "owner": OWNER,
    }


def guide() -> list[dict[str, str]]:
    """Panduan penyedia domain gratis (read-only, tanpa janji resmi)."""
    return [
        {
            "name": "Local `*.agenty.local`",
            "type": "lokal",
            "usage": "generator ini + pemasangan blok /etc/hosts dengan izin eksplisit",
            "note": "Hanya berfungsi di perangkat ini; bukan domain publik.",
        },
        {
            "name": "DuckDNS",
            "type": "dynamic DNS publik",
            "usage": "System/ddns_client.py --provider duckdns --authorize",
            "note": "Butuh akun dan token milik Anda; tidak ada token bawaan.",
        },
        {
            "name": "FreeDNS (afraid.org)",
            "type": "dynamic DNS publik",
            "usage": "Daftar manual lalu pakai token di client DNS dinamis",
            "note": "Ketentuan penyedia berlaku; IT Agenty tidak menjamin ketersediaan.",
        },
        {
            "name": "No-IP",
            "type": "dynamic DNS publik",
            "usage": "Daftar manual, lalu perbarui host lewat klien resmi",
            "note": "Tier gratis memiliki batasan dan pembaharuan berkala.",
        },
    ]
