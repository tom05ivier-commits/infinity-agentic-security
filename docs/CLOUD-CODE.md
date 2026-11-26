<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Cloud Code di Supervisor IT Agenty

Layanan `cloud-code` (port 8785, health `/health`) memantau alat Cloud Code
yang terpasang di workspace. Semua endpoint bersifat read-only, loopback, dan
tidak memakai kredensial.

## Komponen

| Alat | Peran | Wajib |
|---|---|---|
| `claude` | Claude Code CLI | ya |
| `gcloud` | Google Cloud CLI (dependensi Cloud Code) | ya |
| `kubectl` | Kubernetes CLI (dependensi Cloud Code) | ya |
| `skaffold` | Build/deploy lokal (dependensi Cloud Code) | ya |
| `minikube` | Cluster lokal (dependensi Cloud Code) | ya |
| `code` | VS Code, untuk ekstensi IDE Cloud Code | ya |

Keenam alat dinyatakan wajib. Ekstensi IDE Cloud Code (VS Code/JetBrains)
tidak dapat dipasang pada lingkungan headless; yang dipantau supervisor
adalah biner `code` di PATH. Bila biner itu belum tersedia, status menjadi
`GAGAL` dengan `wajib_hilang` memuat `code`, walaupun lima alat lainnya ada.

## Pemasangan

```bash
bash scripts/cloud_code_install.sh
```

Skrip ini memperbaiki symlink `gcloud` yang rusak dengan wrapper ke
`/root/google-cloud-sdk/bin/gcloud`, memasang biner resmi `skaffold` dan
`minikube` untuk `aarch64` dari bucket Google, serta biner `code` (VS Code
resmi, MIT) dengan wrapper headless `--no-sandbox` bila belum ada. Tidak ada
`gcloud auth login`, tidak ada akses project/billing, dan tidak ada kredensial
yang dibaca atau ditulis.

## Endpoint

- `GET /health` — liveness.
- `GET /status` — status semua alat plus laporan pemasangan.
- `GET /tools` — daftar alat dan versi terdeteksi.
- `GET /capabilities` — kemampuan layanan (tanpa mutasi).

Laporan lokal: `system/reports/cloud_code.json` dan
`system/reports/cloud_code_install.json`.

## Supervisor

Layanan terdaftar lewat:

```bash
./run_system.sh service-add --name cloud-code --kind http \
  --port 8785 --health /health --cmd python3 system/cloud_code_service.py
```

Setiap perubahan registry wajib diikuti `python3 chip/server_chip_gen.py`
agar `chip/rtl/srv_cloud_code.v` tetap ada. Komponen `cloud-code` juga
terdaftar di `system/infinity_connectivity.py` agar status infinity tetap
`TERHUBUNG`.
