<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Akselerator AI tom05 (TAI-1)

`tom05_ai_accel` adalah modul RTL kombinasional orisinal IT Agenty untuk
inferensi AI skala kecil. Modul ini mengambil ide arsitektur dari laporan
AIMultiple, *Top 30+ AI Chip Makers: NVIDIA & Its Competitors* (diperbarui
13 Oktober 2026), tautan: https://aimultiple.com/ai-chip-makers.

Laporan tersebut memetakan lebih dari 30 produsen dan arsitektur: NVIDIA
(Hopper/Blackwell/Vera Rubin), AMD (MI300/MI400, CDNA), Intel (Gaudi, Crescent
Island), Qualcomm (Cloud AI 100, AI200/AI250, High Bandwidth Compute), Groq
(LPU), SambaNova (RDU), Cerebras (wafer-scale engine), d-Matrix (Corsair,
in-memory compute), Rebellions, Tenstorrent, Positron, dan Etched. TAI-1
hanya mengadaptasi **ide**-nya menjadi empat profil dataflow yang bisa
diverifikasi dengan model referensi Python, Icarus Verilog, dan simulator
browser — bukan salinan IP, bukan desain pihak ketiga, dan bukan klaim
kinerja setara produk komersial.

## Arsitektur

Empat jalur aktivasi 2-bit (`a0`–`a3`) diproses memakai profil yang dipilih
`mode[1:0]`:

| mode | Profil | Fungsi dot product | Inspirasi |
|---|---|---|---|
| `00` | TENSOR | `a0 + 2a1 + 3a2 + 4a3` | MAC berbobot GPU/TPU (NVIDIA, AMD) |
| `01` | LPU | `4a0 + 3a1 + 2a2 + a3` | aliran deterministik (Groq, Etched) |
| `10` | NEARMEM | bobot SRAM bila `hit`, jika tidak jalur luar | komputasi dekat memori (d-Matrix, Qualcomm HBC) |
| `11` | MESH | `2 × (a0 + a1 + a2 + a3)` | reduksi seragam wafer-scale (Cerebras) |

Keluaran:

- `score[4:0]` — hasil dot product (maksimal 30, sehingga 5 bit cukup).
- `level[1:0]` — kuantisasi `score >> 3` menjadi empat level.
- `hit` — residensi lokal, OR dari bit tinggi keempat aktivasi.
- `irq` — aktif bila `level[1]` tinggi dan `irq_clear` belum di-set.
- `ready` — selalu 1 karena seluruh jalur kombinasional.

Semua sinyal ditulis sebagai `assign` murni. Ini membuat RTL, model Python
(`chip/reference.py::tom05_ai_accel`), testbench Icarus, dan preset simulator
browser menghasilkan vektor yang identik.

## Verifikasi

```bash
python3 chip/chip_cli.py ai-chip     # profil + verifikasi modul (read-only)
python3 chip/chip_cli.py verify      # seluruh model referensi
python3 chip/chip_cli.py iverilog    # lint + kompilasi + vvp + VCD
python3 chip/chip_cli.py synth       # ringkasan sintesis Yosys
./site/chip/test_presets.sh          # preset browser, termasuk TAI-1
python3 chip/chip_cli.py score       # scorecard kualitas (target 100/100)
make chip-verify                     # semuanya sekaligus
```

Bukti saat ini: 11 modul / 4.916 vektor pada verifikasi model, 16.200
pengecekan Icarus tanpa warning, 431 sel hasil sintesis, dan 6 preset browser
dengan 0 mismatch.

## Layanan supervisor

TAI-1 terdaftar di `system/services.json` lewat `./run_system.sh service-add`
dan dijalankan supervisor tanpa restart manual:

| Layanan | Kind | Port/Fungsi | Perintah |
|---|---|---|---|
| `ai-chip` | `http` | 8783, health `/health` | `python3 system/ai_chip_service.py` |
| `ai-chip-watch` | `process` | watchdog verifikasi tiap 60 detik | `python3 chip/chip_watch.py` |

`ai-chip` melayani `GET /health`, `/`, `/status`, `/module`, dan `/capabilities`
dalam JSON read-only (status menyertakan timestamp UTC). Ia hanya membaca
artefak di `chip/reports/` dan tidak menjalankan verifikasi berat saat ada
permintaan. `ai-chip-watch` menjalankan `verify`, `iverilog`, dan `score` tiap
siklus, membaca status sintesis dan preset browser, lalu menulis
`system/reports/ai_chip_watch.json` secara atomik. Keduanya tidak membuka
koneksi keluar, tidak membaca
kredensial, dan status fabrikasi tetap `NOT_READY`.

Setiap perubahan registry wajib diikuti `python3 chip/server_chip_gen.py`
supaya RTL verifikasi server (`srv_ai_chip.v`, `srv_ai_chip_watch.v`) tetap
lengkap. Cek supervisor dengan `./run_system.sh supervisor-status`.

## Batasan

- Ini desain dan logika digital, **bukan fabrikasi silikon**. Status fabrikasi
  tetap `NOT_READY` sampai ada proses fisik dan mitra yang sah.
- Bukan model neural, tidak memuat bobot pihak ketiga, dan tidak melakukan
  training. Tidak ada klaim akurasi atau TOPS/Watt seperti produk komersial.
- Nama dan angka produk pihak ketiga dipakai hanya sebagai rujukan arsitektur.
  Lisensi, paywall, dan mekanisme pembayaran pihak ketiga tetap tidak diubah
  dan tidak tercakup oleh `Tom05ivier-commits-1.0`.
- Kode ini mengikuti lisensi IT Agenty `Tom05ivier-commits-1.0`, Copyright
  (c) 2026 Tomi vier.
