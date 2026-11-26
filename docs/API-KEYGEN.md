<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Pembangkit kunci API otomatis

Kemampuan ini diadaptasi dari HEX Hero Random Key Generator
(https://share.google/6GMmCzrbL3tEz57Ji): pembangkitan kunci acak kriptografis
di sisi lokal, setara Web Crypto API / `openssl rand -base64 32`.

Modul: `system/api_keygen.py` — wrapper: `./api-key.sh` — integrasi:
`python3 security/security_cli.py api-keygen ...`.

## Format & kekuatan

| Format | Panjang @256-bit | Contoh penggunaan |
|---|---|---|
| `base64` | 44 | environment variable, berkas konfigurasi |
| `hex` | 64 | kunci enkripsi, token basis data |
| `urlsafe` | 43 | JWT, token URL/query string |
| `alphanumeric` | 43+ | kode yang dibaca manusia |

Kekuatan: 128 / 256 / 384 / 512 bit. Jumlah: 1–100 kunci. Seluruh bytes
berasal dari CSPRNG (`secrets.token_bytes` / `secrets.choice`), bukan
`Math.random()`.

## Pemakaian

```bash
./api-key.sh generate --strength 256 --format urlsafe   # hanya sidik jari
./api-key.sh ensure                                     # AGENTY_API_KEY (default), buat bila belum ada
./api-key.sh status                                     # boolean, tanpa nilai
./api-key.sh load --name AGENTY_API_KEY                 # ADA + sidik jari
./api-key.sh guard                                      # audit privasi kunci
./api-key.sh rotate --name AGENTY_API_KEY               # rotasi kunci
./api-key.sh generate --show                            # RAHASIA: tampilkan nilai
eval "$(./api-key.sh load --name AGENTY_API_KEY --export)"  # ekspor ke shell
```

Lewat Python:

```python
from system.api_keygen import ensure_api_key, load_api_key

ensure_api_key("AGENTY_API_KEY")     # idempoten, otomatis saat pertama kali
key = load_api_key("AGENTY_API_KEY") # environment dulu, lalu credentials/.env
```

## Penyimpanan & keamanan

- Kunci disimpan di `credentials/.env` (mode `0600`, ditulis atomik). Berkas
  ini masuk `.gitignore` dan tidak pernah dipublikasikan.
- Secara default nilai kunci **tidak pernah** dicetak ke layar, log, atau
  chat. Yang tampil hanya sidik jari SHA-256 (16 hex) dan metadata.
- `--show` dan `--export` adalah opt-in eksplisit dan menyingkap nilai hanya
  ke stdout pemanggil; keduanya memberi peringatan ke stderr.
- Audit di `security/reports/api_keygen.jsonl` berisi metadata saja dan
  menolak baris yang mengandung pola kunci nyata. Sifatnya **append-only**:
  rotasi menambah catatan baru, tidak menimpa riwayat.
- `./api-key.sh guard` memeriksa mode 0600, `.gitignore`, audit, dan
  kebocoran nilai ke berkas lain. Hasilnya path dan alasan saja — tanpa nilai.
  Kode keluar 1 bila tidak AMAN; `make test` menjadikannya gate.
  `make score-bootstrap` membuat kunci otomatis di pemasangan baru.
- Kunci bersifat **per pemasangan**. Untuk kredit/cloud OpenCode tetap pakai
  `opencode auth login` sesuai `PANDUAN-OTORISASI-PUBLIK.md`; pembangkit ini
  mengelola kunci API lokal milik Anda sendiri.
