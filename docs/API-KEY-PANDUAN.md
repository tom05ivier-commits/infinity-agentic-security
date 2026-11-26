<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# API Key: ringkasan dan panduan pakai

Sumber: artikel BRIAPI, "API Key: Pengertian, Fungsi, dan Manfaatnya" —
<https://share.google/y66Q5NifnI617rsnW> (halaman developers.bri.co.id).

## Inti artikel

API key adalah kode unik yang dipakai sebagai gerbang pertama autentikasi dan
otorisasi. Di BRIAPI, API key berperan sebagai **Client ID** dalam kerangka
OAuth 2.0, yaitu identitas yang mewakili pengguna atau partner terdaftar. Ada
dua level otorisasi yang dibedakan artikel itu: otorisasi **proyek**, yang
memastikan aplikasi pemanggil memang memiliki akses dan mengidentifikasi
proyeknya, serta otorisasi **pengguna**, yang memastikan pemanggil adalah
pengguna terdaftar dan memiliki izin untuk permintaan tertentu.

Selain mengidentifikasi, API key dipakai untuk *tracking* dan *controlling*:
mencatat rangkaian panggilan, memblokir trafik anonim, membatasi jumlah
panggilan, mengenali pola trafik, dan menyaring permintaan. Artikel ini juga
menekankan bahwa API key saja tidak cukup. BRIAPI menambahkan **tanda tangan
HMAC-SHA256** pada request dan response supaya isi pesan tidak bisa diubah
oleh pihak yang tidak berwenang. HMAC menggabungkan fungsi hash dengan kunci
rahasia, sehingga tanda tangan hanya bisa dibuat oleh pihak yang memiliki
kunci tersebut.

Perlu dibedakan antara API key (Client ID) dan kunci rahasia (client secret).
Keduanya sering disebut "kredensial", tetapi perannya berbeda: ID mengatakan
*siapa* pemanggil, secret membuktikan *bahwa* pemanggil memang orang itu.
Karena itu, keduanya tidak boleh ditaruh di kode sumber, log, atau argumen
baris perintah.

## Praktik aman yang dipakai di sini

Utilitas `apikey_demo.py` mengikuti beberapa aturan yang berasal dari artikel
tersebut dan praktik umum keamanan API:

- Kredensial dibaca hanya dari variabel lingkungan `BRIAPI_CLIENT_ID` dan
  `BRIAPI_CLIENT_SECRET`, bukan dari argumen. Argumen baris perintah biasanya
  terekam di riwayat shell dan daftar proses.
- String kanonik yang ditandatangani terdiri dari metode, path, timestamp,
  nonce, dan hash SHA-256 dari body. Mengubah salah satu bagian akan mengubah
  tanda tangan.
- Perbandingan tanda tangan memakai `hmac.compare_digest`, bukan `==`, agar
  tidak membocorkan informasi lewat perbedaan waktu perbandingan.
- Timestamp ditolak bila selisihnya lebih dari 300 detik, dan nonce yang sudah
  dipakai ditolak. Ini menahan serangan replay, bukan hanya pemalsuan isi.
- Keluaran bawaan tidak pernah menampilkan API key ataupun tanda tangan
  lengkap. Bila header lengkap memang diperlukan, `--emit-file` menulisnya ke
  berkas dengan izin `0600`.

## Memakai utilitas

Periksa implementasi tanpa kredensial asli:

```sh
tom05 --apikey-check
tom05-apikey selftest
```

Bangun header bertanda tangan. Kunci diambil dari lingkungan, dan yang
tampil di layar sudah disamarkan:

```sh
export BRIAPI_CLIENT_ID='...'
export BRIAPI_CLIENT_SECRET='...'
tom05 --apikey-sign 'amount=1000'
```

Untuk header lengkap, tulis ke berkas dengan izin `0600`:

```sh
tom05-apikey sign --method POST --path /v1/payment --body 'amount=1000' \
  --emit-file /tmp/opencode/hy4-headers.json
```

Verifikasi header yang diterima:

```sh
tom05-apikey verify "$JSON_HEADER" --method POST --path /v1/payment --body 'amount=1000'
```

Cek usia kunci tanpa menyimpan kunci itu sendiri:

```sh
tom05 --apikey-rotate
```

Perintah ini menyimpan sidik jari SHA-256 dari Client ID beserta tanggal
pertama kali terlihat di berkas `0600`, lalu mengingatkan setelah 90 hari.
Berkasnya berisi sidik jari, bukan kunci, jadi tetap aman untuk dibaca saat
audit. Lokasinya bisa diubah lewat `BRIAPI_ROTATION_FILE`.

Samarkan kredensial dari log sebelum dicatat:

```sh
some_command 2>&1 | tom05 --apikey-redact >> app.log
```

Penyamaran mencakup nilai dari `BRIAPI_CLIENT_ID` dan `BRIAPI_CLIENT_SECRET`,
token GitHub, AWS, Slack, JWT, kunci privat, dan header Bearer.

## Pemeriksaan otomatis

Workspace memiliki dua pemeriksaan yang saling melengkapi. `make credential-audit`
memetakan *nama* penanda kredensial, sedangkan `make secret-scan` mencari
*nilai* yang menyerupai kredensial. Keduanya tidak mencetak nilai; yang
ditampilkan hanyalah path, baris, jenis pola, dan panjang. Keduanya juga
berjalan di GitHub Actions melalui `.github/workflows/secret-scan.yml`,
dan `make apikey-check` menjalankan uji tanda tangan dengan nilai buatan.

## Batasan yang perlu disadari

Ini adalah demo dan alat bantu, bukan klien BRIAPI resmi. Penyimpanan nonce
bersifat dalam-memori, sehingga cocok untuk satu proses saja; pada layanan
multi-proses, nonce sebaiknya disimpan di penyimpanan bersama seperti Redis.
Utilitas ini juga tidak menggantikan TLS, tidak mengimplementasikan alur OAuth
2.0 lengkap, dan tidak melakukan rotasi kunci. Sebelum dipakai terhadap API
riil, ikuti dokumentasi resmi penyedia untuk nama header, format canonical
string, dan aturan produksinya.

Laporan audit penanganan kredensial di workspace ada di
`security/reports/credential-handling-audit.md`.
