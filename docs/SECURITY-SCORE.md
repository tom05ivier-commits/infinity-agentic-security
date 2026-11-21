<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Skor keamanan 100/100

`security/score.py` menghitung skor dari **12 kontrol yang dapat dibuktikan**.
Skor = `100 × kontrol_lulus / total_kontrol`. Laporan:
`security/reports/security_score.json`.

```bash
python3 security/score.py                       # ringkas
python3 security/security_cli.py score --json  # mesin
make security-score                             # lewat Makefile
make dashboard                                  # sinkronkan kartu Skor Kualitas
make score                                      # chip + keamanan + dashboard
make score-bootstrap                            # bangkitkan laporan di clone kosong
```

Perintah skor mengembalikan kode 0 hanya bila 100/100; kode 1 bila ada kontrol
yang gagal. `make test` menjadikannya gate bersama skor chip dan
`./api-key.sh guard` (juga kode 1 bila kunci tidak aman).

## Dua belas kontrol

verifikasi kepatuhan, efikasi pertahanan, firewall & drill, antivirus & DLP,
privasi rilis publik, kunci API aman, kerahasiaan kredensial, integritas
berkas, izin terbatas & diaudit, chip terverifikasi, pemindaian rahasia, dan
respons insiden.

## Risiko simulasi bukan penalti

`risiko_simulasi` (dari `efficacy.json`) sengaja **tidak** mengurangi skor.
Serangan red-team yang terdeteksi adalah bukti kontrol bekerja; menghilangkan
alertnya berarti memalsukan keamanan. Angka itu tetap dilaporkan terpisah
sebagai informasi.

Semua bukti berupa status, jumlah, dan path — tidak pernah nilai kredensial.
