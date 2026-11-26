<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Agen CLI Hardware — perangkat Android

## Apa yang bisa dan tidak bisa

Skill `android-device` yang tersedia di perangkat ini mengekspos:

| Aksi | Status |
|---|---|
| `device-info` (pabrikan, model, SDK, Android, baterai) | tersedia |
| `file-diagnostics` (storage bebas, workspace) | tersedia |
| `file-list`, `file-share`, `file-save`, `file-pick`, `file-capture` | tersedia |
| `notify`, `toast`, `open-url`, `clipboard-get` | tersedia |
| **GPU / Vulkan / NPU compute** | **TIDAK diekspos** |

Jadi agen hardware **tidak** menjalankan kernel GPU dan **tidak** mengukur GPU
ponsel secara langsung. Tidak ada klaim sertifikasi atau kemampuan yang tidak ada.

## Perintah

```bash
tom05 --hardware
```

Output JSON berisi status koneksi perangkat, informasi perangkat, baterai,
penyimpanan, serta `gpu_status: "TIDAK_TEREKSPOS"`. Laporan ini **tidak disimpan**
ke berkas karena data perangkat dapat bersifat pribadi, dan tidak membaca
kredensial.

## Alur pengukuran GPU bila diperlukan

```bash
tom05 --gpu          # bagikan site/hardware/gpu.html ke share sheet Android
tom05 --gpu-result   # baca hasil dari clipboard
```

1. `tom05 --gpu` membagikan halaman WebGPU mandiri (`site/hardware/gpu.html`)
   lewat share sheet perangkat. Halaman ini tidak mengirim data ke server.
2. Pengguna membukanya di browser ponsel, menekan **Jalankan pengukuran**, lalu
   **Salin hasil**.
3. `tom05 --gpu-result` membaca clipboard dan **hanya** menerima JSON dengan
   penanda `benchmark: "tom05-webgpu"`. Isi clipboard lain tidak ditampilkan.

Hasil itu diperlakukan sebagai data yang diberikan pengguna, bukan kapasitas yang
dijamin agen. Jika WebGPU tidak tersedia, halaman melaporkan
`status: GAGAL` dengan alasan, bukan angka rekaan.

## Integrasi

- Definisi kanonik: `system/hardware_agent.py`.
- Laporan: `system/hardware_report.py`.
- Agent OpenCode/Copilot: `hardware.md` (model `tom05/tom05-flash-free`).
- Sumber data: skill `android-device` → helper
  `/root/.config/opencode/skills/android-device/android_device.py`.
