# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
"""Regresi untuk perbaikan retrieval tom05-flash-free (23 Nov 2026)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.tom05_knowledge import (  # noqa: E402
    MODEL_ID, clean_snippet, split_code, split_prose, tokenize,
)


class TestTom05Knowledge(unittest.TestCase):
    def test_command_verbs_are_not_stop_words(self):
        tokens = tokenize("status sistem cek inbox")
        self.assertIn("status", tokens)
        self.assertIn("inbox", tokens)

    def test_generic_only_question_never_dumps_code(self):
        # dulu "Atasi error" memuntahkan potongan kode acak
        from system.tom05_knowledge import get_model
        result = get_model().answer("Atasi error")
        content = result["choices"][0]["message"]["content"]
        self.assertEqual(result["model"], MODEL_ID)
        self.assertTrue(all(src.endswith((".md", ".txt"))
                            for src in result["tom05"]["sources"]))
        for artifact in ("ocessError", "as exc:", "return ", "def "):
            self.assertNotIn(artifact, content)

    def test_clean_snippet_drops_broken_prefix(self):
        out = clean_snippet("ocessError) as exc:\n    last_error = str(exc)\n")
        self.assertNotIn("ocessError", out)
        self.assertIn("last_error", out)

    def test_clean_snippet_drops_spdx_header(self):
        raw = "<!--\n  SPDX-License-Identifier: Tom05ivier-commits-1.0\n-->\n\n# Judul\nIsi singkat."
        self.assertTrue(clean_snippet(raw).startswith("# Judul"))

    def test_split_code_keeps_whole_lines(self):
        self.assertEqual(split_code("a\nb\nc"), ["a\nb\nc"])
        long = "\n".join(f"baris_{i}" for i in range(200))
        chunks = split_code(long, size=80)
        self.assertGreater(len(chunks), 1)
        joined = "\n".join(chunks)
        self.assertIn("baris_0", joined)
        self.assertIn("baris_199", joined)

    def test_split_prose_keeps_paragraphs(self):
        raw = "Paragraf satu kalimat pertama.\nKedua.\n\nParagraf dua isi dokumentasi."
        self.assertEqual(len(split_prose(raw, size=200)), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
