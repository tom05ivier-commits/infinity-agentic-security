<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Kebijakan Privasi Data Pribadi

Sistem ini **tidak menyimpan nilai sensitif dalam kode atau artefak publik**.
Data pribadi hanya ada di dokumen otorisasi lokal dan pengelola kredensial.

## Data yang dilindungi

| Label | Perlakuan |
|---|---|
| Email | Disamarkan menjadi `owner@example.invalid` |
| WhatsApp/telepon | Disamarkan menjadi `000000000000` |
| Tanda tangan digital | Disamarkan menjadi `(__signature__)` |
| Kata sandi/token | Ditolak & diganti `[REDACTED]`; tidak pernah dicetak |
| Tanggal lahir | Disamarkan menjadi `01-01-1970` |
| Lokasi | Disamarkan menjadi `Kota, Provinsi` |

## Modul

`security/privacy.py` menyediakan:
- `scan(text)` — hitung kemunculan per label **tanpa mengembalikan nilai**.
- `scan_secrets(text)` — hitung kredensial per bentuk (GitHub, OpenAI, Bearer,
  penugasan `api_key=...`) tanpa nilai.
- `redact(text)` / `safe_output(text)` — samarkan PII **dan** kredensial sebelum
  teks masuk log, chat, atau laporan.
- `sanitize_tree(root)` — sanitasi generik seluruh file teks.
- `verify_tree(root)` — audit paparan: path relatif, label, dan jumlah saja;
  berkas `.env` asli tidak dibaca, hanya mode izinnya dicek (0644 → temuan).
- `release_ready(root)` — status `SIAP` hanya bila privasi aman, kredensial
  ber-mode 0600, dan `credentials/.env` masuk `.gitignore`.

Karena pola bersifat generik (regex), skrip rilis **tidak perlu menanamkan**
nilai asli email, telepon, tanda tangan, atau kata sandi.

Perlindungan kunci API dari `api-key.sh` melengkapi ini: kunci disimpan di
`credentials/.env` (0600), tidak pernah dicetak/diaudit, hanya sidik jari
SHA-256. Lihat `docs/API-KEYGEN.md`.

## Integrasi

- `prepare_github.sh` memanggil `privacy.py sanitize` sebelum commit publik.
- `blue/dlp.py` menyamarkan `evidence` temuan.
- `data_delivery.py` menyamarkan payload sebelum menulis file.
- CLI: `python3 security/security_cli.py privacy scan|secrets|redact|sanitize|verify|release PATH`.
- Rilis: `python3 security/privacy.py release publish/infinity-agentic-security`
  harus berstatus `SIAP` sebelum push.

## Aturan

1. Jangan pernah menempelkan kata sandi/token di chat, log, README, atau file proyek.
2. Token GitHub tetap di `~/.copilot/config.json` dan dibaca hanya saat diperlukan.
3. Surat izin asli tetap lokal; rilis publik memakai templat sanitasi.
4. Setiap pelanggaran privasi adalah alasan untuk membatalkan rilis.

Verifikasi: `grep` di `publish/` untuk nilai sensitif harus menghasilkan "tidak ada".
