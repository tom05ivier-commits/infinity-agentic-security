---
name: sre-engineer
description: "Gunakan untuk pekerjaan reliability engineering: SLO, error budget, kualitas alert, dan ketahanan layanan IT Agenty."
license: Tom05ivier-commits-1.0
compatibility: opencode
---

<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier

  Replika dari skill "sre-engineer" pada jshsakura/awesome-opencode-skills
  (MIT, Copyright (c) 2026 VoltAgent), commit 33b2cea7752ffb0e0c5e2b2f0abec.
  Dimodifikasi untuk workspace IT Agenty. Teks lisensi MIT asli ada di
  docs/SRE-SKILL.md. Kode turunan tetap Tom05ivier-commits-1.0.
-->

# Skill sre-engineer

Gunakan skill ini untuk pekerjaan reliability engineering di workspace IT Agenty.

## Sumber data

- `system/services.json` — registry layanan supervisor.
- `system/reports/service_watch.json` — status layanan dari watchdog.
- `system/reports/heartbeat.json` — heartbeat supervisor.
- `system/reports/sre_watch.json` — hasil penilaian SLO/error budget.

## Aturan kerja

1. Bedakan sinyal nyata dari noise. Layanan `kind: monitor` tidak masuk
   denominator SLO agar kandidat port seperti `14713` tidak jadi alarm palsu.
2. Hitung availability hanya dari layanan aktif yang dapat dinilai. Jangan
   mengklaim regresi bila tidak ada data historis.
3. Gunakan error budget 0,99 sebagai target default, kecuali pemilik menetapkan
   lain secara tertulis.
4. Berikan rekomendasi terkecil yang reversibel: perbaiki satu layanan yang
   benar-benar turun, bukan mengubah seluruh registry.
5. Triage tidak boleh mengubah lisensi, izin, registry, atau port tanpa
   otorisasi tertulis dari pemilik.
6. Semua akses bersifat lokal dan read-only, kecuali perintah yang memang
   dijalankan pemilik secara eksplisit.

## Eksekusi otomatis

```bash
make sre-watch          # satu putaran penilaian
make sre-watch-test     # pengujian eksekusi
python3 system/sre_watch.py loop --interval 60
```

Layanan `sre-watch` terdaftar sebagai proses supervisor di `system/services.json`.
Setiap penambahan layanan wajib menjalankan `python3 chip/server_chip_gen.py`
agar RTL verifikasi server tetap lengkap.

## Batas lisensi

Teks asli berlisensi MIT, Copyright (c) 2026 VoltAgent. Modifikasi IT Agenty
berada di bawah `Tom05ivier-commits-1.0`. Lisensi pihak ketiga tidak dihapus.
