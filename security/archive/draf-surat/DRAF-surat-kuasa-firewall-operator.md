<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# DRAF — SURAT KUASA TERBATAS: OPERATOR FIREWALL

> **DRAF — BELUM BERLAKU.** Ini bukan jabatan tata kelola, bukan pengangkatan
> wakil CEO, dan bukan tanda tangan baru. Kolom di bawah wajib diisi manual
> oleh pemilik di berkas asli. Tanda tangan yang diketik/dikirim lewat chat
> tidak saya validasi.

**Nomor:** `IT-AGENTY/KUASA/2026/11-22-OPERATOR-FIREWALL`  
**Perihal:** Pemberian kuasa **terbatas** untuk operasi verifikasi firewall

---

## 1. Pihak

| Keterangan | Isi |
|---|---|
| Pemberi Kuasa | Tomi vier |
| Jabatan | **Owner / CEO — IT Agenty** |
| Tanda tangan digital resmi | `(__signature__)` |
| Kontak | `[KONTAK — diisi manual bila diperlukan; kosongkan untuk salinan publik]` |
| Tanda tangan Pemberi Kuasa | `[Isi langsung di berkas asli oleh pemilik; jangan diketik atau dikirim lewat chat]` |
| Tanggal | `[TANGGAL — diisi manual]` |
| Penerima Kuasa | `[NAMA PENERIMA / UNIT OPERASIONAL — diisi manual]` |
| Tanda tangan Penerima | `[Isi langsung oleh penerima di berkas asli]` |
| Tanggal penerima | `[TANGGAL — diisi manual]` |

## 2. Penegasan jabatan

- Penerima Kuasa adalah **Operator Firewall** — peran **operasional teknis**.
- Ini **bukan** pengangkatan wakil CEO, bukan wakil pemilik, dan bukan
  pengalihan jabatan Owner/CEO yang melekat pada **Tomi vier**.
- Tanda tangan yang dipakai tetap `(__signature__)` milik pemilik.
  **Tidak ada tanda tangan baru** seperti `(__signature__)` yang dibuat oleh agen/model.

## 3. Wewenang yang diberikan (terbatas)

Operator Firewall diberi kuasa **khusus dan terbatas** untuk:

1. Menjalankan `python3 chip/chip_cli.py firewall` (drill + Icarus).
2. Menjalankan `python3 chip/firewall_drill.py` dengan variabel lingkungan
   `.env.firewall.example` (`AGENTY_FIREWALL_MODE`, `AGENTY_FIREWALL_REPORT`).
3. Membaca dan memverifikasi `security/firewall/rules.json` (policy userspace).
4. Menulis laporan hasil drill ke `chip/reports/` dan mencatat audit yang
   relevan di `security/reports/`.
5. Melaporkan hasil verifikasi kepada pemilik.

## 4. Yang TIDAK diberikan

- **Tidak** mengubah `LICENSE`, `AGENTS.md`, atau surat kuasa/izin lain.
- **Tidak** mengangkat atau menandatangani siapa pun sebagai wakil CEO.
- **Tidak** membuat atau memakai tanda tangan selain `(__signature__)`.
- **Tidak** mengaktifkan `capbnd` / `CAP_NET_ADMIN` / eskalasi kernel —
  tetap dicabut dan dihapus dari `HostActions.ALLOWED`.
- **Tidak** mengubah aturan firewall lintas batas Lampiran 1
  `surat-izin-konfigurasi-otomatis.md` (`firewall.deny_port`,
  `firewall.allow_port`, `workflow.name`, `delivery.channel`,
  `system.interval`). Kunci `license.*`, `authorization.*`, `network.*`,
  `data.*`, `signature.*` tetap ditolak.
- **Tidak** membuka akses publik, mengekstraksi data, atau melakukan aksi
  jaringan eksternal.

## 5. Batas berlaku

- Berlaku sejak **tanggal diisi manual oleh Pemberi Kuasa** hingga
  **30 November 2027** — lebih awal dari batas umum 01-01-1970.
- Dapat dicabut sewaktu-waktu secara tertulis oleh Pemberi Kuasa.
- Setiap tindakan tercatat di `security/reports/` yang relevan.
- Bukan izin tanpa batas; TTL teknis tetap **300 detik** untuk izin otomatis.

## 6. Kategori yang tetap ditolak

`data-theft`, `unlimited-auth`, `third-party-license-removal`,
`external-network-action`, dan semua kunci di luar Lampiran 1 teknis.

## 7. Mekanisme berlaku

Surat berlaku setelah kolom di atas diisi manual, berkas asli disimpan di
workspace, perubahan dicatat di `security/reports/`, dan diverifikasi ulang
dengan `python3 system/final_status.py` serta `python3 system/shared_data.py`.
**Tidak ada perubahan otomatis hanya dari perintah chat.**

## 8. Penegasan akhir

Surat ini **bukan sumber otoritas baru**, bukan jabatan tata kelola, dan tidak
menggantikan surat izin yang masih berlaku. Bila bertentangan dengan batas di
bagian 4–6, bagian tersebut yang menang. Status lisensi aktif tetap
`MENUNGGU_TANDA_TANGAN` sampai pemilik menandatangani dan mengganti `LICENSE`
secara manual.

---

**Status:** DRAF — menunggu pengisian dan tanda tangan manual pemilik.
