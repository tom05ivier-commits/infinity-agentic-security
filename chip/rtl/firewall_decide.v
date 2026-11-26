// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.

`timescale 1ns/1ps

// Keputusan firewall: allow hanya bila aturan allow cocok dan deny tidak cocok.
// Deny memiliki prioritas.
module firewall_decide(
  input p0, p1, p2, p3,
  input d0, d1, d2, d3, deny_en,
  input a0, a1, a2, a3, allow_en,
  output decision
);
  wire deny_hit;
  wire allow_hit;

  assign deny_hit = ~(p0 ^ d0) & ~(p1 ^ d1) & ~(p2 ^ d2) & ~(p3 ^ d3) & deny_en;
  assign allow_hit = ~(p0 ^ a0) & ~(p1 ^ a1) & ~(p2 ^ a2) & ~(p3 ^ a3) & allow_en;
  assign decision = allow_hit & ~deny_hit;
endmodule
