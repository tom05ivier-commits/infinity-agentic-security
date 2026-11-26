# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian koneksi OpenCode ↔ OpenCode AI dan data bersama."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.shared_data import verify  # noqa: E402


class SharedDataTests(unittest.TestCase):
    def test_connected(self) -> None:
        report = verify()
        self.assertEqual(report["status"], "TERHUBUNG")
        self.assertEqual(report["workspace"], str(ROOT))

    def test_all_checks_ok(self) -> None:
        report = verify()
        for name, check in report["checks"].items():
            self.assertEqual(check["status"], "OK", f"{name}: {check}")

    def test_mcp_has_required_servers(self) -> None:
        mcp = verify()["checks"]["mcp"]
        self.assertGreaterEqual(mcp["connected"], 7)
        for name in ("filesystem", "github", "new-mcp-server", "playwright"):
            self.assertIn(name, mcp["servers"])

    def test_no_credentials_in_report(self) -> None:
        text = str(verify())
        for token in ("password", "api_key", "authorization", "bearer "):
            self.assertNotIn(token, text.lower())

    def test_mirror_retry_pulih_dari_jendela_publish(self) -> None:
        """Berkas cermin yang muncul pada percobaan kedua tetap dianggap OK."""
        import tempfile
        from unittest import mock

        from security.privacy import redact
        from system import shared_data

        with tempfile.TemporaryDirectory() as tmp:
            staging = Path(tmp)
            # Bangun cermin sempurna dari sumber lokal agar deterministik.
            for rel in shared_data.SHARED_FILES:
                raw = (ROOT / rel).read_bytes()
                if rel == "AGENTS.md":
                    raw = redact(raw.decode("utf-8")).encode("utf-8")
                dst = staging / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(raw)

            original = shared_data._compare_mirror_once
            calls = {"n": 0}

            def sekali_gagal(redactor: object) -> tuple[list[str], dict[str, str]]:
                calls["n"] += 1
                if calls["n"] == 1:
                    # Simulasikan satu berkas belum tersalin saat publish.
                    return ([shared_data.SHARED_FILES[0] + ": berkas tidak ada"], {})
                return original(redactor)

            with mock.patch.object(shared_data, "PUBLISH", staging), \
                    mock.patch.object(shared_data, "_compare_mirror_once",
                                      side_effect=sekali_gagal), \
                    mock.patch.object(shared_data.time, "sleep"):
                report = shared_data.check_mirror()

        self.assertEqual(report["status"], "OK")
        self.assertEqual(calls["n"], 2)
        self.assertEqual(len(report["digests"]), len(shared_data.SHARED_FILES))


if __name__ == "__main__":
    unittest.main(verbosity=2)
