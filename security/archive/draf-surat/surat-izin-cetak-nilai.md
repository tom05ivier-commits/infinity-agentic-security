<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# SURAT IZIN PENCATETAN NILAI KONFIGURASI & STATUS (NON-SENSITIF)

> **STATUS: DRAF — BELUM BERLAKU.** Dokumen ini bukan otorisasi aktif.
> Berlaku hanya setelah pemilik mengisi kolom dan menandatangani secara manual
> di berkas ini. Tidak ada tanda tangan yang diisi oleh agen atau model.

**Nomor:** `IT-AGENTY/IZIN/2026/11-23-CETAK-NILAI`  
**Lampiran:** 1 (Daftar nilai yang boleh dicetak)  
**Perihal:** Izin terbatas untuk menampilkan nilai konfigurasi, status, dan metrik non-sensitif

---

Yang bertanda tangan di bawah ini:

| Keterangan | Isi |
|---|---|
| Nama | **Tomi vier** |
| Jabatan | **Owner / CEO — IT Agenty** |
| Unit | IT Agenty |
| Tanda tangan resmi | `(__signature__)` |

selanjutnya disebut **PEMBERI IZIN**.

Dengan ini memberikan izin kepada **IT Agenty / Tom05** untuk mencetak,
menampilkan, atau melaporkan nilai-nilai yang tercantum dalam Lampiran 1,
dengan ketentuan bahwa **nilai kredensial dan data pribadi tidak pernah
termasuk** dalam izin ini.

## 1. Ruang Lingkup

Pencetakan hanya diperbolehkan untuk nilai yang sudah bersifat publik atau
operasional non-rahasia, meliputi:

- konfigurasi model dan batas konteks (`ctl`, `context_length`, versi model);
- status koneksi dan kesehatan server lokal (nama, port, kode status HTTP);
- skor kualitas dan metrik kepatuhan (`chip_score`, `tom05_score`, `security_score`);
- jalur berkas konfigurasi (tanpa isi kredensial di dalamnya);
- ringkasan audit dalam bentuk status (`DIIZINKAN`/`DITOLAK`), bukan nilai rahasia.

## 2. Batasan Tegas

Izin ini **TIDAK** mencakup, dan secara eksplisit melarang pencetakan:

- token akses, kata sandi, kunci API, secret, atau nilai kredensial lainnya;
- data pribadi (nama lengkap, email, nomor telepon, tanggal lahir, alamat);
- isi `~/.copilot/config.json`, `~/.copilot/providers.json`, atau
  `/root/.config/opencode/auth.json`;
- nilai yang masuk kategori `token-export` dalam `surat-izin-github.md`;
- apa pun yang dilarang oleh `PANDUAN-OTORISASI-PUBLIK.md` dan `DENIED`
  pada `security/auto_approval.py`.

Setiap permintaan pencetakan kredensial tetap **DITOLAK** dan dicatat sebagai
`token-export` di `security/reports/github_actions.jsonl`.

## 3. Tata Cara

- Pencetakan dilakukan lewat perintah baca-saja (`status`, `--score`, `--ctl`,
  `curl /health`, `curl /v1/models`) yang tidak menampilkan header otorisasi.
- Bila suatu perintah berisiko menampilkan kredensial, agen wajib berhenti dan
  meminta konfirmasi tertulis baru.
- Setiap pencetakan dicatat di `security/reports/print_values.jsonl` sebagai
  jejak audit, tanpa menyimpan nilai sensitif.

## 4. Masa Berlaku & Pencabutan

Berlaku sejak tanggal yang diisi pemilik hingga **31 Desember 2027**, dapat
dicabut sewaktu-waktu secara tertulis. Bila ragu, pelaksana wajib berhenti dan
meminta konfirmasi tertulis baru.

## 5. Pernyataan

Dokumen ini adalah **draf template**. Ia bukan sumber otoritas baru, bukan
amandemen `LICENSE`, dan tidak melegitimasi pencetakan kredensial. Tanda
tangan `(__signature__)` **tidak** dilekatkan oleh agen atau otomatisasi.

## 6. Tanda Tangan

| Peran | Penanda / Tanda tangan | Keterangan |
|---|---|---|
| Pemberi Izin | **Tomi vier** — Owner / CEO | Diisi manual oleh pemilik |
| Tanda tangan pemilik | `__________________________` | Khusus `(__signature__)`, oleh Tomi vier |
| Tanggal | `[DIISI MANUAL]` | — |
| Pelaksana | **IT Agenty / Tom05** | Operator Sistem |
| Tanda tangan pelaksana | `__________________________` | Diisi manual oleh operator |

---

## Lampiran 1 — Daftar Nilai yang Boleh Dicetak

| Nilai | Sumber | Contoh |
|---|---|---|
| `ctl` / `context_length` | `tom05 --ctl`, `/v1/models` | `100000000` |
| Versi model & server | `/api/info`, `--version` | `2.4.1` |
| Status server | `curl /health` | `{"status":"ok"}` |
| Skor kualitas | `chip --score`, `tom05 --score` | `100/100` |
| Status koneksi | `connection_status.py` | `TERHUBUNG` |
| Kode status HTTP | probe endpoint lokal | `200` |

**Dilarang dicetak:** token, password, API key, secret, isi berkas kredensial,
dan data pribadi — tanpa kecuali.
