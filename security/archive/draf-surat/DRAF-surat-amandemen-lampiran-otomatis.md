<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# DRAF — AMANDEMEN LAMPIRAN 1 SURAT PERSETUJUAN OTOMATIS

> **DRAF — BELUM BERLAKU.** Ini bukan otoritas baru dan bukan pengganti
> `surat-persetujuan-otomatis.md`. Kolom di bawah wajib diisi manual oleh
> pemilik di berkas asli. Tanda tangan yang diketik/dikirim lewat chat tidak
> saya validasi.

**Nomor:** `IT-AGENTY/OTO/2026/11-22-AMANDEMEN-LAMPIRAN`  
**Perihal:** Usulan penambahan kategori `config` ke Lampiran 1 meta-izin otomatis

---

## 1. Pihak

| Keterangan | Isi |
|---|---|
| Pemberi meta-izin | Tomi vier |
| Jabatan | Owner / CEO — IT Agenty |
| Kontak | `[KONTAK — diisi manual bila diperlukan; kosongkan untuk salinan publik]` |
| Tanda tangan | `[Isi langsung di berkas asli oleh pemilik; jangan diketik atau dikirim lewat chat]` |
| Tanggal | `[TANGGAL — diisi manual]` |
| Penerima | `[NAMA PENERIMA / UNIT — diisi manual]` |
| Tanda tangan penerima | `[Isi langsung oleh penerima di berkas asli]` |
| Tanggal penerima | `[TANGGAL — diisi manual]` |

## 2. Latar belakang

Kode `security/auto_approval.py` saat ini memuat 13 kategori di `ALLOWED`,
termasuk `config`, `host`, `github`, `clone`, dan `delivery`. Namun Lampiran 1
`surat-persetujuan-otomatis.md` hanya mencantumkan 8 kategori:
`server-add`, `verify`, `integrity`, `dlp`, `campaign`, `debug`, `efficacy`,
`finalize`.

Validasi `AutoApproval` hanya memeriksa **keberadaan tanda tangan** surat,
bukan kecocokan daftar kategori. Akibatnya ada ketidaksesuaian antara kode dan
dokumen. Draf ini **mengusulkan** penambahan kategori `config` — bukan
mengizinkan kategori lain secara otomatis.

## 3. Usulan penambahan (bisa ditolak/diubah pemilik)

Baris yang diusulkan untuk Lampiran 1:

| Kategori | Cakupan |
|---|---|
| `config` | Konfigurasi otomatis **terbatas** sesuai `surat-izin-konfigurasi-otomatis.md` Lampiran 1 (kunci: `firewall.deny_port`, `firewall.allow_port`, `workflow.name`, `delivery.channel`, `system.interval`) |

Dengan syarat:
1. Hanya kunci di Lampiran 1 `surat-izin-konfigurasi-otomatis.md` yang diproses.
2. `firewall.deny_port`/`firewall.allow_port` hanya menerima port **1–65535**.
3. Setiap penerapan lewat `security/auto_config.py apply()` dan tercatat di
   `security/reports/auto_configs.jsonl` dengan `approval_id`, nilai lama/baru,
   dan tanda tangan digital.
4. TTL izin maksimal **300 detik**; bukan izin tanpa batas.
5. Firewall tetap **policy userspace** (`CapBnd=0`); kernel hanya dari host.
6. Kategori DENIED (`data-theft`, `unlimited-auth`,
   `third-party-license-removal`, `external-network-action`) tetap ditolak.

## 4. Yang tidak diusulkan

Draf ini **tidak** menambahkan `host`, `github`, `clone`, atau `delivery` ke
Lampiran 1. Kategori lain yang sudah ada di kode tetapi tidak tercantum di
surat tetap menjadi catatan tersendiri untuk pemilik — tidak saya izinkan
otomatis lewat draf ini.

## 5. Batas yang tidak dapat diubah

- Otorisasi, kuasa tanda tangan, lisensi, atau amandemen `LICENSE`.
- Ketentuan tanda tangan manual (penanda digital di chat bukan tanda tangan).
- Batas 01-01-1970, pencabutan, dan jejak audit.
- Kunci terlarang (`license.*`, `authorization.*`, `network.*`, `data.*`,
  `signature.*`) dan semua kategori DENIED.
- Pencabutan `capbnd` tidak dibatalkan.

## 6. Mekanisme berlaku

Berlaku setelah kolom di atas diisi manual, berkas asli disimpan di workspace,
perubahan dicatat di `security/reports/`, dan diverifikasi ulang dengan
`python3 system/final_status.py` serta `python3 system/shared_data.py`.
Tidak ada perubahan otomatis hanya dari perintah chat.

## 7. Penegasan akhir

Surat ini bukan sumber otoritas baru, bukan izin tanpa batas, dan tidak
menggantikan surat izin yang masih berlaku. Bila bertentangan dengan batas di
bagian 5, bagian 5 yang menang. Status lisensi aktif tetap
`MENUNGGU_TANDA_TANGAN` sampai pemilik menandatangani dan mengganti `LICENSE`
secara manual.

---

**Status:** DRAF — menunggu pengisian dan tanda tangan manual pemilik.
