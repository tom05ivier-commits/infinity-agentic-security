<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Container hardened untuk tom05

`Dockerfile.tom05` + `docker-compose.tom05.yml` adalah image purpose-built untuk
**Tom05 flash Free**. Berbeda dengan `Dockerfile` utama yang membawa seluruh
workspace dan `CAP_NET_ADMIN`, image ini sengaja minimal dan tidak memerlukan
capability kernel apa pun.

## Alasan desain

| Aspek | Kontainer utama | Kontainer tom05 |
|---|---|---|
| Sumber image | seluruh workspace (termasuk klon besar) | hanya artefak tom05 |
| Tahapan build | satu | tiga (`builder` → `verify` → `runtime`) |
| User | root (untuk iptables) | `10001:10001` non-root |
| Root filesystem | writable | `read_only: true` |
| Capability | `NET_ADMIN` | `cap_drop: ALL` |
| Privileges | default | `no-new-privileges:true` |
| Jaringan | `network_mode: host` | bridge, publish loopback saja |
| Healthcheck | dashboard 8765 | provider tom05 `/health` |
| Verifikasi build | tidak ada | `chip_cli.py soc` saat build |

## Menjalankan

```bash
# Verifikasi statis tanpa daemon (aman di lingkungan ini):
bash scripts/tom05_container_verify.sh
bash scripts/tom05_container_verify.sh --json

# Build & jalankan (membutuhkan Docker Engine pada host):
docker compose -f docker-compose.tom05.yml up -d --build

# Perintah di dalam kontainer:
docker compose -f docker-compose.tom05.yml exec tom05 verify
docker compose -f docker-compose.tom05.yml exec tom05 soc
docker compose -f docker-compose.tom05.yml exec tom05 list-models
docker compose -f docker-compose.tom05.yml exec tom05 display
```

Provider mendengar di `127.0.0.1:${AGENTY_TOM05_PORT:-8772}/v1` pada host.
Variabel `PORT` polos **tidak dipakai**; gunakan `AGENTY_TOM05_PORT`.
Untuk menjangkau bridge Copilot di host, container memakai
`host.docker.internal` lewat `extra_hosts: host-gateway`.

## Profil tampilan

Profil tampilan dideklarasikan di `config/tom05-models.json` pada
`capabilities.display` dan dibaca lewat `tom05 --display` (JSON).

| Kunci | Nilai |
|---|---|
| Nama tampilan | `Tom05 Landscape Display` |
| Orientasi / output | lanskap (`landscape`) |
| Akselerasi GPU | Panfrost, Mali (utama: Panfrost) |
| Mode | `deklarasi-manual` |

Variabel container terkait: `TOM05_DISPLAY_NAME`, `TOM05_DISPLAY_ORIENTATION`,
`TOM05_GPU_BACKENDS`, dan `TOM05_GPU_ACCEL` (lihat `docker-compose.tom05.yml`).
Nilai `bridge_exposed: false` berarti GPU ponsel **tidak** diekspos lewat
bridge — backend di atas hanya profil tampilan, bukan klaim akses GPU nyata.
Pengukuran WebGPU tetap dilakukan manual di perangkat lewat
`site/hardware/gpu.html`, lalu dibaca dengan `tom05 --gpu-result`.

Pemeriksaan profil ini juga menjadi bagian dari
`bash scripts/tom05_container_verify.sh`.

## Jaringan bersama & manager

Container dasar (`infinity` pada compose produksi, `infinity-dev` pada compose
dev) berperan sebagai **manager container**. Container tom05 bergabung ke
jaringan bersama `agenty-net` (alias `tom05`, sedangkan manager memakai alias
`infinity` dan `manager`). Nama jaringan dapat dioverride lewat
`AGENTY_NETWORK`.

Upstream tom05 diarahkan ke manager:

```
TOM05_UPSTREAM=http://infinity:8766/v1/chat/completions
TOM05_MANAGER_HOST=infinity
```

Pada compose produksi, manager berjalan dengan `network_mode: host` agar
iptables dapat memengaruhi antarmuka host. Karena mode host tidak dapat
bergabung ke jaringan bridge, tom05 memakai `extra_hosts`
`infinity:host-gateway` sebagai fallback; dengan demikian `infinity:8766`
tetap terjangkau tanpa mengubah hardening tom05 (non-root, `cap_drop: ALL`,
rootfs hanya-baca, publish loopback saja).

Peran manager juga tercatat di `system/services.json` melalui layanan
`tom05-provider` (`container`, `container_network`, `manager`,
`manager_endpoint`, `managed_by: supervisor`). Supervisor di container dasar
memantau health layanan ini, dan statusnya ditampilkan pada dashboard.

## Verifikasi build-time

Stage `verify` mengulas katalog tom05 dan menjalankan
`python3 chip/chip_cli.py soc` (1.024 vektor). Bila verifikasi gagal, build
dihentikan — image tidak pernah diterbitkan dengan SoC yang rusak.

## Lingkungan ini

Docker CLI dan plugin Compose tersedia, tetapi **Docker daemon tidak berjalan**
di workspace Android ini. Karena itu yang dijalankan di sini adalah verifikasi
statik + `docker compose config` (tidak memerlukan daemon). Build nyata
dilakukan di host yang memiliki Docker Engine. Lihat `DOCKER.md`.

## Lisensi

`Tom05ivier-commits-1.0` — Copyright (c) 2026 Tomi vier.
