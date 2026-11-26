# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Pengujian scorecard kualitas chip."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chip import scorecard  # noqa: E402
from chip.scorecard import CHECKS, build  # noqa: E402


class ScorecardTests(unittest.TestCase):
    def test_ten_criteria(self) -> None:
        self.assertEqual(len(CHECKS), 10)

    def test_build_is_perfect(self) -> None:
        report = build()
        self.assertEqual(report["score"], 100)
        self.assertEqual(report["maximum"], 100)
        self.assertEqual(report["grade"], "100/100")
        self.assertEqual(report["status"], "PERFECT")
        self.assertEqual(report["failed"], [])
        self.assertTrue(all(item["points"] == 10 for item in report["checks"]))

    def test_report_written(self) -> None:
        build()
        path = ROOT / "chip" / "reports" / "chip_score.json"
        self.assertTrue(path.exists())
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["grade"], "100/100")
        self.assertIn("Tom05ivier-commits-1.0", data["license"])

    def test_load_retries_transient_read_error(self) -> None:
        with mock.patch.object(
            Path, "read_text", side_effect=[OSError("race"), '{"status": "PASS"}']
        ) as read, mock.patch.object(scorecard.time, "sleep") as sleep:
            data = scorecard._load("bukti.json")
        self.assertEqual(data, {"status": "PASS"})
        self.assertEqual(read.call_count, 2)
        sleep.assert_called_once_with(0.1)

    def test_load_retries_transient_bad_json(self) -> None:
        with mock.patch.object(Path, "read_text", side_effect=["{", '{"ok": true}']), \
             mock.patch.object(scorecard.time, "sleep"):
            self.assertEqual(scorecard._load("bukti.json"), {"ok": True})

    def test_load_raises_after_three_failures(self) -> None:
        with mock.patch.object(Path, "read_text", side_effect=OSError("rusak")), \
             mock.patch.object(scorecard.time, "sleep") as sleep:
            with self.assertRaises(OSError):
                scorecard._load("bukti.json")
        self.assertEqual(sleep.call_count, 2)

    def test_build_idempoten_tanpa_perubahan_hash(self) -> None:
        """Build ulang dengan bukti sama tidak mengubah isi berkas laporan."""
        import hashlib

        path = ROOT / "chip" / "reports" / "chip_score.json"
        build()
        sebelum = hashlib.sha256(path.read_bytes()).hexdigest()
        build()
        sesudah = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(sesudah, sebelum)

    def test_build_tulis_ulang_bila_bukti_berubah(self) -> None:
        """Perubahan isi semantik tetap memicu penulisan laporan."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "chip_score.json"
            target.write_text(
                json.dumps({"score": 90, "grade": "90/100"}), encoding="utf-8"
            )
            with mock.patch.object(scorecard, "REPORT_PATH", target):
                report = scorecard.build()
            data = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(report["score"], 100)
        self.assertEqual(data["grade"], "100/100")


if __name__ == "__main__":
    unittest.main(verbosity=2)
