// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
//
// index_match4 — akselerator irisan himpunan untuk indeks data aman.
// q = masker query 4-bit, k = masker kata kunci 4-bit.
// score = jumlah bit yang bernilai 1 pada (q & k), dipotong ke 3 bit.
// Ini adalah operasi inti `len(terms & haystack)` di safe_data_index.py.

`timescale 1ns/1ps

module index_match4(input [3:0] q, input [3:0] k, output [2:0] score);
  assign score = ((q & k) & 1) + (((q & k) >> 1) & 1) + (((q & k) >> 2) & 1) + (((q & k) >> 3) & 1);
endmodule
