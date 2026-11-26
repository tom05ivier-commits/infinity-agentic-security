# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian NOTICE hak cipta terpisah Tom05 flash Free."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

NOTICE = ROOT / "TOM05-FLASH-FREE-NOTICE.md"


class Tom05CopyrightTests(unittest.TestCase):
    def test_notice_exists_with_required_statements(self) -> None:
        self.assertTrue(NOTICE.is_file())
        text = NOTICE.read_text(encoding="utf-8")
        for token in (
            "SPDX-License-Identifier: Tom05ivier-commits-1.0",
            "Copyright (c) 2026 Tomi vier",
            "Tom05 flash Free",
            "hukum hak cipta",
            "alias/proxy",
            "hy4-flash-free",
            "AGPL-3.0",
            "bukan model terlatih baru",
            "bukan pendaftaran",
            "Tidak ada tanda tangan",
            "LICENSE",
        ):
            self.assertIn(token, text, token)

    def test_notice_does_not_claim_upstream_copyright(self) -> None:
        text = NOTICE.read_text(encoding="utf-8")
        self.assertIn("tidak menciptakan hak cipta atas model", text)
        self.assertIn("tidak menggantikan lisensi mereka", text)
        self.assertNotIn("model terlatih Tom05", text)

    def test_catalog_points_to_notice(self) -> None:
        data = json.loads(
            (ROOT / "config" / "tom05-models.json").read_text(encoding="utf-8")
        )
        alias = next(a for a in data["aliases"] if a["id"] == "tom05-flash-free")
        self.assertEqual(alias["copyright_notice"], NOTICE.name)

    def test_active_license_unchanged(self) -> None:
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("Tom05ivier-commits", license_text)
        self.assertIn("Tomi vier", license_text)

    def test_provider_docs_mention_notice(self) -> None:
        text = (ROOT / "docs" / "PROVIDER-TOM05.md").read_text(encoding="utf-8")
        self.assertIn("TOM05-FLASH-FREE-NOTICE.md", text)
        self.assertIn("alias/proxy", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
