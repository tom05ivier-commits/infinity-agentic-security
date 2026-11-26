<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Penonaktifan hy4 flash free dan alias hy4

Tanggal: 22 November 2026. Berlaku untuk workspace `/root/workspace`.

Catatan lanjutan: setelah penonaktifan, model default sempat diubah ke
`opencode/tidepool-alpha-free`, lalu pada hari yang sama diganti ke
`opencode/glm-5.3-flash` (alias proxied dengan ctl 100M) sesuai pilihan pengguna.
Cadangan tidepool ada di `/tmp/opencode/glm-default-20261122/opencode.json`.

## Yang dinonaktifkan

1. **Model default OpenCode** — dari `opencode/hy4-flash-free` menjadi
   `opencode/tidepool-alpha-free` (model yang sama dipakai profil `owner-ceo.md`).
2. **Agen `hy4.md`** — dihapus dari `AGENTS` di `system/hy4_manager.py` dan dari
   direktori agen OpenCode/Copilot setelah sinkronisasi.
3. **Alias CLI `./hy4`** — diganti nama menjadi `hy4.nonaktif-20261122` dan
   tidak lagi disalin ke cermin publik.

## Yang sengaja dipertahankan

- Entri `hy4-flash-free` di `config/tom05-models.json`,
  `config/tom05-provider-models.json`, dan provider tom05. Entri ini adalah
  upstream dari alias `tom05/tom05-flash-free`; menghapusnya akan merusak
  parity dan katalog pihak ketiga. Ini **bukan** model default lagi.
- `hy4-auth-check.sh`, `manage_hy4.sh`, dan modul verifikasi lain: tetap
  berfungsi sebagai alat perawatan, bukan sebagai model aktif.
- Cermin Copilot memakai `opencode-hy4/hy4-flash-free` sesuai aturan
  `copilot_sync.py` sampai diubah terpisah.

## Pemulihan

Cadangan ada di `/tmp/opencode/hy4-deaktivasi-20261122/`:

```bash
cp /tmp/opencode/hy4-deaktivasi-20261122/opencode.json /root/.config/opencode/opencode.json
cp /tmp/opencode/hy4-deaktivasi-20261122/hy4_manager.py /root/workspace/system/hy4_manager.py
mv /root/workspace/hy4.nonaktif-20261122 /root/workspace/hy4
cd /root/workspace && ./manage_hy4.sh agents && ./manage_hy4.sh copilot-sync
```

Cadangan bersifat sementara; salin ke lokasi permanen bila diperlukan.

## Diaktifkan kembali (26 November 2026)

Atas permintaan pengguna, penonaktifan di atas dibatalkan pada 26 November 2026:

1. **Alias CLI `./hy4`** — dipulihkan dari `hy4.nonaktif-20261122` menjadi `hy4`
   (skrip kompatibilitas yang memanggil `./tom05`) dan `/usr/local/bin/hy4`
   dipasang. `tom05` tetap CLI kanonik. Kembali ke keadaan dinonaktifkan:
   `mv hy4 hy4.nonaktif-20261122` + `rm /usr/local/bin/hy4`.
2. **Agen `hy4.md`** — ditambahkan kembali ke `AGENTS` di
   `system/hy4_manager.py` (model `opencode/hy4-flash-free`); dihasilkan ulang
   dengan `./manage_hy4.sh agents` + `./manage_hy4.sh copilot-sync`.
3. **Model default OpenCode** — `model` di `opencode.json`
   (`/root/workspace` + `/root/.config/opencode`) diatur ke
   `opencode/hy4-flash-free`. CLI `tom05`/`hy4` sendiri memakai alias
   `tom05/tom05-flash-free` (provider tom05 menerjemahkan ke upstream
   `opencode/hy4-flash-free`, model `hy4-flash-free`).
   Cadangan keadaan sebelumnya: `opencode.json.bak-hy4-20261126`
   (masing-masing direktori) dan `/tmp/opencode/hy4-deaktivasi-20261122/opencode.json`.
   Tidak ada model baru di provider; `hy4-flash-free` tetap upstream alias,
   bukan model terlatih.

Yang tetap berlaku: `hy4-auth-check.sh`, `manage_hy4.sh`, verifikasi hy4;
cermin publik GitHub tidak otomatis berubah sampai `./update_all.sh` dijalankan.
