# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian agen CLI dataset IT Agenty (persiapan data, bukan training)."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from dataset import builder as b
from dataset import dataset_cli as cli


TEXT = """\
# Server Mandiri

Server inferensi mandiri tom05 menjawab dari data workspace tanpa pihak ketiga.
Semua permintaan tetap berada di loopback dan tidak pernah masuk log.

## Privasi Dataset

Setiap pasangan instruksi dan jawaban disaring dengan redaksi privasi.
Kredensial dan data pribadi tidak pernah disimpan ke dalam dataset.

## Otorisasi

Aksi ofensif hanya di lab localhost dengan izin tertulis pemilik dan batas waktu.
"""

CREDENTIAL_TEXT = """\
## Kredensial

Token akses: sk-abcdefghijklmnopqrstuvwxyz0123456789abcdef
Jangan pernah disimpan ke dalam dataset atau log publik.
"""


class BuilderTests(unittest.TestCase):
    def test_pairs_from_text(self) -> None:
        pairs = b.pairs_from_text(TEXT, "docs/contoh.md")
        self.assertGreaterEqual(len(pairs), 3)
        for pair in pairs:
            self.assertTrue(pair["instruction"])
            self.assertGreaterEqual(len(pair["response"]), b.MIN_RESPONSE)
            self.assertFalse(pair["trained"])
            self.assertEqual(pair["license"], b.LICENSE)
            self.assertEqual(pair["kind"], b.KIND)

    def test_redaction_and_credential_rejection(self) -> None:
        text = "## Kontak\nHubungi owner@example.invalid untuk info lebih lanjut mengenai server.\n"
        pairs = b.pairs_from_text(text, "docs/kontak.md")
        self.assertTrue(pairs)
        self.assertNotIn("owner@example.invalid", pairs[0]["response"])
        bad = b.manual_pair("Apa kunci API?", "kunci = AAAA-BBBB-CCCC-DDDD-EEEE-FFFF")
        self.assertIsNone(bad)

    def test_validate_and_privacy(self) -> None:
        pairs = b.pairs_from_text(TEXT, "docs/contoh.md")
        result = b.validate_records(pairs)
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(b.privacy_report(pairs)["flagged"], 0)
        broken = [dict(pairs[0]), {"instruction": "x"}]
        self.assertFalse(b.validate_records(broken)["ok"])
        trained = [dict(pairs[0], trained=True)]
        self.assertFalse(b.validate_records(trained)["ok"])

    def test_stats_and_roundtrip(self) -> None:
        pairs = b.pairs_from_text(TEXT, "docs/contoh.md")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ds.jsonl"
            b.write_jsonl(pairs, path)
            self.assertEqual(b.read_jsonl(path), pairs)
        s = b.stats(pairs)
        self.assertEqual(s["records"], len(pairs))
        self.assertFalse(s["trained"])

    def test_build_dataset_from_temp_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs" / "a.md").write_text(TEXT, encoding="utf-8")
            (root / "docs" / "b.md").write_text(CREDENTIAL_TEXT, encoding="utf-8")
            records = b.build_dataset(root, ["docs"])
            self.assertTrue(records)
            self.assertTrue(all(not r["trained"] for r in records))
            self.assertEqual(b.privacy_report(records)["flagged"], 0)
            self.assertFalse(any("sk-abcdef" in r["response"] for r in records))

    def test_build_dedups_casefold_instructions(self) -> None:
        """Judul beda huruf besar dari dua dokumen tidak boleh jadi duplikat."""
        # Judul berakhir "?" sehingga dipakai apa adanya — beda huruf saja.
        body_a = "# Apa itu Masa berlaku?\nIzin berlaku hingga 31 Desember 2027 untuk seluruh tugas.\n"
        body_b = "# Apa itu Masa Berlaku?\nIzin diperpanjang sampai 31 Desember 2027 oleh pemilik.\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs" / "a.md").write_text(body_a, encoding="utf-8")
            (root / "docs" / "b.md").write_text(body_b, encoding="utf-8")
            records = b.build_dataset(root, ["docs"])
            self.assertEqual(len(records), 1, [r["instruction"] for r in records])
            result = b.validate_records(records)
            self.assertTrue(result["ok"], result["errors"])

    def test_merge_dedups_casefold_instructions(self) -> None:
        first = dict(b.manual_pair(
            "Apa itu Masa berlaku?",
            "Masa berlaku izin ditetapkan sampai 31 Desember 2027 oleh pemilik.",
            "a.md",
        ))
        second = dict(b.manual_pair(
            "Apa itu MASA BERLAKU?",
            "Masa berlaku izin diperpanjang sampai 31 Desember 2027.",
            "b.md",
        ))
        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        second["id"] = "id-lain-yang-unik"
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.jsonl"
            bb = Path(tmp) / "b.jsonl"
            b.write_jsonl([first], a)
            b.write_jsonl([second], bb)
            merged, removed = b.merge_datasets([a, bb])
            self.assertEqual(removed, 1)
            self.assertEqual(len(merged), 1)
            self.assertTrue(b.validate_records(merged)["ok"])

    def test_license_header(self) -> None:
        for path in (b.ROOT / "dataset" / "dataset_cli.py", b.ROOT / "dataset" / "builder.py"):
            text = path.read_text(encoding="utf-8")
            self.assertIn("SPDX-License-Identifier: Tom05ivier-commits-1.0", text)
            self.assertIn("Copyright (c) 2026 Tomi vier", text)


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "docs").mkdir()
        (self.root / "docs" / "a.md").write_text(TEXT, encoding="utf-8")
        (self.root / "docs" / "b.md").write_text(CREDENTIAL_TEXT, encoding="utf-8")
        self.out = self.root / "data.jsonl"
        self._old_root, self._old_audit = cli.ROOT, b.AUDIT_PATH
        cli.ROOT = self.root
        b.AUDIT_PATH = self.root / "audit.jsonl"

    def tearDown(self) -> None:
        cli.ROOT, b.AUDIT_PATH = self._old_root, self._old_audit
        self.tmp.cleanup()

    def _run(self, *argv: str) -> tuple[int, dict]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main(list(argv))
        return code, json.loads(buf.getvalue())

    def test_agent_doctor_template_are_honest(self) -> None:
        code, agent = self._run("agent")
        self.assertEqual(code, 0)
        self.assertFalse(agent["trained"])
        self.assertIn("build", agent.get("commands", []))

        code, doc = self._run("doctor")
        self.assertEqual(code, 0)
        self.assertIn("pustaka_ml", doc)
        self.assertIsInstance(doc["training_siap"], bool)
        self.assertFalse(doc["training_siap"])

        code, tpl = self._run("template")
        self.assertEqual(code, 0)
        self.assertEqual(tpl["status"], "TEMPLATE")
        self.assertFalse(tpl["contoh"]["trained"])

    def test_build_is_dry_runnable_and_idempotent(self) -> None:
        code, dry = self._run("build", "--source", "docs", "--out", str(self.out), "--dry-run")
        self.assertEqual(code, 0)
        self.assertEqual(dry["status"], "SIMULASI")
        self.assertEqual(dry["written"], 0)
        self.assertFalse(self.out.exists())

        code, gen = self._run("build", "--source", "docs", "--out", str(self.out))
        self.assertEqual(code, 0)
        self.assertEqual(gen["status"], "OK")
        self.assertTrue(self.out.exists())
        self.assertGreater(gen["count"], 0)
        self.assertFalse(gen["trained"])
        self.assertEqual(gen["privacy"]["flagged"], 0)
        first = self.out.read_text(encoding="utf-8")
        self._run("build", "--source", "docs", "--out", str(self.out))
        self.assertEqual(self.out.read_text(encoding="utf-8"), first)

    def test_validate_stats_privacy_and_export(self) -> None:
        self._run("build", "--source", "docs", "--out", str(self.out))
        code, val = self._run("validate", str(self.out))
        self.assertEqual(code, 0)
        self.assertEqual(val["status"], "PASS")

        code, stats = self._run("stats", str(self.out))
        self.assertEqual(code, 0)
        self.assertEqual(stats["stats"]["records"], val["count"])

        code, priv = self._run("privacy", str(self.out))
        self.assertEqual(code, 0)
        self.assertEqual(priv["status"], "BERSIH")

        for fmt in ("alpaca", "sharegpt", "jsonl"):
            target = self.root / f"out.{fmt}.jsonl"
            code, exp = self._run("export", str(self.out), "--format", fmt, "--out", str(target))
            self.assertEqual(code, 0, exp)
            self.assertEqual(exp["count"], val["count"])
            rows = b.read_jsonl(target)
            self.assertEqual(len(rows), val["count"])
            self.assertTrue(all(not r["trained"] for r in rows))
            if fmt == "alpaca":
                self.assertIn("output", rows[0])
            elif fmt == "sharegpt":
                self.assertEqual(rows[0]["conversations"][0]["from"], "human")

    def test_add_is_safe_and_idempotent(self) -> None:
        args = (
            "add",
            "Apa fungsi agen dataset?",
            "Agen dataset menyiapkan dan memvalidasi pasangan instruksi jawaban dari dokumen workspace IT Agenty.",
            "--out", str(self.out),
        )
        code, added = self._run(*args)
        self.assertEqual(code, 0)
        self.assertEqual(added["status"], "OK")
        self.assertFalse(added["trained"])
        code, again = self._run(*args)
        self.assertEqual(code, 0)
        self.assertEqual(again["total"], added["total"])

        code, bad = self._run(
            "add", "Apa kunci API?", "sk-abcdefghijklmnopqrstuvwxyz0123456789abcdef token",
            "--out", str(self.out),
        )
        self.assertEqual(code, 1)
        self.assertEqual(bad["status"], "GAGAL")

    def test_add_replaces_casefold_duplicate(self) -> None:
        first = (
            "add", "Apa batas Izin?",
            "Batas izin ditetapkan sampai 31 Desember 2027 dan dapat dicabut pemilik.",
            "--out", str(self.out),
        )
        second = (
            "add", "apa batas izin?",
            "Batas izin ditetapkan sampai 31 Desember 2027 dan dapat dicabut pemilik.",
            "--out", str(self.out),
        )
        code, added = self._run(*first)
        self.assertEqual(code, 0, added)
        code, again = self._run(*second)
        self.assertEqual(code, 0, again)
        self.assertEqual(again["total"], added["total"])
        self.assertEqual(b.validate_records(b.read_jsonl(self.out))["errors"], [])

    def test_privacy_reports_counts_without_values(self) -> None:
        seeded = self.root / "seeded.jsonl"
        seeded.write_text(
            json.dumps({
                "id": "x", "instruction": "Apa email?",
                "response": "Hubungi owner@example.invalid untuk info.",
                "source": "manual", "license": b.LICENSE, "kind": "manual", "trained": False,
            }) + "\n",
            encoding="utf-8",
        )
        code, report = self._run("privacy", str(seeded))
        self.assertEqual(code, 1)
        self.assertEqual(report["status"], "TEMUAN")
        self.assertGreater(report["privacy"]["flagged"], 0)
        self.assertNotIn("owner@example.invalid", json.dumps(report))

    def test_validate_rejects_trained_true(self) -> None:
        bad = self.root / "bad.jsonl"
        rows = b.pairs_from_text(TEXT, "docs/contoh.md")
        rows[0] = dict(rows[0], trained=True)
        b.write_jsonl(rows, bad)
        code, result = self._run("validate", str(bad))
        self.assertEqual(code, 1)
        self.assertEqual(result["status"], "FAIL")


class DatasetOpsTests(unittest.TestCase):
    """Regresi untuk subcommand olah data: init/merge/dedup/filter/split."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self._old_root, self._old_audit = cli.ROOT, b.AUDIT_PATH
        cli.ROOT = self.root
        b.AUDIT_PATH = self.root / "audit.jsonl"
        self.base = b.pairs_from_text(TEXT, "docs/contoh.md")
        self.assertTrue(self.base)
        self.path = self.root / "ds.jsonl"
        b.write_jsonl(self.base, self.path)

    def tearDown(self) -> None:
        cli.ROOT, b.AUDIT_PATH = self._old_root, self._old_audit
        self.tmp.cleanup()

    def _run(self, *argv: str) -> tuple[int, dict]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main(list(argv))
        return code, json.loads(buf.getvalue())

    def _write(self, name: str, records: list[dict]) -> Path:
        path = self.root / name
        b.write_jsonl(records, path)
        return path

    def test_init_labels_synthetic_examples_and_guards_overwrite(self) -> None:
        out = self.root / "contoh.jsonl"
        code, payload = self._run("init", "--out", str(out))
        self.assertEqual(code, 0, payload)
        self.assertTrue(payload["sintetis"])
        rows = b.read_jsonl(out)
        self.assertEqual(len(rows), 3)
        for row in rows:
            self.assertEqual(row["source"], "sintetis")
            self.assertEqual(row["kind"], "contoh-sintetis")
            self.assertFalse(row["trained"])
            self.assertIn("CONTOH/SINTETIS", row["catatan"])

        code, payload = self._run("init", "--out", str(out))
        self.assertEqual(code, 1)
        self.assertEqual(payload["status"], "GAGAL")

        empty = self.root / "kosong.jsonl"
        code, payload = self._run("init", "--empty", "--out", str(empty))
        self.assertEqual(code, 0, payload)
        self.assertFalse(payload["sintetis"])
        self.assertEqual(b.read_jsonl(empty), [])

    def test_merge_dedups_by_id(self) -> None:
        extra = b.manual_pair(
            "Apa fungsi split?",
            "Split membagi dataset menjadi berkas train dan val secara deterministik "
            "tanpa tumpang tindih antar instruksi.",
            "manual",
        )
        self.assertIsNotNone(extra)
        second = self._write("lain.jsonl", [dict(self.base[0]), extra])  # type: ignore[list-item]
        out = self.root / "gabungan.jsonl"
        code, payload = self._run("merge", str(self.path), str(second), "--out", str(out))
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["duplicates"], 1)
        self.assertEqual(len(b.read_jsonl(out)), len(self.base) + 1)

    def test_dedup_by_instruction_and_pair(self) -> None:
        duplicated = self.base[:2] + [dict(self.base[0]), dict(self.base[1])]
        source = self._write("dup.jsonl", duplicated)
        for key in ("instruction", "pair"):
            out = self.root / f"dedup-{key}.jsonl"
            code, payload = self._run("dedup", str(source), "--key", key, "--out", str(out))
            self.assertEqual(code, 0, payload)
            self.assertEqual(payload["removed"], 2)
            self.assertEqual(len(b.read_jsonl(out)), 2)

    def test_filter_by_source_contains_and_length(self) -> None:
        out = self.root / "filter.jsonl"
        code, payload = self._run(
            "filter", str(self.path), "--source", "docs/contoh.md", "--out", str(out)
        )
        self.assertEqual(code, 0, payload)
        self.assertEqual(len(b.read_jsonl(out)), len(self.base))

        needle = "privasi"
        expected = sum(
            needle in (r["instruction"] + "\n" + r["response"]).casefold()
            for r in self.base
        )
        out2 = self.root / "filter-contains.jsonl"
        code, payload = self._run(
            "filter", str(self.path), "--contains", needle, "--out", str(out2)
        )
        self.assertEqual(code, 0, payload)
        self.assertEqual(len(b.read_jsonl(out2)), expected)

        out3 = self.root / "filter-panjang.jsonl"
        code, payload = self._run(
            "filter", str(self.path), "--min-chars", "100000", "--out", str(out3)
        )
        self.assertEqual(code, 0, payload)
        self.assertEqual(b.read_jsonl(out3), [])

    def test_split_deterministic_nonoverlapping_and_guarded(self) -> None:
        train = self.root / "train.jsonl"
        val = self.root / "val.jsonl"
        argv = (
            "split", str(self.path), "--val-frac", "0.34", "--seed", "7",
            "--train-out", str(train), "--val-out", str(val),
        )
        code, payload = self._run(*argv)
        self.assertEqual(code, 0, payload)
        train_rows, val_rows = b.read_jsonl(train), b.read_jsonl(val)
        self.assertEqual(len(train_rows) + len(val_rows), len(self.base))
        self.assertEqual(payload["val"], len(val_rows))
        self.assertFalse(
            {r["instruction"] for r in train_rows}
            & {r["instruction"] for r in val_rows}
        )
        for part in (train, val):
            self.assertTrue(b.validate_records(b.read_jsonl(part))["ok"])

        code, payload = self._run(*argv)
        self.assertEqual(code, 1)
        self.assertEqual(payload["status"], "GAGAL")

    def test_export_accepts_root_relative_path(self) -> None:
        rel = str(self.path.relative_to(self.root))
        out = self.root / "ekspor.jsonl"
        code, payload = self._run("export", rel, "--format", "jsonl", "--out", str(out))
        self.assertEqual(code, 0, payload)
        self.assertEqual(len(b.read_jsonl(out)), len(self.base))


if __name__ == "__main__":
    unittest.main()
