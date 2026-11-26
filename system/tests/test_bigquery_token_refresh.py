# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Pengujian refresh token BigQuery MCP: mode 0600, audit, tanpa kebocoran."""

from __future__ import annotations

import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tools.bigquery_token_refresh as mod


class BigQueryTokenRefreshTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.config = base / "opencode.json"
        self.token = base / "bigquery_token.txt"
        self.audit = base / "audit.jsonl"
        self.config.write_text(json.dumps({
            "mcp": {"servers": {"bigquery": {
                "type": "remote", "url": "https://bigquery.googleapis.com/mcp",
                "disabled": True,
            }}},
        }), encoding="utf-8")
        self.patcher = (patch.object(mod, "CONFIG", self.config),
                        patch.object(mod, "TOKEN", self.token),
                        patch.object(mod, "AUDIT", self.audit))
        for p in self.patcher:
            p.start()

    def tearDown(self) -> None:
        for p in reversed(self.patcher):
            p.stop()
        self.tmp.cleanup()

    def test_status_tanpa_token(self) -> None:
        data = mod.status()
        self.assertFalse(data["token_ada"])
        self.assertFalse(data["mcp_aktif"])

    def test_refresh_butuh_authorize(self) -> None:
        with self.assertRaises(SystemExit):
            mod.refresh(False)

    def test_refresh_gagal_tidak_menyentuh_token(self) -> None:
        with patch.object(mod.subprocess, "run") as run:
            run.return_value.returncode = 1
            run.return_value.stdout = ""
            data = mod.refresh(True)
        self.assertEqual(data["status"], "DILEWATI")
        self.assertFalse(self.token.exists())
        self.assertIn("DILEWATI", self.audit.read_text(encoding="utf-8"))

    def test_refresh_berhasil_mengaktifkan_mcp(self) -> None:
        secret = "rahasia-token-xyz"
        with patch.object(mod.subprocess, "run") as run:
            run.return_value.returncode = 0
            run.return_value.stdout = secret + "\n"
            data = mod.refresh(True)
        self.assertEqual(data["status"], "DIPERBARUI")
        self.assertTrue(data["mcp_aktif"])
        self.assertTrue(data["mcp_baru_diaktifkan"])
        self.assertEqual(stat.S_IMODE(os.stat(self.token).st_mode), 0o600)
        cfg = json.loads(self.config.read_text(encoding="utf-8"))
        self.assertFalse(cfg["mcp"]["servers"]["bigquery"]["disabled"])
        self.assertNotIn(secret, self.audit.read_text(encoding="utf-8"))
        self.assertNotIn(secret, json.dumps(data))


class BigQueryProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.config = base / "opencode.json"
        self.token = base / "bigquery_token.txt"
        self.audit = base / "audit.jsonl"
        self.config.write_text(json.dumps({
            "mcp": {"servers": {"bigquery": {"disabled": True}}},
        }), encoding="utf-8")
        self.patcher = (patch.object(mod, "CONFIG", self.config),
                        patch.object(mod, "TOKEN", self.token),
                        patch.object(mod, "AUDIT", self.audit))
        for p in self.patcher:
            p.start()

    def tearDown(self) -> None:
        for p in reversed(self.patcher):
            p.stop()
        self.tmp.cleanup()

    def test_probe_tanpa_token(self) -> None:
        self.assertEqual(mod.probe()["status"], "DILEWATI")

    def test_probe_metadata_lengkap(self) -> None:
        self.token.write_text("rahasia-probe\n", encoding="utf-8")
        os.chmod(self.token, 0o600)
        body = "data:" + json.dumps({"result": {"tools": [
            {"name": f"https://docs.cloud.google.com/{n}"}
            for n in mod.METADATA_TOOLS
        ]}})
        with patch.object(mod.urllib.request, "urlopen") as urlopen:
            urlopen.return_value.__enter__.return_value.read.return_value = (
                body.encode("utf-8")
            )
            data = mod.probe()
        self.assertEqual(data["status"], "PASS")
        self.assertEqual(len(data["metadata_tersedia"]), 4)
        self.assertNotIn("rahasia-probe", json.dumps(data))
        self.assertNotIn("rahasia-probe", self.audit.read_text(encoding="utf-8"))

    def test_probe_metadata_tidak_lengkap(self) -> None:
        self.token.write_text("rahasia-probe\n", encoding="utf-8")
        os.chmod(self.token, 0o600)
        body = json.dumps({"result": {"tools": [{"name": "list_dataset_ids"}]}})
        with patch.object(mod.urllib.request, "urlopen") as urlopen:
            urlopen.return_value.__enter__.return_value.read.return_value = (
                body.encode("utf-8")
            )
            data = mod.probe()
        self.assertEqual(data["status"], "GAGAL")
        self.assertEqual(data["metadata_tersedia"], ["list_dataset_ids"])


class BigQueryGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.config = base / "opencode.json"
        self.token = base / "bigquery_token.txt"
        self.audit = base / "audit.jsonl"
        self.config.write_text(json.dumps({
            "mcp": {"servers": {"bigquery": {
                "url": mod.PROBE_URL,
                "headers": {"Authorization": "Bearer {file:~/.config/opencode/bigquery_token.txt}"},
                "disabled": True,
            }}},
        }), encoding="utf-8")
        self.patcher = (patch.object(mod, "CONFIG", self.config),
                        patch.object(mod, "TOKEN", self.token),
                        patch.object(mod, "AUDIT", self.audit))
        for p in self.patcher:
            p.start()

    def tearDown(self) -> None:
        for p in reversed(self.patcher):
            p.stop()
        self.tmp.cleanup()

    def test_guard_pass(self) -> None:
        self.token.write_text("secret-guard\n", encoding="utf-8")
        os.chmod(self.token, 0o600)
        data = mod.guard()
        self.assertEqual(data["status"], "PASS")

    def test_guard_gagal_bila_token_bocor_di_audit(self) -> None:
        self.token.write_text("secret-guard\n", encoding="utf-8")
        os.chmod(self.token, 0o600)
        self.audit.write_text('{"event":"bocor","token":"secret-guard"}\n',
                              encoding="utf-8")
        self.assertEqual(mod.guard()["status"], "FAIL")

    def test_probe_tolak_mode_token_lemah(self) -> None:
        self.token.write_text("secret-guard\n", encoding="utf-8")
        os.chmod(self.token, 0o644)
        with patch.object(mod.urllib.request, "urlopen") as urlopen:
            data = mod.probe()
        self.assertEqual(data["status"], "GAGAL")
        urlopen.assert_not_called()

    def test_probe_tolak_respons_besar(self) -> None:
        self.token.write_text("secret-guard\n", encoding="utf-8")
        os.chmod(self.token, 0o600)
        with patch.object(mod, "MAX_BODY", 4), \
             patch.object(mod.urllib.request, "urlopen") as urlopen:
            urlopen.return_value.__enter__.return_value.read.return_value = (
                b"data:{}"
            )
            data = mod.probe()
        self.assertEqual(data["status"], "GAGAL")
        self.assertIn("terlalu besar", data["alasan"])


if __name__ == "__main__":
    unittest.main()
