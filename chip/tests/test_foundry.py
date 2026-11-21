# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian paket penawaran fabrikasi."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chip.foundry.outreach import list_partners  # noqa: E402


class FoundryTests(unittest.TestCase):
    def test_partners_listed(self) -> None:
        partners = list_partners()
        self.assertEqual(len(partners), 5)
        ids = {p["id"] for p in partners}
        self.assertIn("tinytapeout", ids)
        self.assertIn("skywater", ids)

    def test_docs_present(self) -> None:
        base = ROOT / "chip" / "foundry"
        for name in (
            "README.md", "FOUNDRIES.md", "OUTREACH_EMAIL.md",
            "OUTREACH_ID.md", "SUBMISSION_CHECKLIST.md", "TRACKER.md",
        ):
            self.assertTrue((base / name).exists(), name)

    def test_drafts_generated(self) -> None:
        base = ROOT / "chip" / "foundry"
        for partner in list_partners():
            path = base / f"outreach_{partner['id']}.md"
            self.assertTrue(path.exists(), path)

    def test_tracker_is_honest(self) -> None:
        text = (ROOT / "chip" / "foundry" / "TRACKER.md").read_text()
        self.assertIn("DRAFT SIAP", text)
        self.assertIn("BELUM DIKIRIM", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
