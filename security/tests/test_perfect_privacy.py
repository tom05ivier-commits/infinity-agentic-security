# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian perlindungan privasi menyeluruh (tanpa nilai sensitif)."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from security.privacy import (  # noqa: E402
    release_ready,
    redact,
    safe_output,
    scan,
    scan_secrets,
    verify_tree,
)

FAKE_TOKEN = "ghp_" + "A" * 36
FAKE_KEY = "api_key = '" + "aB3dE5gH7jK9mN2pQ4rS6tU8" + "'"


class PerfectPrivacyTests(unittest.TestCase):
    def test_scan_secrets_counts_only(self) -> None:
        result = scan_secrets(f"token {FAKE_TOKEN}\n{FAKE_KEY}")
        self.assertGreater(result["github_token"], 0)
        self.assertGreater(result["assignment"], 0)
        self.assertNotIn(FAKE_TOKEN, json.dumps(result))
        self.assertNotIn("aB3dE5gH7jK9mN2pQ4rS6tU8", json.dumps(result))

    def test_redact_removes_provider_tokens(self) -> None:
        cleaned = redact(f"h={FAKE_TOKEN} {FAKE_KEY}")
        self.assertNotIn(FAKE_TOKEN, cleaned)
        self.assertNotIn("aB3dE5gH7jK9mN2pQ4rS6tU8", cleaned)
        self.assertIn("[REDACTED]", cleaned)

    def test_safe_output_matches_redact(self) -> None:
        text = "email: user@domain.test " + FAKE_TOKEN
        self.assertEqual(safe_output(text), redact(text))
        self.assertNotIn(FAKE_TOKEN, safe_output(text))

    def test_verify_tree_reports_paths_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "doc.md").write_text(f"mail user@domain.test {FAKE_TOKEN}", encoding="utf-8")
            result = verify_tree(root)
            self.assertEqual(result["status"], "BOCOR")
            self.assertTrue(result["findings"])
            blob = json.dumps(result)
            self.assertNotIn(FAKE_TOKEN, blob)
            self.assertNotIn("user@domain.test", blob)
            self.assertIn("doc.md", blob)

    def test_sanitized_placeholders_are_not_findings(self) -> None:
        sanitized = (
            "owner@example.invalid 000000000000 (__signature__) "
            "01-01-1970 Kota, Provinsi api_key=[REDACTED]"
        )
        self.assertEqual(sum(scan(sanitized).values()), 0)
        self.assertEqual(sum(scan_secrets(sanitized).values()), 0)

    def test_verify_tree_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "clean.md").write_text("tidak ada data sensitif", encoding="utf-8")
            self.assertEqual(verify_tree(Path(tmp))["status"], "AMAN")

    def test_verify_tree_flags_loose_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = Path(tmp) / ".env"
            env.write_text("OPENCODE_API_KEY=whatever", encoding="utf-8")
            os.chmod(env, 0o644)
            result = verify_tree(Path(tmp))
            self.assertEqual(result["status"], "BOCOR")
            self.assertIn("mode_kredensial", [f["label"] for f in result["findings"]])
            os.chmod(env, 0o600)
            self.assertEqual(verify_tree(Path(tmp))["status"], "AMAN")

    def test_release_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gitignore").write_text("credentials/.env\n", encoding="utf-8")
            (root / "clean.md").write_text("aman", encoding="utf-8")
            self.assertEqual(release_ready(root)["status"], "SIAP")
            (root / "doc.md").write_text(FAKE_TOKEN, encoding="utf-8")
            self.assertEqual(release_ready(root)["status"], "PERLU TINDAKAN")


if __name__ == "__main__":
    unittest.main(verbosity=2)
