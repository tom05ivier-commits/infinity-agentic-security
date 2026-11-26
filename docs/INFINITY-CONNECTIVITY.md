<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.1 — lihat file LICENSE di root proyek.
-->

# Konektivitas Infinity — supervisor ↔ seluruh workspace

`system/infinity_connectivity.py` menyatukan dua hal yang sebelumnya tersebar:

1. **Supervisor menjaga semua layanan** yang terdaftar di `system/services.json`.
2. **Semua subsistem workspace saling terhubung** lewat satu sumber kebenaran
   (`/root/workspace`) dan relai chat (`config/chat_dispatch.json`).

Modul ini read-only. Ia hanya membaca registry, heartbeat, PID, dan laporan
JSON yang sudah ada. Tidak ada kredensial yang dibaca atau dicetak. Satu-satunya
tulisan adalah `system/reports/infinity_connectivity.json`.

## Model graph

- **Simpul** = komponen: 19 layanan registry (termasuk `sites`, `ai-chip`, dan
  `ai-chip-watch`) + subsistem (system, security, chip, agent, advanced,
  dataset, platform, container, device, knowledge, model, tom05-cli, dashboard,
  publish, mcp, workspace, supervisor).
- **Sisi** = koneksi lewat `registry` (supervisor → layanan), lewat sumber data
  bersama (setiap komponen ↔ `workspace`), atau lewat `links` yang didefinisikan
  explicit di manifest (misalnya `chat-dispatch` ↔ responder, `sites` ↔ `chip`).
- Status `TERHUBUNG` hanya bila: heartbeat sah, tidak ada `issues`, semua path
  komponen ada, semua layanan yang dihitung hidup, dan tidak ada simpul terputus.

Layanan `monitor` (`port-14713`) sengaja tidak dijalankan supervisor dan tidak
masuk penilaian — sesuai catatan `AGENTS.md`. Layanan dengan flag
`AGENTY_DISABLE_PUBLIC=1` / `AGENTY_DISABLE_TUNNEL=1` juga dikecualikan.

`public` bertipe `http` (bukan `process`) karena server memang menyediakan
health endpoint; HTTP 401 dianggap hidup karena berarti server aktif dan
meminta autentikasi.

## Cara pakai

```bash
python3 system/infinity_connectivity.py     # JSON + tulis laporan
make infinity-connectivity                 # sama, lewat Makefile
make infinity-connectivity-test            # 8 kasus uji
python3 system/cli.py infinity-connectivity
tom05 --infinity-connectivity
```

Laporan memuat `status`, `supervisor`, `layanan`, `komponen`, `graf`
(`simpul`/`sisi`/`terjangkau`/`terputus`), `masalah`, dan ringkasan `laporan`
dari chip/security/tom05/device/container score serta watcher.

## Batas jujur

- Ini peta konektivitas, bukan jaminan kapasitas atau SLA.
- Model `tom05/*` dan sejenisnya tetap alias/proxy pihak ketiga, bukan model
  terlatih baru tom05.
- Chip verifikasi server (`srv_<nama>.v`) adalah logika status, bukan silikon;
  `fabrication: NOT_READY`.
- Menambah layanan baru tetap wajib lewat `service-add` dan
  `python3 chip/server_chip_gen.py` agar RTL dan peta ini tetap sinkron.

Lisensi: **Tom05ivier-commits-1.0**, pemilik **Tomi vier**.
