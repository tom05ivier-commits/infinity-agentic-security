// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.

`timescale 1ns/1ps

// Chip verifikasi server: community (http, port 8781)
// Logika: ready = alive & healthy & enabled
//         degraded = alive & enabled & ~healthy
//         blocked = ~alive | ~enabled
module srv_community(
  input alive,
  input healthy,
  input enabled,
  output ready,
  output degraded,
  output blocked
);
  assign ready = alive & healthy & enabled;
  assign degraded = alive & enabled & ~healthy;
  assign blocked = ~alive | ~enabled;
endmodule
