// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
//
// tom05_ai_accel — akselerator AI inference tom05 (TAI-1).
//
// Desain RTL orisinal IT Agenty yang mengadaptasi ide arsitektur dari
// laporan "Top 30+ AI Chip Makers: NVIDIA & Its Competitors" (AIMultiple):
//   mode 00 TENSOR  — MAC berbobot ala GPU/TPU (NVIDIA, AMD)
//   mode 01 LPU     — aliran deterministik ala LPU (Groq, Etched)
//   mode 10 NEARMEM — komputasi dekat SRAM ala d-Matrix / Qualcomm HBC
//   mode 11 MESH    — reduksi seragam ala wafer-scale (Cerebras)
//
// Bukan salinan IP pihak ketiga. Status fabrikasi: NOT_READY.
// Seluruh keluaran murni `assign` agar model Python, simulator browser,
// dan Icarus Verilog menghasilkan vektor yang identik.

`timescale 1ns/1ps

module tom05_ai_accel(
  input [1:0] a0, a1, a2, a3,
  input [1:0] mode,
  input irq_clear,
  output [4:0] score,
  output [1:0] level,
  output hit,
  output irq,
  output ready
);
  wire [4:0] d_tensor;
  wire [4:0] d_lpu;
  wire [4:0] d_near_hit;
  wire [4:0] d_near_miss;
  wire [4:0] d_near;
  wire [4:0] d_mesh;
  wire h;
  wire [1:0] lvl;

  // Profil TENSOR: bobot 1,2,3,4 (maks 30).
  assign d_tensor = a0 + (a1 * 2) + (a2 * 3) + (a3 * 4);
  // Profil LPU: bobot dibalik 4,3,2,1 (maks 30).
  assign d_lpu = (a0 * 4) + (a1 * 3) + (a2 * 2) + a3;
  // Profil NEARMEM: bobot lokal bila data di SRAM, jika tidak pakai jalur luar.
  assign d_near_hit = (a0 * 2) + (a1 * 2) + a2 + a3;
  assign d_near_miss = a0 + a1 + (a2 * 2) + (a3 * 2);
  assign h = ((a0 >> 1) & 1) | ((a1 >> 1) & 1)
           | ((a2 >> 1) & 1) | ((a3 >> 1) & 1);
  assign d_near = ((1 - h) * d_near_miss) + (h * d_near_hit);
  // Profil MESH: reduksi seragam 2× dari jumlah semua jalur (maks 24).
  assign d_mesh = (a0 * 2) + (a1 * 2) + (a2 * 2) + (a3 * 2);

  assign score = (((1 - (mode & 1)) & (1 - ((mode >> 1) & 1))) * d_tensor)
               + (((mode & 1) & (1 - ((mode >> 1) & 1))) * d_lpu)
               + (((1 - (mode & 1)) & ((mode >> 1) & 1)) * d_near)
               + (((mode & 1) & ((mode >> 1) & 1)) * d_mesh);
  assign lvl = (score >> 3) & 3;
  assign hit = h;
  assign level = lvl;
  assign irq = ((lvl >> 1) & 1) & (irq_clear ^ 1);
  assign ready = 1;
endmodule
