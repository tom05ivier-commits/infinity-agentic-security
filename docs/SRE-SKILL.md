<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
-->

# Skill sre-engineer — replika dan pemasangan di supervisor

## Sumber GitHub

Replika ini diadaptasi dari `skills/sre-engineer/SKILL.md` pada:

- repositori: https://github.com/jshsakura/awesome-opencode-skills
- lisensi: MIT, Copyright (c) 2026 VoltAgent
- berkas: `skills/sre-engineer/SKILL.md`

Perubahan yang dibuat di workspace IT Agenty:

- frontmatter memakai `license: Tom05ivier-commits-1.0` untuk turunan IT Agenty;
- referensi operasional diganti ke `system/services.json`, `service_watch.json`,
  dan `heartbeat.json` milik workspace ini;
- aturan kerja diterjemahkan ke pemeriksaan terukur oleh `system/sre_watch.py`;
- ditambahkan batas eksplisit: tidak mengubah lisensi/izin/registry/port saat triage.

Lisensi MIT asli tetap dipertahankan untuk teks yang diadaptasi:

```text
MIT License

Copyright (c) 2026 VoltAgent

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

Kode dan dokumentasi IT Agenty tetap tunduk pada `Tom05ivier-commits-1.0`.
Lisensi pihak ketiga tidak dihapus atau ditimpa.

## Pasang di supervisor

```bash
./run_system.sh service-add --name sre-watch --kind process \
  --cmd python3 system/sre_watch.py loop --interval 60
python3 chip/server_chip_gen.py
python3 chip/chip_cli.py server-chip
```

Supervisor melakukan hot-reload registry, jadi proses langsung hidup tanpa restart.
Verifikasi lewat `system/reports/heartbeat.json`.

## Pemakaian

```bash
make sre-watch                 # sekali jalan, cetak JSON
make sre-watch-test            # 7 tes unit
python3 system/sre_watch.py loop --interval 60
```

Berkas yang dihasilkan:

- `system/reports/sre_watch.json` — hasil triage terakhir;
- `system/reports/sre_history.jsonl` — riwayat availability (maks. 200 sampel).

Keluaran mengikuti struktur skill: boundary, evidence, asumsi, owner ranking,
rekomendasi terkecil, validasi normal/failure/recovery, risiko residual.
Layanan ber-`kind` `monitor` hanya dicatat di kolom `informational`: ia
tidak dijalankan supervisor, jadi tidak boleh masuk denominator SLO dan
membuat alarm palsu seperti `port-14713`. Target default 99% dapat diubah
dengan `--target` (bukan menaikkan SLO secara sepihak; perubahan target
tercatat di laporan).
