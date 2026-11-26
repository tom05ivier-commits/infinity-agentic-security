# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.1 — lihat file LICENSE di root proyek.
"""Pengujian peta konektivitas supervisor <-> seluruh workspace."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system import infinity_connectivity as ic  # noqa: E402


class InfinityConnectivityTests(unittest.TestCase):
    def test_manifest_covers_registry(self) -> None:
        services = {item.get("name") for item in ic.registry()}
        mapped = {item["service"] for item in ic.COMPONENTS if item.get("service")}
        self.assertEqual(services, mapped, "setiap layanan registry punya komponen")

    def test_server_components_are_managed(self) -> None:
        for item in ic.COMPONENTS:
            if item["kind"] in ("server", "process", "monitor"):
                self.assertTrue(item.get("service"), f"{item['name']} tanpa layanan")

    def test_component_paths_exist(self) -> None:
        for item in ic.COMPONENTS:
            self.assertTrue((ROOT / item["path"]).exists(), f"{item['name']}: {item['path']}")

    def test_graph_is_connected(self) -> None:
        graph = ic.build_graph()
        self.assertEqual(graph["terputus"], [])
        self.assertEqual(set(graph["terjangkau"]), set(graph["simpul"]))
        self.assertIn(["supervisor", "workspace"],
                      [sorted(pair) for pair in graph["sisi"]])

    def test_check_shape(self) -> None:
        result = ic.check()
        self.assertIn(result["status"], ("TERHUBUNG", "SEBAGIAN"))
        self.assertEqual(result["sumber_data"], str(ROOT))
        self.assertEqual(result["license"], "Tom05ivier-commits-1.0")
        self.assertGreater(result["graf"]["jumlah_sisi"], len(ic.COMPONENTS))
        self.assertEqual(result["masalah"]["path_hilang"], [])
        self.assertEqual(result["masalah"]["tanpa_layanan"], [])

    def test_sites_registered_and_public_is_http(self) -> None:
        services = {item["name"]: item for item in ic.registry()}
        self.assertEqual(services["sites"]["port"], 8769)
        self.assertEqual(services["sites"]["health"], "/health")
        self.assertEqual(services["public"]["kind"], "http")

    def test_report_write(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "laporan.json"
            with patch.object(ic, "REPORT", target):
                written = ic.write_report(ic.check())
            self.assertEqual(written, target)
            data = json.loads(target.read_text(encoding="utf-8"))
            self.assertIn("status", data)

    def test_no_credentials_in_report(self) -> None:
        text = json.dumps(ic.check(), ensure_ascii=False).lower()
        for marker in ("api_key", "password", "secret", "authorization"):
            self.assertNotIn(marker, text)


if __name__ == "__main__":
    unittest.main()
