<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Chip Simulasi NEURO-25

`chip/rtl/tom05_neuro25.v` adalah inti pemroses **sinyal sintetis** yang
memetakan empat tahap kognitif ke jalur data digital. Modul ini lahir dari
pemetaan fungsi otak di `system/cognitive_brain.py` (lihat
`docs/COGNITIVE-BRAIN.md`), tetapi sengaja dibatasi sebagai **desain RTL untuk
simulasi dan pembelajaran**.

## Pernyataan batas (baca dulu)

- Ini **bukan alat medis**, bukan BCI, bukan implant, dan bukan antarmuka saraf.
- **Tidak terhubung** ke otak manusia hidup; tidak ada elektroda, kabel,
  radio, atau perangkat eksternal.
- **Tidak membaca, menyimpan, atau mengirim** data neural dari subjek mana pun.
- **Tidak memberikan stimulasi** atau aksi fisik ke tubuh.
- Angka "25 tahun" adalah penanda konfigurasi simulasi (gain `2` pada jalur
  memori), **bukan** data biologis, pengukuran, atau klaim usia subjek.
- Status fabrikasi: `NOT_READY`. Validasi klinis: `NOT_VALIDATED`.
- Segala penggunaan dengan subjek manusia memerlukan persetujuan tertulis,
  etika/medik legal, dan mitra berlisensi — **tidak tersedia di sini**.

## Pemetaan empat tahap kognitif

| Tahap | Otak (analogi) | Port / sinyal | Fungsi RTL |
|---|---|---|---|
| Indra | Mata, telinga, kulit | `n0..n3[1:0]` | fusi empat kanal sintetis berbobot `1,2,3,4` → `sense[4:0]` |
| Memori | Hippocampus | `mem[1:0]` | `sense + 2*mem` → `memory_w[4:0]` (gain profil referensi ~25 tahun) |
| Perencanaan | Korteks prefrontal | `intent[1:0]` | `memory_w + 2*intent` → `decision[4:0]`; `stage = intent` |
| Aksi | Korteks motorik/otot | `gate`, `act`, `blocked`, `irq` | aksi hanya bila ambang `decision[3]` tercapai **dan** `gate=1` |

`stage` bernilai `0` indra, `1` memori, `2` perencanaan, `3` aksi. Hanya tahap
`2`/`3` yang boleh menghasilkan aksi (`actionable = intent[1]`). Tanpa izin,
`blocked=1` dan `irq=1` pada tahap aksi — ini *consent gate*, bukan fitur medis.

## Bukti verifikasi

Jalur verifikasi terpisah dari scorecard hy4 utama agar skor 500/500 tidak
berubah. Tiga bukti dijalankan lokal, offline, tanpa kredensial:

1. **Model referensi vs RTL** — `chip/neuro25_reference.py`, 8192 vektor
   (4 kanal × `mem` × `intent` × `gate`), 0 mismatch.
2. **Icarus Verilog** — `chip/tb/tb_neuro25.v`, lint + kompilasi + `vvp`,
   8192 vektor, 49152 pengecekan, 0 error, 0 warning, waveform
   `chip/reports/tb_tom05_neuro25.vcd`.
3. **Sintesis Yosys** — `chip/synth/tom05_neuro25_gate.v`,
   `tom05_neuro25_netlist.json`, dan `tom05_neuro25.stat` (13 sel).

Laporan: `chip/reports/neuro25.json` (skema `tom05-neuro25-chip/1`),
`neuro25_verification.json`, `neuro25_iverilog.json`, `neuro25_synthesis.json`.

## Perintah

```bash
python3 chip/chip_cli.py neuro25          # jalankan ketiga bukti + laporan
python3 chip/chip_cli.py neuro25-agent    # profil agen khusus (JSON)
python3 chip/chip_cli.py fleet             # status 23 chip agen + NEURO-25 (baca saja)
tom05 --neuro25                           # ringkasan chip
tom05 --neuro25-agent                     # profil agen khusus
make neuro25                              # lewat Makefile
make neuro25-test                         # pengujian chip + agen
make fleet                                # status gabungan (read-only)
```

Status `PASS` pada laporan hanya berarti RTL cocok dengan model sintetis dan
dapat disintesis. Tidak ada kaitan dengan keselamatan, kelayakan medis, atau
kinerja pada sistem biologis.

## Agen khusus `neuro25.md`

Sumber kebenaran agen ada di `chip/neuro25_agent.py` (model
`tom05/tom05-flash-free`), didaftarkan di `system/hy4_manager.py` sebagai
`neuro25.md`, lalu disamakan ke agent/skill Copilot CLI oleh
`system/copilot_sync.py`. Agen ini hanya menjelaskan dan memverifikasi chip;
ia tidak memiliki izin untuk menghubungkan desain ke subjek manusia, membaca
data neural, atau mengubah status `NOT_READY`/`NOT_VALIDATED`.
