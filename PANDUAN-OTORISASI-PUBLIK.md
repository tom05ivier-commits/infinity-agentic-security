<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Panduan Otorisasi untuk Pemasangan Publik hy4

## Prinsip utama

**Token tidak dibagikan.** Setiap pemasangan menggunakan kredensial akunnya
sendiri. Repo publik hanya berisi kode dan dokumentasi, bukan token.

Alasan:
- token adalah identitas akun (kuota, tagihan, audit);
- token bersama tidak dapat diaudit per pemakai;
- pelanggaran dapat menyebabkan pencabutan akun;
- prinsip least privilege harus dipertahankan.

## Kredensial per pemasangan

| Komponen | Lokasi lokal | Cara membuat |
|---|---|---|
| OpenCode / model hy4 | `~/.config/opencode` | `opencode auth login` |
| Copilot CLI | `~/.copilot/config.json` | `copilot login` |
| Bridge hy4 | `~/.copilot/providers.json` | dibuat oleh `copilot login` + `manage_hy4.sh copilot-sync` |

Nilai kredensial **tidak pernah** boleh:
- ditaruh di `README.md`, `AGENTS.md`, atau file sumber;
- dikirim ke chat, log, atau issue;
- dimasukkan ke repository publik.

## Langkah pemasangan baru

```bash
git clone https://github.com/tom05ivier-commits/infinity-agentic-security.git
cd infinity-agentic-security

# Otorisasi sesuai akun pemakai
opencode auth login
copilot login

# Samakan agent/command hy4 ke Copilot CLI
./manage_hy4.sh copilot-sync

# Verifikasi tanpa menampilkan rahasia
./hy4-auth-check.sh
```

Hasil yang diharapkan:

```
Status: SIAP
Publik: AMAN (jumlah file)
```

Jika status `PERLU TINDAKAN`, ulangi login lalu jalankan pemeriksa lagi.

## Pemeriksa `hy4-auth-check.sh`

Skrip ini:
1. mendeteksi keberadaan kredensial OpenCode/Copilot hanya sebagai **boolean**;
2. memindai `publish/` untuk pola token nyata;
3. mengabaikan placeholder dokumentasi seperti `example.invalid` atau `token-anda`;
4. tidak pernah mencetak nilai token.

Jangan menggunakan `opencode auth export` di lingkungan publik karena perintah
itu menampilkan kredensial.

## Rilis maintainer

Sebelum push:

```bash
./hy4-auth-check.sh
bash prepare_github.sh
bash prepare_hy4_repo.sh
./hy4-auth-check.sh
bash update_all.sh
```

`prepare_github.sh` dan `prepare_hy4_repo.sh` sudah menyertakan sanitasi privasi.
Pemeriksa memberi lapisan kedua sebelum rilis.
