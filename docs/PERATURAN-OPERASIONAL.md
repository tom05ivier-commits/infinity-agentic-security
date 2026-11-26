<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# PERATURAN OPERASIONAL IT AGENTY — INFINITY

**Status:** Dokumen tata kelola, konsolidasi aturan yang sudah berlaku.  
**Perihal:** Ringkasan aturan operasional workspace untuk agent dan operator.  
**Catatan:** Dokumen ini **bukan sumber otoritas baru**. Ia tidak menambah izin,
tidak mengubah lisensi, tidak menetapkan tanda tangan, dan tidak mencabut
pembatasan yang sudah ada. Bila bertentangan dengan surat izin tertulis atau
`AGENTS.md`, maka surat izin tertulis dan `AGENTS.md` yang menang.

---

## 1. Identitas dan lisensi

- Sistem: **IT Agenty — Infinity Computer System**.
- Pemilik: **Tomi vier**, Owner / CEO.
- Lisensi aktif: **Tom05ivier-commits-1.0** (`LICENSE` versi 1.0).
- Draf amandemen lisensi, surat larangan klon, dan kuasa tanda tangan **belum
  berlaku** sebelum pemilik mengisi dan menandatangani manual.
- Kode pihak ketiga (OpenCode, Chromium, dan sejenisnya) tetap tunduk pada
  lisensi aslinya. Lisensi IT Agenty tidak menghapus lisensi, paywall, atau
  mekanisme pembayaran pihak ketiga.

## 2. Komputer dan layanan

- `./run_always.sh` wajib aktif; supervisor menjaga server dan proteksi tetap
  berjalan. Heartbeat ada di `system/reports/heartbeat.json`.
- Setiap komponen baru yang membutuhkan server wajib didaftarkan di
  `system/services.json` lewat `./run_system.sh service-add`. Supervisor
  melakukan hot-reload registry setiap siklus. Server di luar registry dilarang.
- Layanan proyek memakai `AGENTY_PORT`, bukan variabel `PORT`.
- Firewall berjalan sebagai policy userspace (`CapBnd = 0`). Enforcement kernel
  hanya dipasang dari host melalui `security/firewall/install-net-admin.sh`.

## 3. Berkas dan privasi

- Setiap berkas baru wajib memuat header:
  `SPDX-License-Identifier: Tom05ivier-commits-1.0` dan
  `Copyright (c) 2026 Tomi vier`.
- Dilarang mencuri, mengekstraksi, atau mengirim data. Modul `dlp` hanya untuk
  deteksi dan karantina paparan data.
- Kredensial, token, dan kunci API tidak boleh masuk chat, log, issue, README,
  berkas proyek, atau repo publik. Pembangkit kunci lokal menyimpan nilai di
  `credentials/.env` dengan mode `0600` dan hanya mencatat sidik jari.
- Token otorisasi hy4 bersifat **per pemasangan**, bukan token bersama.
  Jalankan `./hy4-auth-check.sh` sebelum rilis; pemeriksa hanya mencetak status
  boolean dan tidak pernah menampilkan nilai token.
- Rilis publik wajib lolos `security/security_cli.py privacy release PATH`.
  Status `SIAP` hanya bila bersih, `.env` ber-mode `0600`, dan ter-ignore.

## 4. Izin dan otorisasi

- Semua izin bersifat **terbatas, ber-scope, berjangka, dan dapat dicabut**.
  Otorisasi tertulis berlaku sampai **31 Desember 2027** dan dapat dicabut
  sewaktu-waktu. Permintaan izin "tanpa batas" ditolak dan dicatat.
- Tanda tangan pemilik hanya sah bila diisi manual di berkas asli. Penanda
  yang diketik atau dikirim lewat chat bukan tanda tangan.
- Meta-izin otomatis (`surat-persetujuan-otomatis.md`) hanya mencakup delapan
  kategori rutin: `server-add`, `verify`, `integrity`, `dlp`, `campaign`,
  `debug`, `efficacy`, `finalize`. Setiap izin dicatat di
  `security/reports/auto_approvals.jsonl`.
- Kategori `data-theft`, `unlimited-auth`, `third-party-license-removal`, dan
  `external-network-action` **tetap ditolak** dan memerlukan izin tertulis baru.
- TTL izin otomatis maksimal **300 detik**. Perpanjangan melampaui batas kode
  ditolak.
- Konfigurasi otomatis hanya untuk kunci dalam Lampiran 1
  `surat-izin-konfigurasi-otomatis.md` (firewall port, `workflow.name`,
  `delivery.channel`, `system.interval`). Kunci `license.*`, `authorization.*`,
  `network.*`, `data.*`, dan `signature.*` ditolak. Setiap perubahan diaudit di
  `security/reports/auto_configs.jsonl`.
- Aksi ofensif hanya di laboratorium/localhost dengan `AGENTY_RED_AUTH_TOKEN`,
  maksimal 300 detik, dan `--authorize` eksplisit.

## 5. Mutu dan publikasi

- Sebelum rilis, semua scorecard wajib bernilai 100/100: chip, keamanan, tom05,
  perangkat, dan container. `update_all.py` membatalkan publikasi bila salah
  satu turun.
- `make test` memakai skor chip, skor keamanan, dan `apikey-guard` sebagai gate.
- Push GitHub hanya lewat `push_github.sh` sesuai `surat-izin-github.md`, dengan
  remote tanpa kredensial dan audit setiap `repo-push` di
  `security/reports/github_actions.jsonl`. Tidak ada autopay atau pembayaran
  otomatis untuk layanan pihak ketiga.
- Sumber kebenaran data bersama adalah `/root/workspace`. Cek dengan
  `make share-check`; salinan `publish/` adalah cermin tersanitasi.
- Status teknis yang sempurna tidak mengubah status lisensi yang masih
  menunggu tanda tangan pemilik. Cek ringkas dengan `python3 system/final_status.py`.

## 6. Sumber otoritas

Dokumen ini hanya merangkum. Untuk mengetahui aturan yang mengikat, rujuk
langsung ke sumbernya:

| Pokok | Sumber |
|---|---|
| Identitas, lisensi, dan aturan tetap | `AGENTS.md`, `LICENSE` |
| Izin tertulis dan pencabutan | `surat-izin-*.md`, `surat-persetujuan-*.md`, `surat-kuasa-tandatangan.md` |
| Meta-izin otomatis | `surat-persetujuan-otomatis.md`, `security/auto_approval.py` |
| Konfigurasi otomatis | `surat-izin-konfigurasi-otomatis.md`, `config/` |
| Register layanan | `system/services.json` |
| Privasi dan kerahasiaan | `PRIVACY.md`, `security/privacy.py` |
| Scorecard dan publikasi | `system/final_status.py`, `system/update_all.py`, `push_github.sh` |

Bila ada perbedaan, sumber di tabel di atas yang menang atas ringkasan ini.

## 7. Pemeriksaan ringkas

Semua perintah berikut tidak membaca atau menampilkan kredensial. Kecuali
`make score`, yang menulis ulang berkas laporan scorecard, perintah di bawah
bersifat pemeriksaan:

```bash
python3 system/final_status.py     # status teknis, koneksi, dan lisensi
make share-check                   # data bersama OpenCode ↔ OpenCode AI
./hy4-auth-check.sh                # status token per pemasangan (boolean)
python3 security/security_cli.py privacy release publish/infinity-agentic-security
make score                         # kelima scorecard (menulis laporan)
make connection-status             # koneksi server, provider, dan bridge
```

Hasil pemeriksaan tidak menggantikan tanda tangan pemilik.

## 8. Penegasan

Peraturan ini hanya merangkum kewajiban yang sudah berlaku. Ia tidak
menciptakan aksi baru, tidak mengubah katalog tool, tidak menggantikan aturan
permission di `opencode.json`, dan tidak memberi wewenang kepada agen untuk
menulis ulang surat izinnya sendiri. Perubahan substansi hanya berlaku setelah
pemilik mengisi dan menandatangani berkas resmi secara manual dan perubahannya
dicatat serta diverifikasi ulang.
