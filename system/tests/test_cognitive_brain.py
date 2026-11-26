# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian pemetaan fungsi kognitif ke dalam supervisor."""

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

from system import cognitive_brain as cb  # noqa: E402


class CognitiveBrainTests(unittest.TestCase):
    def test_empat_lapisan_berurutan(self) -> None:
        self.assertEqual(
            [layer["id"] for layer in cb.LAYERS],
            ["indra", "memori", "perencanaan", "aksi"],
        )

    def test_setiap_lapisan_punya_analogi_dan_batasan(self) -> None:
        for layer in cb.LAYERS:
            self.assertTrue(layer["otak"], layer["id"])
            self.assertTrue(layer["fungsi"], layer["id"])
            self.assertTrue(layer["komputer"], layer["id"])
            self.assertTrue(layer["analogi"], layer["id"])
            self.assertTrue(layer["batasan"], layer["id"])
            self.assertTrue(layer["komponen"], layer["id"])

    def test_semua_path_bukti_ada(self) -> None:
        for layer in cb.LAYERS:
            for item in layer["komponen"]:
                self.assertTrue((ROOT / item["path"]).exists(), item["path"])

    def test_perceive_read_only(self) -> None:
        data = cb.perceive()
        self.assertEqual(data["mode"], "read-only")
        self.assertGreaterEqual(data["propriosepsi"]["layanan_terdaftar"], 1)
        self.assertEqual(data["sensor_perangkat"]["gpu"], "TIDAK_TEREKSPOS")
        self.assertIn("masuk", data["antrean_chat"])

    def test_remember_tanpa_training(self) -> None:
        data = cb.remember()
        self.assertGreater(data["dataset"]["rekord"], 0)
        self.assertFalse(data["dataset"]["trained"])
        self.assertGreaterEqual(data["pengetahuan"]["dokumen_terindeks"], 0)
        self.assertGreaterEqual(data["jejak_keputusan"]["runs"], 0)

    def test_plan_stabil_dan_diawali_status(self) -> None:
        first = cb.plan("status sistem")
        second = cb.plan("status sistem")
        self.assertEqual(first, second)
        self.assertEqual(first["langkah"][0]["tugas"], "status")
        self.assertEqual(first["izin"], "tanpa-otorisasi")

    def test_plan_aksi_terbatas_tidak_dijalankan(self) -> None:
        result = cb.plan("jalankan drill keamanan")
        restricted = [s for s in result["langkah"] if s["jenis"] == "terbatas"]
        self.assertTrue(restricted)
        self.assertTrue(all(s["tugas"] in cb.RESTRICTED_TASKS for s in restricted))
        authorized = cb.plan("jalankan drill keamanan", authorize=True)
        self.assertEqual(authorized["izin"], "dengan-otorisasi")

    def test_act_deskriptif_saja(self) -> None:
        data = cb.act()
        self.assertEqual(data["mode"], "deskriptif")
        self.assertGreaterEqual(data["respon_teks"]["jumlah_responder"], 1)
        self.assertFalse(data["pengaman"]["shell"])
        self.assertFalse(data["pengaman"]["aksi_ofensif_otomatis"])

    def test_siklus_lima_tahap(self) -> None:
        data = cb.cycle("status sistem")
        for key in ("indra", "memori", "perencanaan", "aksi", "refleksi"):
            self.assertIn(key, data)
        self.assertEqual(data["refleksi"]["status"], "SIMULASI")

    def test_peta_lengkap_dan_tersimpan(self) -> None:
        result = cb.map_cognitive()
        self.assertEqual(result["status"], "TERPETAKAN")
        self.assertEqual(len(result["lapisan"]), 4)
        self.assertTrue(all(c["ada"] for layer in result["lapisan"]
                            for c in layer["komponen"]))
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "peta.json"
            written = cb.write_report(result, target)
            self.assertEqual(written, target)
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["status"],
                             "TERPETAKAN")

    def test_cli_verify(self) -> None:
        self.assertEqual(cb.main(["--verify", "--no-write"]), 0)

    def test_cli_cycle(self) -> None:
        self.assertEqual(cb.main(["--cycle", "status sistem"]), 0)

    def test_tidak_ada_kredensial_dalam_laporan(self) -> None:
        text = json.dumps(cb.map_cognitive(), ensure_ascii=False).lower()
        for marker in ("api_key", "password", "secret", "authorization"):
            self.assertNotIn(marker, text)
    def test_indra_memiliki_pengetahuan_rasa(self) -> None:
        names = {item["nama"] for item in cb.LAYERS[0]["komponen"]}
        self.assertIn("Pengetahuan Rasa", names)
        self.assertIn("Config Rasa", names)
        rasa = cb.perceive()["rasa"]
        self.assertFalse(rasa["sensor"])
        self.assertEqual(rasa["kategori"], ["manis", "asin", "asam", "pahit", "umami"])

    def test_perencanaan_memiliki_latar_hak(self) -> None:
        names = {item["nama"] for item in cb.LAYERS[2]["komponen"]}
        self.assertIn("Keseimbangan Kepentingan-Hak", names)
        self.assertIn("Config Keseimbangan", names)
        from system import rights_balance

        self.assertEqual(rights_balance.check()["status"], "SEIMBANG")
        self.assertEqual(cb.map_cognitive()["latar"]["keseimbangan"]["status"],
                         "SEIMBANG")

    def test_rasa_bukan_sensor_dan_tanpa_data_pribadi(self) -> None:
        from system import taste_knowledge

        data = taste_knowledge.describe()
        self.assertFalse(data["sensor"])
        self.assertEqual(data["jumlah_kategori"], 5)
        text = json.dumps(data, ensure_ascii=False).lower()
        self.assertNotIn("biometrik subjek", text)
        for marker in ("api_key", "password", "secret", "authorization"):
            self.assertNotIn(marker, text)

    def test_hak_mendahului_tanpa_izin(self) -> None:
        from system import rights_balance

        denied = rights_balance.evaluate("jalankan drill", authorize=False)
        self.assertEqual(denied["keputusan"], "hak_mendahului")
        granted = rights_balance.evaluate("jalankan drill", authorize=True)
        self.assertEqual(granted["keputusan"], "seimbang_terbatas")
        self.assertEqual(granted["ttl_maks_detik"], 300)
        plan = cb.plan("jalankan drill", authorize=False)
        self.assertEqual(plan["keseimbangan"]["keputusan"], "hak_mendahului")

    def test_siklus_membawa_rasa_dan_keseimbangan(self) -> None:
        result = cb.cycle("status sistem")
        self.assertFalse(result["indra"]["rasa"]["sensor"])
        self.assertIn("keseimbangan", result["perencanaan"])


if __name__ == "__main__":
    unittest.main()
