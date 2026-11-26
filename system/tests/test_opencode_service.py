# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian pendaftaran server API OpenCode di supervisor."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.infinity_connectivity import COMPONENTS  # noqa: E402
from system.opencode_watch import discover  # noqa: E402
from system.supervisor import validate_services  # noqa: E402


def registry() -> dict:
    return json.loads((ROOT / "system" / "services.json").read_text(encoding="utf-8"))


class OpenCodeServiceTests(unittest.TestCase):
    def test_registry_memiliki_opencode(self) -> None:
        entry = next((s for s in registry()["services"] if s["name"] == "opencode"), None)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["kind"], "http")
        self.assertEqual(entry["port"], 8786)
        self.assertEqual(entry["health"], "/health")
        self.assertEqual(entry["command"], ["bash", "scripts/opencode_serve.sh"])

    def test_registry_memiliki_instansi_tambahan(self) -> None:
        entry = next((s for s in registry()["services"] if s["name"] == "opencode-42337"), None)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["kind"], "http")
        self.assertEqual(entry["port"], 42337)
        self.assertEqual(entry["health"], "/health")
        self.assertEqual(entry["command"], ["bash", "scripts/opencode_serve.sh", "42337"])

    def test_registry_memiliki_watchdog(self) -> None:
        entry = next((s for s in registry()["services"] if s["name"] == "opencode-watch"), None)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["kind"], "process")
        self.assertEqual(entry["command"], ["python3", "system/opencode_watch.py", "loop"])

    def test_registry_valid(self) -> None:
        self.assertEqual(validate_services(registry()["services"]), [])

    def test_wrapper_mendukung_port_argumen(self) -> None:
        text = (ROOT / "scripts" / "opencode_serve.sh").read_text(encoding="utf-8")
        self.assertIn('${1:-${AGENTY_OPENCODE_PORT:-8786}}', text)
        self.assertIn('exec "$OPENCODE_BIN_VALUE" serve', text)

    def test_wrapper_dan_rtl_tersedia(self) -> None:
        self.assertTrue((ROOT / "scripts" / "opencode_serve.sh").is_file())
        self.assertTrue((ROOT / "chip" / "rtl" / "srv_opencode.v").is_file())
        self.assertTrue((ROOT / "chip" / "rtl" / "srv_opencode_42337.v").is_file())
        self.assertTrue((ROOT / "chip" / "rtl" / "srv_opencode_watch.v").is_file())
        self.assertTrue((ROOT / "system" / "opencode_watch.py").is_file())
        self.assertTrue((ROOT / "system" / "opencode_service.md").is_file())

    def test_komponen_konektivitas_terdaftar(self) -> None:
        names = {item["name"] for item in COMPONENTS}
        self.assertIn("opencode", names)
        self.assertIn("opencode-42337", names)
        self.assertIn("opencode-watch", names)
        item = next(i for i in COMPONENTS if i["name"] == "opencode")
        self.assertEqual(item["service"], "opencode")

    @unittest.skipUnless(Path("/proc").is_dir(), "/proc tidak tersedia")
    def test_discover_tidak_memasukkan_instansi_sesi(self) -> None:
        for item in discover():
            raw = Path(f"/proc/{item['pid']}/cmdline").read_bytes()
            self.assertNotIn(b"--service", raw.replace(b"\0", b" "))

    @unittest.skipUnless(Path("/proc").is_dir(), "/proc tidak tersedia")
    def test_semua_server_tercakup(self) -> None:
        registered = {
            int(s["port"])
            for s in registry()["services"]
            if s.get("kind") == "http" and str(s.get("port", "")).isdigit()
        }
        watcher = any(s["name"] == "opencode-watch" for s in registry()["services"])
        self.assertTrue(watcher)
        for item in discover():
            self.assertTrue(
                item["port"] in registered or watcher,
                f"port {item['port']} tidak diawasi",
            )


if __name__ == "__main__":
    unittest.main()
