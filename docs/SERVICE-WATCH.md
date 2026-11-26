<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
-->

# Service Watch — watchdog layanan supervisor

`system/service_watch.py` adalah layanan kecil yang membaca `system/services.json`,
memeriksa seluruh layanan yang terdaftar, menulis laporan ke
`system/reports/service_watch.json`, dan menyajikan status di HTTP lokal.

## Bahan dari GitHub

Diadaptasi dari **PyUptimeKit** — https://github.com/HarikrishnanK9/PyUptimeKit
pada commit `79e3a3e4ed4f12166ad71ff38eaa8e291ef85748`.

Yang dipakai hanyalah pola probe TCP `connect_ex` + `time.perf_counter` dari
`src/pyuptimekit/monitors/tcp.py`, ditulis ulang tanpa ketergantungan Pydantic
agar berjalan dengan Python standar. Penulisan ulang ini disebut "sempurnakan":
lebih ringan, memakai `AGENTY_PORT`-style eksplisit (bukan variabel `PORT`),
terintegrasi dengan registry supervisor, dan memakai header lisensi IT Agenty.

Lisensi MIT asli tetap dipertahankan untuk bagian yang diadaptasi:

```text
MIT License

Copyright (c) 2026 PyUptimeKit Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Kode IT Agenty di sekitarnya tetap tunduk pada `Tom05ivier-commits-1.0`.
Lisensi pihak ketiga tidak dihapus atau diubah.

## Pemasangan di supervisor

```bash
./run_system.sh service-add \
  --name service-watch --kind http --port 8782 \
  --health /health --cmd python3 system/service_watch.py serve --port 8782
```

Supervisor melakukan hot-reload registry setiap siklus, jadi layanan langsung
hidup tanpa restart. Verifikasi lewat `system/reports/heartbeat.json`.

## Pemakaian

```bash
make service-watch                              # alias python3 system/service_watch.py once
make service-watch-test                         # 9 tes unit
python3 system/service_watch.py serve           # HTTP di 127.0.0.1:8782
python3 system/service_watch.py serve --port 8783 --interval 5
```

Setiap layanan baru juga perlu RTL verifikasi server. Jalankan generator
setelah `service-add`, lalu cek:

```bash
python3 chip/server_chip_gen.py
python3 chip/chip_cli.py server-chip   # PASS, 15 server, 120 vektor
```

Endpoint:

- `GET /health` — status boolean sederhana untuk supervisor.
- `GET /status` — laporan JSON lengkap.
- `GET /` — halaman HTML ringkas (semua nilai di-escape).

## Perilaku

- `kind: http` → GET ke `health` pada port lokal; 200 = `UP`.
- `kind: tcp` / `monitor` → `connect_ex` + latensi; tidak menjalankan proses.
- `kind: process` → status diambil dari `heartbeat.json` milik supervisor.
- Kegagalan baca registry menghasilkan laporan kosong, bukan crash.
- Tiap 10 detik laporan diperbarui; budget CPU sengaja kecil.
