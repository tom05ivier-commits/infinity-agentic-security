<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Analisis Data & Rancangan Chip Firewall

## 1. Analisis data yang tersedia

Sumber: `security/firewall/rules.json` (policy userspace, bukan kernel).

| Field | Isi saat ini | Arti |
|---|---|---|
| `version` | 1 | versi skema policy |
| `license` | `Tom05ivier-commits-1.0` | lisensi artefak |
| `denied_ports` | `tcp/23`, `tcp/65534`, `tcp/9999` | port yang ditolak |
| `allowed_ports` | `tcp/22`, `tcp/8765` | port yang diizinkan |
| `blocked_ips` | 1 entri | alamat IP diblokir |

Data ini dihasilkan lewat `security/auto_config.py apply()` dan diaudit di
`security/reports/auto_configs.jsonl`. Sifatnya **kebijakan**, bukan aturan
packet-filtering kernel — sesuai aturan #6 AGENTS.md (`CapBnd = 0`).

## 2. Ide rancangan chip firewall

Tujuan: **prototype RTL** yang mengubah aturan allow/deny menjadi logika
kombinasional yang bisa diverifikasi exhaustif — bukan pengganti firewall kernel.

### 2.1 Modul `firewall_match`
- Input: `p0..p3` (4-bit port yang dinilai), `r0..r3` (4-bit port aturan), `enable`.
- Output: `hit` = 1 bila port cocok dengan aturan dan aturan aktif.
- Fungsi: `hit = ~(p0^r0) & ~(p1^r1) & ~(p2^r2) & ~(p3^r3) & enable`.

### 2.2 Modul `firewall_decide`
- Input: 4-bit port, aturan `deny` dan `allow` masing-masing 4-bit + enable.
- Output: `decision` = 1 (allow) hanya bila aturan allow cocok **dan** aturan deny tidak cocok.
- Fungsi: `decision = allow_hit & ~deny_hit` — **deny memiliki prioritas**.

Ini mencerminkan praktik firewall umum: aturan tolak menang atas aturan izin.

## 3. Batas jujur

1. Ini **prototype 4-bit** (16 nilai port), bukan implementasi 16-bit penuh
   (65536 port). Dipilih agar verifikasi exhaustif tetap cepat.
2. Chip ini **tidak** terhubung ke kernel/network stack. Ia hanya memodelkan
   keputusan kebijakan; tidak memfilter packet sungguhan.
3. Tidak ada izin `capbnd`/`NET_ADMIN` yang diberikan lewat rancangan ini —
   eskalasi sudah dicabut dan tetap dicabut.
4. Tidak mengubah `MODULES` utama `chip/reference.py` (10 modul, 2868 vektor,
   5960 check) agar skor chip 100/100 tidak rusak. Jalur verifikasi terpisah.

## 4. Alur kerja cari bug & uji coba

`chip/firewall_drill.py` menjalankan:

1. **Verifikasi exhaustif**: RTL vs model referensi untuk semua vektor.
2. **Mutation testing**: menyuntik 4 bug ke salinan RTL (flip operator), lalu
   memastikan setiap bug **terdeteksi** sebagai mismatch. Jika ada mutan yang
   lolos, drill gagal — ini cara mencari celah verifikasi.
3. Menulis laporan `chip/reports/firewall_chip.json` dengan status, jumlah
   vektor, jumlah mutan terdeteksi, dan `license`.
4. Exit code 0 hanya bila verifikasi PASS dan semua mutan terdeteksi.

Perintah: `python3 chip/firewall_drill.py`

## 5. Integrasi ke commit

File yang ditambahkan:
- `chip/rtl/firewall_match.v`, `chip/rtl/firewall_decide.v`
- `chip/firewall_reference.py`
- `chip/firewall_drill.py`
- `chip/tests/test_firewall_chip.py`
- `docs/FIREWALL-CHIP-ANALYSIS.md`
- laporan `chip/reports/firewall_chip.json`

Semua memuat header SPDX `Tom05ivier-commits-1.0` / `Copyright (c) 2026 Tomi vier`.
Commit lokal dilakukan setelah drill & tes lulus. Tidak push tanpa perintah.
