<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Deployment Symphony di IT Agenty

Dokumen ini mencatat cara menjalankan Symphony sebagai layanan opsional dan
batasan yang berlaku di lingkungan workspace saat ini. Konfigurasi ini adalah
karya IT Agenty; citra `b3log/symphony` dan seluruh kode di `symphony-src`
tetap tunduk pada lisensi AGPLv3 aslinya.

## Artefak yang dibuat

Sumber pihak ketiga di-clone ke `/root/workspace/symphony-src` dengan
`git clone --depth 1 --single-branch`. Isi direktori itu sengaja tidak diubah,
termasuk `LICENSE`, `THIRD_PARTY_LICENSE`, dan seluruh header AGPLv3-nya.

Deployment disiapkan di tiga berkas:

| Berkas | Fungsi |
|---|---|
| `docker-compose.symphony.yml` | Stack dua kontainer: MariaDB 10.11 dan `b3log/symphony`, dengan volume bernama untuk database dan direktori upload `~/sym/upload/`. |
| `.env.symphony.example` | Template kredensial dan port (default `8780`). Salin ke `.env.symphony` lalu ganti sandi sebelum digunakan. |
| `scripts/symphony-deploy.sh` | Penjaga idempoten yang dipanggil supervisor. Menunggu Docker Engine bila belum aktif, menyiapkan `.env.symphony`, lalu menjalankan dan memantau `docker compose up -d`. |

Port yang dipakai adalah `8780` untuk antarmuka Symphony dan `8781` untuk
portal komunitas IT Agenty yang terpisah. Keduanya terikat ke `127.0.0.1`
sehingga tidak terekspos ke jaringan publik tanpa terowongan eksplisit.

## Status di lingkungan ini

Pemeriksaan menunjukkan Docker CLI `29.10.0` dan Compose `v5.8.0` tersedia,
tetapi **Docker Engine tidak berjalan** — `docker info` gagal karena
`/var/run/docker.sock` tidak ada dan biner `dockerd` tidak ditemukan. Di
lingkungan ini juga tidak ada Java, Maven, MySQL, maupun Redis, sehingga
menjalankan Symphony dari sumber juga tidak memungkinkan.

Yang sudah terverifikasi adalah sintaks Compose:

```bash
docker compose --env-file .env.symphony -f docker-compose.symphony.yml config
```

Perintah itu berhasil merender konfigurasi dengan `JDBC_URL`, `depends_on`
berbasis `service_healthy`, dan port `127.0.0.1:8780:8080` yang benar.
Wrapper tidak lagi keluar dengan kode `1` ketika Engine tidak aktif: ia tetap
hidup sebagai penjaga, mencatat status `MENUNGGU` sekali per perubahan keadaan,
lalu memeriksa ulang tiap `SYMPHONY_WAIT_SECONDS` (default 30 detik). Ini
menghentikan badai restart supervisor pada lingkungan tanpa `dockerd`.

## Cara mengaktifkan nanti

Begitu Docker Engine tersedia pada host (sesuai `surat-izin-host.md`),
langkahnya:

```bash
cp .env.symphony.example .env.symphony
# edit .env.symphony: ganti kedua sandi default
curl -fsS http://127.0.0.1:8780/ | head
```

Tidak perlu menjalankan wrapper secara manual: supervisor sudah mengenal
layanan `symphony` dari `system/services.json` sebagai layanan `process`
(bukan `http`), karena yang dipantau adalah proses penjaga, bukan port 8780
selagi Docker belum aktif. Begitu `docker info` berhasil, penjaga yang sudah
berjalan otomatis menjalankan stack — tidak perlu restart supervisor. Jika
Symphony mengembalikan redirect saat first-run, selesaikan wizard awalnya
terlebih dahulu. Pendekatan ini mencegah `restarts` layanan terus bertambah
saat Docker belum tersedia.

## Catatan lisensi

Meng-clone dan mempelajari kode diperbolehkan selama lisensi asli dipertahankan.
Menjalankan Symphony sebagai layanan jaringan memicu kewajiban AGPLv3 bila
kode dimodifikasi; organisasi yang memakainya untuk kegiatan komersial perlu
lisensi komersial. Karena itu portal komunitas IT Agenty dibangun sebagai
karya baru yang terpisah dengan lisensi `Tom05ivier-commits-1.0`, bukan turunan
atau salinan Symphony. Analisis lebih lengkap ada di `docs/SYMPHONY-ANALYSIS.md`.
