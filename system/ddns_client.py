# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Klien Dynamic DNS publik dengan gerbang izin eksplisit.

Tidak ada permintaan jaringan otomatis. Token dibaca dari environment saat
eksekusi dan tidak pernah dicetak, diaudit, atau disimpan. TTL maksimal 300
detik sesuai batas otorisasi workspace.
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "security" / "reports" / "ddns_actions.jsonl"
LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"
MAX_TTL = 300
PROVIDERS = {
    "duckdns": {
        "env": "DUCKDNS_TOKEN",
        "endpoint": "https://www.duckdns.org/update",
    },
    "freedns": {
        "env": "FREEDNS_TOKEN",
        "endpoint": "https://freedns.afraid.org/dynamic/update.php",
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _audit(action: str, detail: dict[str, Any]) -> None:
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    entry = {"timestamp": _now(), "action": action, **detail,
             "license": LICENSE, "owner": OWNER}
    with AUDIT.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def status() -> dict[str, Any]:
    """Status konfigurasi boolean saja; nilai token tidak pernah dibaca keluar."""
    return {
        "providers": {
            name: {"configured": bool(os.environ.get(info["env"]))}
            for name, info in PROVIDERS.items()
        },
        "max_ttl": MAX_TTL,
        "automatic_updates": False,
        "license": LICENSE,
        "owner": OWNER,
    }


def _url(provider: str, token: str, domain: str) -> str:
    info = PROVIDERS[provider]
    if provider == "duckdns":
        query = urllib.parse.urlencode({"domains": domain, "token": token, "ip": ""})
        return info["endpoint"] + "?" + query
    return info["endpoint"] + "?" + urllib.parse.urlencode({"token": token})


def update(
    provider: str,
    domain: str,
    authorize: bool = False,
    ttl: int = MAX_TTL,
    opener: Any = None,
) -> dict[str, Any]:
    """Perbarui alamat IP dinamis. Hanya dengan `--authorize` eksplisit."""
    if provider not in PROVIDERS:
        raise ValueError(f"penyedia tidak dikenal: {provider}")
    if not authorize:
        raise PermissionError("update DDNS memerlukan --authorize eksplisit")
    ttl = int(ttl)
    if not 1 <= ttl <= MAX_TTL:
        raise ValueError(f"TTL harus 1..{MAX_TTL} detik")
    token = os.environ.get(PROVIDERS[provider]["env"], "")
    if not token:
        raise RuntimeError("token penyedia tidak tersedia di environment")
    if not domain or any(ch in domain for ch in "\r\n?&"):
        raise ValueError("domain tidak valid")

    request = urllib.request.Request(
        _url(provider, token, domain),
        headers={"User-Agent": "IT-Agenty-DDns/1.0"},
    )
    http = opener or urllib.request.urlopen
    with http(request, timeout=min(30, ttl)) as response:
        body = response.read(256).decode("utf-8", errors="replace").strip()
    ok = body.lower().startswith("ok")
    result = {
        "status": "OK" if ok else "GAGAL",
        "provider": provider,
        "domain": domain,
        "ttl": ttl,
        "response": "OK" if ok else "respons bukan OK",
    }
    _audit("ddns-update", {
        "provider": provider, "domain": domain, "ttl": ttl,
        "status": result["status"],
    })
    return result
