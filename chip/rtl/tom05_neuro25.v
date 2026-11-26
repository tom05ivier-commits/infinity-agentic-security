// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
//
// tom05_neuro25 — inti pemroses sinyal SINTETIS NEURO-25.
//
// Pemetaan empat tahap kognitif ke jalur data:
//   n0..n3  indra      : empat kanal aktivitas sintetis (bukan elektroda)
//   mem     memori     : bobot pengalaman sintetis
//   intent  perencanaan: tahap 0..3 (indra/memori/rencana/aksi)
//   gate    izin       : 0 = aksi diblokir, 1 = aksi diizinkan
//   act     aksi       : hanya aktif bila ambang tercapai DAN gate=1
//   blocked/irq        : aksi ditahan bila gate=0
//
// "Profil 25 tahun" adalah konstanta kalibrasi simulasi (gain=2) pada jalur
// memori. BUKAN data biologis, bukan pengukuran otak, bukan alat medis.
// Tidak ada input dari subjek hidup, tidak ada elektroda, tidak ada stimulasi,
// tidak ada radio, dan tidak ada koneksi ke perangkat eksternal.
//
// Status: NOT_READY (fabrikasi), NOT_VALIDATED (klinis).
// Seluruh keluaran murni `assign` agar model Python, Icarus, dan sintesis
// menghasilkan vektor yang identik.

`timescale 1ns/1ps

module tom05_neuro25(
  input [1:0] n0, n1, n2, n3,
  input [1:0] mem,
  input [1:0] intent,
  input gate,
  output [4:0] decision,
  output [1:0] stage,
  output act,
  output blocked,
  output irq,
  output ready
);
  wire [4:0] sense;
  wire [4:0] memory_w;
  wire [4:0] plan_w;
  wire [1:0] stage_w;
  wire actionable;
  wire stage_is_action;
  wire high;

  // INDRA: fusi empat kanal sintetis dengan bobot 1,2,3,4 (maks 30).
  assign sense = (n0 + (n1 * 2) + (n2 * 3) + (n3 * 4)) & 31;
  // MEMORI: tambah bobot pengalaman dengan gain profil dewasa-muda (=2).
  assign memory_w = (sense + (mem * 2)) & 31;
  // PERENCANAAN: gabungkan memori dengan tujuan, gain yang sama (=2).
  assign plan_w = (memory_w + (intent * 2)) & 31;
  assign decision = plan_w & 31;

  assign stage_w = intent & 3;
  assign stage = stage_w;
  // Hanya tahap perencanaan/aksi (bit-1 = 1) yang boleh menghasilkan aksi.
  assign actionable = (intent >> 1) & 1;
  assign stage_is_action = (stage_w & 1) & ((stage_w >> 1) & 1);
  assign high = (decision >> 3) & 1;

  // AKSI: ambang tinggi DAN izin diberikan. Tanpa izin, aksi ditahan.
  assign act = high & gate & actionable;
  assign blocked = high & (gate ^ 1) & actionable;
  assign irq = blocked & stage_is_action;
  assign ready = 1;
endmodule
