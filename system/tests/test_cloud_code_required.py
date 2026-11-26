# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian: keenam alat Cloud Code dinyatakan wajib."""

import unittest

from system import cloud_code


class CloudCodeRequiredTests(unittest.TestCase):
    def test_semua_alat_wajib(self) -> None:
        self.assertEqual(len(cloud_code.TOOLS), 6)
        for tool in cloud_code.TOOLS:
            self.assertEqual(tool["required"], "ya", tool["name"])

    def test_laporan_wajib_hilang_kosong(self) -> None:
        data = cloud_code.status()
        self.assertEqual(data["wajib_hilang"], [])


if __name__ == "__main__":
    unittest.main()
