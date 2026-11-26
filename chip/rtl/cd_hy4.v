// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.

`timescale 1ns/1ps

// Chip khusus agent: hy4 (cd_hy4). Diaktifkan kembali 26 November 2026.
// truth table: ok = req & (tag == 116); match = (tag == 116)
module cd_hy4(
  input req,
  input [7:0] tag,
  output ok,
  output match
);
  wire [7:0] ACC;
  assign ACC = 8'd116;
  assign ok = req & (tag == ACC);
  assign match = (tag == ACC);
endmodule
