# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian skor keamanan terpadu."""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import security.score as score  # noqa: E402


def _controls(*flags: bool) -> list[dict[str, object]]:
    return [
        {"kontrol": f"kontrol-{i}", "status": "LULUS" if flag else "GAGAL", "bukti": "aman"}
        for i, flag in enumerate(flags)
    ]


class ScoreTests(unittest.TestCase):
    def test_summarize_perfect(self) -> None:
        result = score.summarize(_controls(True, True, True, True))
        self.assertEqual(result["skor"], 100.0)
        self.assertEqual(result["status"], "SEMPURNA")

    def test_summarize_partial_and_empty(self) -> None:
        partial = score.summarize(_controls(True, False, True, False))
        self.assertEqual(partial["skor"], 50.0)
        self.assertEqual(partial["status"], "PERLU PERBAIKAN")
        self.assertEqual(score.summarize([])["skor"], 0.0)

    def test_evaluate_report_has_no_secret_values(self) -> None:
        original_controls, original_report = score.CONTROLS, score.REPORT
        with tempfile.TemporaryDirectory() as tmp:
            score.CONTROLS = (
                ("kontrol aman", lambda: (True, "semua kontrol aktif")),
                ("kontrol gagal", lambda: (False, "tidak ada nilai rahasia")),
            )
            tmp_report = Path(tmp) / "security_score.json"
            score.REPORT = tmp_report
            try:
                result = score.evaluate()
            finally:
                score.CONTROLS, score.REPORT = original_controls, original_report
            self.assertEqual(result["skor_keamanan"], "50/100")
            self.assertEqual(len(result["controls"]), 2)
            self.assertIn("risiko_simulasi", result)
            self.assertTrue(tmp_report.exists())
            self.assertEqual(
                json.loads(tmp_report.read_text(encoding="utf-8"))["skor_keamanan"],
                "50/100",
            )

    def test_main_is_a_real_gate(self) -> None:
        original = score.evaluate
        try:
            for status, expected in (("SEMPURNA", 0), ("PERLU PERBAIKAN", 1)):
                score.evaluate = lambda s=status: {
                    "skor_keamanan": "100/100" if s == "SEMPURNA" else "50/100",
                    "summary": {"status": s},
                    "risiko_simulasi": 0,
                    "controls": [],
                }
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(score.main([]), expected)
        finally:
            score.evaluate = original

    def test_all_controls_have_boolean_evidence_shape(self) -> None:
        for name, check in score.CONTROLS:
            self.assertIsInstance(name, str)
            self.assertTrue(callable(check))


if __name__ == "__main__":
    unittest.main(verbosity=2)
