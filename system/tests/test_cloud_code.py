# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian pendaftaran layanan status Cloud Code di supervisor."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system import cloud_code  # noqa: E402
from system.infinity_connectivity import COMPONENTS  # noqa: E402
from system.supervisor import validate_services  # noqa: E402


class CloudCodeServiceTests(unittest.TestCase):
    def test_registry_memiliki_cloud_code(self) -> None:
        data = json.loads((ROOT / "system" / "services.json").read_text(encoding="utf-8"))
        entry = next((s for s in data["services"] if s["name"] == "cloud-code"), None)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["kind"], "http")
        self.assertEqual(entry["port"], 8785)
        self.assertEqual(entry["health"], "/health")
        self.assertEqual(entry["command"], ["python3", "system/cloud_code_service.py"])
        self.assertEqual(validate_services(data["services"]), [])

    def test_modul_dan_rtl_tersedia(self) -> None:
        self.assertTrue((ROOT / "system" / "cloud_code.py").is_file())
        self.assertTrue((ROOT / "system" / "cloud_code_service.py").is_file())
        self.assertTrue((ROOT / "scripts" / "cloud_code_install.sh").is_file())
        self.assertTrue((ROOT / "chip" / "rtl" / "srv_cloud_code.v").is_file())

    def test_kapabilitas_read_only(self) -> None:
        cap = cloud_code.capabilities()
        self.assertEqual(cap["service"], "cloud-code")
        self.assertEqual(cap["mutations"], [])
        self.assertIn("/health", cap["endpoints"])

    def test_komponen_konektivitas_terdaftar(self) -> None:
        names = {item["name"] for item in COMPONENTS}
        self.assertIn("cloud-code", names)
        item = next(i for i in COMPONENTS if i["name"] == "cloud-code")
        self.assertEqual(item["service"], "cloud-code")


if __name__ == "__main__":
    unittest.main()
