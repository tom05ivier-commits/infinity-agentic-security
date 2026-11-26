<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Otomatisasi Izin Tertulis

Otomatisasi ini **tidak menciptakan otoritas baru**. Ia memakai
`surat-persetujuan-otomatis.md` (meta-izin bertanda tangan `(__signature__)`,
berlaku 20 November 2026 s.d. 31 Desember 2027) melalui
`security.auto_approval.AutoApproval`. Tanda tangan pemilik manual, izin
tanpa batas, dan kategori dilarang tetap tidak tersedia.

## 1. Generator surat izin rutin

```bash
python3 security/permission_cli.py categories
python3 security/permission_cli.py issue --task verify --ttl 120 --reason "verifikasi rutin"
python3 security/permission_cli.py list --limit 10
```

Perilaku:

- Hanya kategori dalam `ALLOWED` yang diterbitkan: `server-add`, `verify`,
  `integrity`, `dlp`, `campaign`, `debug`, `efficacy`, `finalize`, `delivery`,
  `config`, `host`, `github`, `clone`.
- `unlimited-auth`, `external-network-action`, `data-theft`, dan
  `third-party-license-removal` selalu ditolak.
- TTL maksimal **300 detik**. Permintaan lebih lama ditolak dan dicatat.
- Surat ringkas ditulis ke `security/reports/auto_permission_letters/<id>.md`,
  indeks ke `security/reports/auto_permission_letters.jsonl`, dan jejak asli
  tetap di `security/reports/auto_approvals.jsonl`.
- Penanda `(__signature__)` pada surat adalah **penanda dari meta-izin**, bukan
  tanda tangan manual baru. Surat menyatakan secara eksplisit bahwa izin
  ber-scope, berjangka, dapat dicabut, dan bukan izin tanpa batas.

## 2. Pemeriksa kedaluwarsa

```bash
python3 security/permission_cli.py check
python3 security/permission_watch.py --once
make infinity-connectivity
```

Laporan read-only ditulis ke `security/reports/permission_expiry.json`.
Pemeriksa:

- membaca surat aktif dan draf (`surat-*.md`, `DRAF-*.md`);
- menandai status `AKTIF`, `SEGERA_KEDALUWARSA` (≤30 hari),
  `KEDALUWARSA`, `DRAF`, atau `TANPA_TANGGAL`;
- memeriksa apakah surat aktif memiliki tanda tangan;
- tidak pernah menerbitkan, memperpanjang, atau menandatangani izin.

## 3. Penjadwalan

Dua lapisan penjadwalan aktif:

1. Layanan supervisor `permission-watch` (proses) memeriksa tiap 3600 detik.
2. Automation OpenCode `Cek kedaluwarsa izin tertulis` menjalankan
   `python3 security/permission_watch.py --once` tiap pukul 09:00
   `Asia/Jakarta` sampai 31 Desember 2027.

Keduanya read-only dan auditabel. Untuk menghentikan penjadwal OpenCode,
hapus automation dengan id `aut_217abe62e001VNoMY4SM8yPZ8P`.

## Batas tegas

- Tidak ada tanda tangan otomatis atas nama pemilik untuk dokumen baru.
- Tidak ada izin tanpa batas atau token permanen.
- Tidak ada aksi jaringan eksternal otomatis dari modul ini.
- Lisensi pihak ketiga dan surat berstatus DRAF tidak diubah.

## Pengujian

```bash
python3 -m unittest security.tests.test_permission_automation -v
python3 chip/chip_cli.py score
make test
```
