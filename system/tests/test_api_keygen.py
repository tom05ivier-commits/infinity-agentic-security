# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian pembangkit kunci API aman (tanpa membocorkan nilai)."""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import system.api_keygen as kg  # noqa: E402


class ApiKeygenTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._env = Path(self._tmp.name) / "credentials" / ".env"
        self._audit = Path(self._tmp.name) / "security" / "reports" / "api_keygen.jsonl"
        self._orig_env, self._orig_audit = kg.ENV_FILE, kg.AUDIT_FILE
        kg.ENV_FILE, kg.AUDIT_FILE = self._env, self._audit
        self._orig_environ = dict(os.environ)

    def tearDown(self) -> None:
        kg.ENV_FILE, kg.AUDIT_FILE = self._orig_env, self._orig_audit
        os.environ.clear()
        os.environ.update(self._orig_environ)
        self._tmp.cleanup()

    def test_formats_and_lengths(self) -> None:
        self.assertEqual(len(kg.generate_key(256, "base64")), 44)
        self.assertEqual(len(kg.generate_key(256, "hex")), 64)
        self.assertEqual(len(kg.generate_key(256, "urlsafe")), 43)
        self.assertGreaterEqual(len(kg.generate_key(256, "alphanumeric")), 43)
        self.assertNotIn("=", kg.generate_key(256, "urlsafe"))

    def test_keys_are_unique_and_validated(self) -> None:
        keys = kg.generate_keys(256, "hex", 5)
        self.assertEqual(len(set(keys)), 5)
        with self.assertRaises(kg.KeygenError):
            kg.generate_key(999, "hex")
        with self.assertRaises(kg.KeygenError):
            kg.generate_keys(256, "hex", 101)

    def test_fingerprint_hides_value(self) -> None:
        key = kg.generate_key()
        self.assertNotIn(key, kg.fingerprint(key))
        self.assertEqual(len(kg.fingerprint(key)), 16)

    def test_set_load_and_permissions(self) -> None:
        meta = kg.set_api_key("AGENTY_API_KEY", strength=256, format_name="hex")
        loaded = kg.load_api_key("AGENTY_API_KEY")
        self.assertIsNotNone(loaded)
        self.assertEqual(len(loaded), 64)
        self.assertEqual(meta["sidik_jari"], kg.fingerprint(loaded))
        self.assertEqual(oct(self._env.stat().st_mode & 0o777), "0o600")
        self.assertNotIn(loaded, json.dumps(meta))

    def test_ensure_is_idempotent(self) -> None:
        first = kg.ensure_api_key("AGENTY_API_KEY")
        self.assertTrue(first["dibuat"])
        second = kg.ensure_api_key("AGENTY_API_KEY")
        self.assertFalse(second["dibuat"])
        self.assertEqual(first["sidik_jari"], second["sidik_jari"])

    def test_rotate_changes_key(self) -> None:
        first = kg.ensure_api_key("AGENTY_API_KEY")
        second = kg.rotate_api_key("AGENTY_API_KEY")
        self.assertNotEqual(first["sidik_jari"], second["sidik_jari"])

    def test_rotation_keeps_audit_history(self) -> None:
        kg.set_api_key("AGENTY_API_KEY")
        kg.rotate_api_key("AGENTY_API_KEY")
        lines = [json.loads(x) for x in self._audit.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([x["aksi"] for x in lines], ["set", "rotate"])
        self.assertNotEqual(lines[0]["sidik_jari"], lines[1]["sidik_jari"])

    def test_guard_clean_and_leak(self) -> None:
        root = Path(self._tmp.name)
        (root / ".gitignore").write_text("credentials/.env\n", encoding="utf-8")
        kg.set_api_key("AGENTY_API_KEY")
        clean = kg.guard("AGENTY_API_KEY", root=root)
        self.assertEqual(clean["status"], "AMAN")
        self.assertNotIn(kg.load_api_key("AGENTY_API_KEY"), json.dumps(clean))

        leaked = root / "catatan.md"
        leaked.write_text("bocor: " + kg.load_api_key("AGENTY_API_KEY"), encoding="utf-8")
        bad = kg.guard("AGENTY_API_KEY", root=root)
        self.assertEqual(bad["status"], "PERLU TINDAKAN")
        self.assertEqual(bad["lokasi_bocor"], ["catatan.md"])
        self.assertNotIn(kg.load_api_key("AGENTY_API_KEY"), json.dumps(bad))

    def test_guard_flags_loose_mode(self) -> None:
        root = Path(self._tmp.name)
        (root / ".gitignore").write_text("credentials/.env\n", encoding="utf-8")
        kg.set_api_key("AGENTY_API_KEY")
        os.chmod(self._env, 0o644)
        result = kg.guard("AGENTY_API_KEY", root=root)
        self.assertIn("mode kredensial longgar", result["alasan"])

    def test_guard_cli_is_a_real_gate(self) -> None:
        kg.set_api_key("AGENTY_API_KEY")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(kg.main(["guard", "--name", "AGENTY_API_KEY"]), 0)
        os.chmod(self._env, 0o644)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(kg.main(["guard", "--name", "AGENTY_API_KEY"]), 1)

    def test_status_and_audit_have_no_secret_values(self) -> None:
        meta = kg.set_api_key("AGENTY_API_KEY")
        secret = kg.load_api_key("AGENTY_API_KEY")
        report = kg.status()
        self.assertIsInstance(report["kunci"]["AGENTY_API_KEY"], bool)
        audit = self._audit.read_text(encoding="utf-8")
        self.assertNotIn(secret, audit)
        self.assertNotIn(secret, json.dumps(report))
        self.assertIn(meta["sidik_jari"], audit)


if __name__ == "__main__":
    unittest.main(verbosity=2)
