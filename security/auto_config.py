# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#  Penerapan konfigurasi otomatis terbatas sesuai surat izin.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .auto_approval import AutoApproval
from .privacy import has_signature
from .blue.policy import FirewallPolicy

ROOT = Path(__file__).resolve().parents[1]
LETTER = ROOT / "surat-izin-konfigurasi-otomatis.md"
CONFIG_FILE = ROOT / "system" / "config.env"
AUDIT = ROOT / "security" / "reports" / "auto_configs.jsonl"
SIGNATURE = "(__signature__)"

NUMERIC_KEYS = {
    "firewall.deny_port": (1, 65535),
    "firewall.allow_port": (1, 65535),
    "system.interval": (1, 86400),
}
CHOICE_KEYS = {
    "workflow.name": ("harian", "kampanye", "lengkap"),
    "delivery.channel": ("local", "webhook"),
}
DENIED_PREFIXES = ("license.", "authorization.", "network.", "data.", "signature.")


def _validate(key: str, value: str) -> tuple[bool, str]:
    if any(key.startswith(prefix) for prefix in DENIED_PREFIXES):
        return False, "Kunci termasuk kategori yang dilarang surat izin."
    if key in NUMERIC_KEYS:
        low, high = NUMERIC_KEYS[key]
        try:
            number = int(value)
        except ValueError:
            return False, f"Nilai '{value}' bukan angka."
        if not low <= number <= high:
            return False, f"Nilai harus antara {low} dan {high}."
        return True, str(number)
    if key in CHOICE_KEYS:
        if value not in CHOICE_KEYS[key]:
            return False, f"Nilai harus salah satu dari {CHOICE_KEYS[key]}."
        return True, value
    return False, f"Kunci '{key}' tidak tercantum dalam Lampiran 1 surat izin."


def _read_config() -> dict[str, str]:
    result: dict[str, str] = {}
    if CONFIG_FILE.exists():
        for line in CONFIG_FILE.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.startswith("#"):
                key, _, value = line.partition("=")
                result[key.strip()] = value.strip()
    return result


def _write_config(values: dict[str, str]) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        "\n".join(f"{key}={value}" for key, value in sorted(values.items())) + "\n",
        encoding="utf-8",
    )


def apply(key: str, value: str, dry_run: bool = False) -> dict[str, Any]:
    """Terapkan konfigurasi otomatis bila izin & validasi lolos."""
    approval = AutoApproval().approve("config")
    if not approval["approved"]:
        return {"status": "DITOLAK", "reason": approval["reason"]}
    if not LETTER.exists() or not has_signature(LETTER.read_text(encoding="utf-8")):
        return {"status": "DITOLAK", "reason": "Surat izin konfigurasi tidak valid."}

    valid, normalized = _validate(key, value)
    if not valid:
        return {"status": "DITOLAK", "reason": normalized}

    current = _read_config()
    old = current.get(key, "")
    record: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "key": key,
        "old_value": old,
        "new_value": normalized,
        "dry_run": dry_run,
        "approval_id": approval["id"],
        "signature": SIGNATURE,
        "status": "DITERAPKAN" if not dry_run else "SIMULASI",
    }

    if not dry_run:
        if key == "firewall.deny_port":
            FirewallPolicy().deny_port(int(normalized))
        elif key == "firewall.allow_port":
            FirewallPolicy().allow_port(int(normalized))
        else:
            env_key = {
                "workflow.name": "WORKFLOW_NAME",
                "delivery.channel": "AGENTY_DELIVERY_CHANNEL",
                "system.interval": "WORKFLOW_INTERVAL",
            }[key]
            current[env_key] = normalized
            _write_config(current)

        AUDIT.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record
