# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian panduan & gerbang tagihan Copilot CLI (tanpa pembayaran)."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import security.copilot_billing as cb  # noqa: E402
import tools.copilot_billing_reminder as reminder  # noqa: E402


def _token(action: str = "status", ttl: int = 60) -> str:
    now = time.time()
    return json.dumps(
        {
            "token_id": "uji-tagihan",
            "issued_by": "Tomi vier",
            "action": action,
            "issued_at": now,
            "expires_at": now + ttl,
        }
    )


class CopilotBillingTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._orig_audit, self._orig_config = cb.AUDIT, reminder.CONFIG
        cb.AUDIT = Path(self._tmp.name) / "copilot_billing.jsonl"
        reminder.CONFIG = Path(self._tmp.name) / "billing.json"

    def tearDown(self) -> None:
        cb.AUDIT, reminder.CONFIG = self._orig_audit, self._orig_config
        self._tmp.cleanup()

    def test_guide_and_status_have_no_secrets(self) -> None:
        guide = cb.guide()
        self.assertIn("https://github.com/settings/billing", json.dumps(guide))
        self.assertIn("tidak menyimpan data pembayaran", json.dumps(guide))
        status = cb.status()
        self.assertIsInstance(status["cli_tersedia"], bool)
        self.assertEqual(status["status_langganan"], "TIDAK DAPAT DITENTUKAN OFFLINE")

    def test_payment_always_denied_without_written_letter(self) -> None:
        token = _token("payment")
        result = cb.authorize("payment", token)
        self.assertEqual(result["status"], "DITOLAK")
        self.assertNotIn(token, json.dumps(result))
        self.assertNotIn(token, cb.AUDIT.read_text(encoding="utf-8"))

    def test_token_validation(self) -> None:
        self.assertEqual(cb.authorize("status", _token())["status"], "DIIZINKAN")
        self.assertEqual(cb.authorize("status", _token("record-confirmation"))["status"], "DITOLAK")
        self.assertEqual(cb.authorize("status", _token(ttl=301))["status"], "DITOLAK")
        expired = json.loads(_token())
        expired["issued_at"] = time.time() - 600
        expired["expires_at"] = time.time() - 300
        self.assertEqual(cb.authorize("status", json.dumps(expired))["status"], "DITOLAK")

    def test_record_and_history(self) -> None:
        cb.record("INV-2026-11/001")
        entries = cb.history()
        self.assertTrue(entries)
        self.assertIn("INV-2026-11/001", json.dumps(entries))
        self.assertNotIn("kartu", json.dumps(entries).lower())

    def test_reminder_local_only(self) -> None:
        today = date(2026, 11, 21)
        self.assertEqual(reminder.report(today)["status"], "BELUM DISETEL")
        reminder.write_config("2026-12-15", "Copilot-Pro")
        self.assertEqual(oct(reminder.CONFIG.stat().st_mode & 0o777), "0o600")
        self.assertEqual(reminder.report(today)["status"], "AMAN")
        reminder.write_config("2026-11-25")
        self.assertEqual(reminder.report(today)["status"], "MENDEKAT")
        reminder.write_config("2026-11-20")
        self.assertEqual(reminder.report(today)["status"], "JATUH TEMPO")
        self.assertIn("credentials/billing.json", (ROOT / ".gitignore").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
