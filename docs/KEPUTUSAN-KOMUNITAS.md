<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Keputusan: platform komunitas IT Agenty

**Tanggal:** 21 November 2026
**Penetap keputusan:** Tomi vier, Owner / CEO (tanda tangan digital `(__signature__)`)
**Dasar:** instruksi pemilik dalam sesi kerja ini — "Semua" untuk empat opsi
yang ditawarkan, dengan rekomendasi analisis (a)+(c) pada
`docs/SYMPHONY-ANALYSIS.md`.

## Keputusan

IT Agenty memakai Symphony (88250/B3log) **hanya sebagai referensi arsitektur**.
Platform komunitas yang dipakai adalah `site/community/`, karya original dengan
lisensi `Tom05ivier-commits-1.0`, berjalan sebagai layanan `community` di port
`8781` dan ditautkan dari hub situs `site/index.html`.

Opsi menjalankan Symphony sebagai forum AGPLv3 (jalur b) **tidak dipilih untuk
sekarang**. Alasannya bukan keterbatasan teknis, melainkan kewajiban hukum:
copyleft jaringan AGPLv3 mewajibkan publikasi source bila kode dimodifikasi dan
dijalankan sebagai layanan, serta lisensi komersial berbayar untuk pemakaian
perusahaan. Memilih jalur itu tanpa keputusan sadar pemilik akan melanggar batas
`third-party-license-removal` dan prinsip bahwa lisensi IT Agenty tidak menimpa
lisensi pihak ketiga.

## Artefak terkait

| Artefak | Peran |
|---|---|
| `symphony-src/` | Sumber pihak ketiga, utuh, AGPLv3, tidak diubah |
| `docs/SYMPHONY-ANALYSIS.md` | Analisis, rekomendasi, dan pemetaan ide ke implementasi |
| `docs/SYMPHONY-DEPLOYMENT.md` | Opsi deploy Symphony bila diputuskan nanti |
| `site/community/` | Portal komunitas resmi IT Agenty |
| `system/services.json` | Registry: `community` aktif, `symphony` stand-by |

## Peninjauan ulang

Keputusan ini dapat ditinjau hanya bila pemilik secara tertulis memilih jalur
AGPLv3 atau membeli lisensi komersial, dan batas waktu izin yang berlaku masih
berlaku sampai 31 Desember 2027. Sampai saat itu, `symphony` sengaja tetap
berstatus tidak aktif di registry; supervisor akan menyalakannya otomatis bila
Docker Engine tersedia, tetapi itu tidak mengubah keputusan platform di atas.

— `(__signature__)`
