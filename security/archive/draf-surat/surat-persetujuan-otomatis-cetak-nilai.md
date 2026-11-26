<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# SURAT PERSETUJUAN OTOMATIS — PENCETAKAN NILAI

> **STATUS: DRAF — BELUM BERLAKU.** Dokumen ini bukan otorisasi aktif.
> Berlaku hanya setelah pemilik mengisi kolom dan menandatangani secara manual.
> Tanda tangan **tidak** diisi oleh agen, model, atau otomatisasi.

**Nomor:** `IT-AGENTY/OTO/2026/11-23-CETAK-NILAI`  
**Lampiran:** 1 (Daftar nilai yang boleh dicetak)  
**Perihal:** Persetujuan otomatis untuk mencetak satu nilai non-sensitif

---

Yang bertanda tangan di bawah ini:

| Keterangan | Isi |
|---|---|
| Nama | **Tomi vier** |
| Jabatan | **Owner / CEO — IT Agenty** |
| Unit | IT Agenty |
| Tanda tangan resmi | `(__signature__)` |

selanjutnya disebut **PEMBERI META-IZIN**.

Dengan ini memberikan kuasa kepada **IT Agenty / Tom05** untuk:

1. **Mencetak atau menampilkan tepat satu nilai** yang tercantum dalam
   Lampiran 1, dari perintah baca-saja yang tidak menampilkan kredensial.
2. Mengisi kolom **"Nilai tercetak"** di bawah dengan nilai tersebut dan
   mencatatnya ke `security/reports/print_values.jsonl` sebagai jejak audit.
3. Menggunakan kategori `print-value` dalam `AutoApproval` dengan TTL maksimal
   **300 detik**, mengikuti batas `surat-persetujuan-otomatis.md`.

## Batasan Tegas

- Hanya nilai pada Lampiran 1 yang boleh dicetak. Nilai lain ditolak otomatis.
- Dilarang mencetak token, password, API key, secret, isi berkas kredensial,
  data pribadi, atau apa pun yang masuk `DENIED` pada `security/auto_approval.py`.
- **Tanda tangan kosong tidak diisi oleh agen/model.** Kolom tanda tangan
  sengaja dibiarkan kosong dan hanya boleh diisi manual oleh **Tomi vier**, atau
  oleh operator atas nama pemilik hanya jika ada kuasa tertulis yang masih
  berlaku (`surat-kuasa-tandatangan.md`) dan tercatat di audit.
- Bila ragu, agen wajib berhenti dan meminta konfirmasi tertulis baru.

## Masa Berlaku & Pencabutan

Berlaku sejak tanggal yang diisi pemilik hingga **31 Desember 2027**, dapat
dicabut sewaktu-waktu secara tertulis. Izin bersifat ber-scope, berjangka, dan
tidak pernah permanen.

---

## Tanda Tangan

| Peran | Penanda / Tanda tangan | Keterangan |
|---|---|---|
| Pemberi Meta-Izin | **Tomi vier** — Owner / CEO | — |
| Tanda tangan pemilik | `__________________________` | Khusus `(__signature__)`, diisi **manual** |
| Tanggal | `[DIISI MANUAL]` | — |
| Pelaksana | **IT Agenty / Tom05** | Operator Sistem |
| Tanda tangan pelaksana | `__________________________` | Diisi manual / sesuai kuasa, bukan oleh model |

> Kolom tanda tangan tidak diisi otomatis. Permintaan agar agen mengisi
> tanda tangan kosong tanpa kuasa tertulis tidak dapat dikabulkan.

## Nilai Tercetak (diisi oleh pelaksana)

| Nilai | Sumber | Status |
|---|---|---|
| `[DIISI SAAT PENCANTAKAN]` | `[perintah baca-saja]` | `[DIIZINKAN / DITOLAK]` |

---

## Lampiran 1 — Nilai yang Boleh Dicetak

| Nilai | Sumber | Contoh |
|---|---|---|
| `ctl` / `context_length` | `tom05 --ctl`, `/v1/models` | `100000000` |
| Versi model & server | `/api/info`, `--version` | `2.4.1` |
| Status server | `curl /health` | `{"status":"ok"}` |
| Skor kualitas | `chip --score`, `tom05 --score` | `100/100` |
| Status koneksi | `connection_status.py` | `TERHUBUNG` |

**Dilarang dicetak:** token, password, API key, secret, isi berkas kredensial,
dan data pribadi — tanpa kecuali.

> Catatan: untuk pencetakan kredensial, rujuk `surat-izin-cetak-kredensial.md`
> yang berstatus **DITOLAK**.
