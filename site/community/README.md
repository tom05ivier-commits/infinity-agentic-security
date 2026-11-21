<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
-->

# IT Agenty Community

Portal komunitas mandiri untuk berbagi posting dan balasan. **Ini karya baru
yang ditulis dari awal** — bukan salinan, turunan, atau port dari Symphony / kode
berlisensi AGPLv3. Tidak ada baris kode Symphony di direktori ini. Lisensi yang
berlaku hanyalah **Tom05ivier-commits-1.0**, pemilik **Tomi vier**.

## Tujuan

Memberikan ruang diskusi ringan bagi komunitas IT Agenty tanpa dependency
eksternal: tidak ada CDN, framework, database, atau paket pip. Seluruh logika
menggunakan Python 3 standar (`http.server`, `json`, `threading`, `tempfile`),
serta HTML/CSS/JS polos. Cocok untuk batas 512 MB RAM / 1 CPU container Infinity.

## Menjalankan

```bash
python3 site/community/server.py
```

Server bind di **127.0.0.1:8781** dan membuat `data/posts.json` otomatis. Buka
<http://127.0.0.1:8781/>.

Overrid port untuk keperluan uji (nama variabel sengaja bukan `PORT`, sesuai
aturan `AGENTS.md`):

```bash
AGENTY_COMMUNITY_PORT=8782 python3 site/community/server.py
# atau: python3 site/community/server.py 8782
```

Hentikan dengan `Ctrl+C`. Pendaftaran ke supervisor / `system/services.json`
dilakukan oleh agen utama; tidak perlu mengubah file tersebut di sini.

## Endpoint API

| Metode | Path | Keterangan |
|---|---|---|
| `GET` | `/health` | Status: `status`, `system`, `version`, `posts`, `license` |
| `GET` | `/` | Antarmuka portal (`index.html`) |
| `GET` | `/app.js`, `/style.css` | Aset statis |
| `GET` | `/README.md` | Dokumentasi ini (text/plain) |
| `GET` | `/api/posts` | Daftar posting: `{"posts": [...]}` |
| `POST` | `/api/posts` | Buat posting `{title, body, author}` → `201` + objek posting |
| `POST` | `/api/posts/<id>/reply` | Balas posting `{author, body}` → `201` + objek balasan |
| `OPTIONS` | semua rute | Preflight → `204` |

Contoh:

```bash
curl http://127.0.0.1:8781/health
curl http://127.0.0.1:8781/api/posts
curl -X POST http://127.0.0.1:8781/api/posts \
  -H 'Content-Type: application/json' \
  -d '{"title":"Halo","author":"Tomi","body":"Posting pertama."}'
```

Contoh balasan (pakai `id` dari posting di atas):

```bash
curl -X POST http://127.0.0.1:8781/api/posts/<id>/reply \
  -H 'Content-Type: application/json' \
  -d '{"author":"Agenty","body":"Terima kasih!"}'
```

## Batasan & keamanan

- Body request maksimal **64 KB**; lebih besar ditolak `413`.
- Panjang field: judul 1–120, nama 1–60, isi posting 1–5000, balasan 1–2000 karakter.
- Maksimal 500 posting (terbaru dipertahankan) dan 200 balasan per posting.
- Penyimpanan `data/posts.json` memakai **atomic write** (`tempfile` + `os.replace`)
  dan `threading.Lock`, aman untuk permintaan konkuren.
- Hanya rute statis yang masuk daftar putih — tidak ada directory traversal.
- Header: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`,
  `Referrer-Policy: no-referrer`, `Cache-Control: no-store`.
- Frontend melakukan `escapeHtml` pada semua data sebelum disisipkan ke DOM
  (pencegahan XSS). Tidak ada autentikasi; jangan ekspos ke internet publik.

## Struktur

```
site/community/
├── server.py     # server HTTP stdlib + API + penyimpanan atomik
├── index.html    # antarmuka portal
├── style.css     # gaya netral merah-putih, responsif
├── app.js        # fetch API, render, escape HTML
├── README.md     # dokumentasi ini
└── data/
    └── posts.json  # data persisten (dibuat otomatis)
```

## Lisensi

SPDX-License-Identifier: **Tom05ivier-commits-1.0** — Copyright (c) 2026 Tomi vier.
Lihat `LICENSE` di root workspace. Kode pihak ketiga yang di-clone tetap tunduk
pada lisensi aslinya dan tidak terpengaruh oleh lisensi ini.
