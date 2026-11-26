# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#" Izin & audit pengelolaan akun GitHub (token tidak pernah diekspos).

from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .auto_approval import AutoApproval
from .privacy import has_signature

ROOT = Path(__file__).resolve().parents[1]
LETTER = ROOT / "surat-izin-github.md"
AUDIT = ROOT / "security" / "reports" / "github_actions.jsonl"
COPILOT_CONFIG = Path("/root/.copilot/config.json")
SIGNATURE = "(__signature__)"
ACCOUNT = "tom05ivier-commits"

ALLOWED: dict[str, str] = {
    "repo-list": "Membaca daftar repository milik akun",
    "repo-read": "Membaca isi repository milik akun",
    "repo-create": "Membuat repository baru",
    "repo-push": "Push ke repository milik akun",
    "repo-status": "Membaca status/commit repository",
}

DENIED = {
    "token-export",
    "password-change",
    "profile-change",
    "repo-delete",
    "repo-transfer",
    "third-party-access",
}


class GitHubAccount:
    """Verifikasi izin dan jejak audit aksi GitHub."""

    def __init__(self) -> None:
        self.letter_valid = LETTER.exists() and has_signature(self._read_letter())

    @staticmethod
    def _read_letter() -> str:
        try:
            return LETTER.read_text(encoding="utf-8")
        except OSError:
            return ""

    @staticmethod
    def allowlist() -> dict[str, str]:
        return ALLOWED

    @staticmethod
    def _token() -> str:
        """Ambil token dari config Copilot tanpa mencetaknya."""
        if not COPILOT_CONFIG.exists():
            return ""
        try:
            text = COPILOT_CONFIG.read_text(encoding="utf-8")
            text = "\n".join(
                line for line in text.splitlines()
                if not line.strip().startswith("//")
            )
            data = json.loads(text)
            tokens = data.get("authTokens", {})
            key = next(
                (k for k in tokens if k.endswith(ACCOUNT) and not k.endswith(":github")),
                None,
            ) or next(iter(tokens), None)
            return tokens[key].get("token", "") if key else ""
        except (OSError, json.JSONDecodeError, AttributeError):
            return ""

    def ready(self) -> dict[str, Any]:
        return {
            "letter_valid": self.letter_valid,
            "token_available": bool(self._token()),
            "account": ACCOUNT,
        }

    def authorize(self, action: str) -> dict[str, Any]:
        approval = AutoApproval().approve("github")
        record: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "account": ACCOUNT,
            "letter": LETTER.name,
            "letter_valid": self.letter_valid,
            "approval_id": approval["id"],
            "signature": SIGNATURE,
        }
        if not self.letter_valid:
            record.update(status="DITOLAK", reason="Surat izin GitHub tidak valid.")
        elif action in DENIED:
            record.update(status="DITOLAK", reason="Aksi dilarang oleh surat izin.")
        elif action not in ALLOWED:
            record.update(status="DITOLAK", reason="Aksi tidak dalam Lampiran 1.")
        elif not approval["approved"]:
            record.update(status="DITOLAK", reason=approval["reason"])
        elif not self._token():
            record.update(status="DITOLAK", reason="Token tidak tersedia.")
        else:
            record.update(
                status="DIIZINKAN",
                scope=ALLOWED[action],
                note="Token tetap di ~/.copilot/config.json; tidak diekspos.",
            )
        AUDIT.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    def list_repos(self) -> dict[str, Any]:
        """Contoh aksi repo-list; hanya nama repository yang dikembalikan."""
        authorized = self.authorize("repo-list")
        if authorized["status"] != "DIIZINKAN":
            return authorized
        request = urllib.request.Request(
            f"https://api.github.com/users/{ACCOUNT}/repos?per_page=100",
            headers={
                "Authorization": f"Bearer {self._token()}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "Infinity-Security/1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
            return {
                "status": "OK",
                "account": ACCOUNT,
                "repos": [item.get("name") for item in data],
            }
        except Exception as exc:  # noqa: BLE001
            return {"status": "ERROR", "error": type(exc).__name__}
