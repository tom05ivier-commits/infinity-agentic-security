<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Docker — Infinity Security System

Setup kontainer dengan **CAP_NET_ADMIN** sehingga `FirewallAgent` dapat
memasang aturan iptables nyata, bukan sekadar policy engine userspace.

## Docker CLI di lingkungan ini

CLI sudah dipasang secara statis (arsitektur `aarch64`):

| Komponen | Versi | Path |
|---|---|---|
| Docker CLI | 29.10.0 | `/usr/local/bin/docker` |
| Compose plugin | v5.8.0 | `/usr/local/lib/docker/cli-plugins/docker-compose` |
| Buildx plugin | v0.39.0 | `/usr/local/lib/docker/cli-plugins/docker-buildx` |

Periksa dengan `make docker-check` atau `bash docker-cli-check.sh`.
Validasi `docker compose config` **tidak memerlukan daemon** dan sudah lulus
untuk kedua file compose.

> Docker **daemon tidak berjalan** di lingkungan ini (tidak ada
> `/var/run/docker.sock`, dan capability kernel tidak memungkinkan menjalankan
> `dockerd`). CLI siap dipakai begitu terhubung ke daemon host melalui
> `DOCKER_HOST` atau saat dijalankan di host yang memiliki Docker Engine.

## Prasyarat

- Docker Engine + Compose plugin terpasang di host.
- Akses root/sudo pada host untuk menjalankan kontainer privileged-ish.

## Menjalankan

```bash
cp .env.example .env        # opsional: ubah alamat bind
make build && make up       # atau: docker compose up -d --build
make logs
```

Dashboard: `http://127.0.0.1:8765/` (hanya di host, karena `network_mode: host`).

Situs statis mandiri (hub, Chip Merah Putih + simulator, IT Agenty) tersedia di
`http://127.0.0.1:8769/`. Mirror aplikasi PERURI memakai port `8770` karena
router React aslinya menggunakan path absolut — ia harus menjadi document root,
bukan berada di bawah `/mirror/`. Kedua layanan (`sites` dan `mirror`) terdaftar
di `system/services.json` lewat `service-add`, sehingga supervisor menjalankan
dan memantau keduanya otomatis. Port 8769/8770 dipetakan di mode dev dan
diekspos di Dockerfile. Semua halaman tanpa CDN dan tetap berfungsi offline.

Mode dev **tanpa** CAP_NET_ADMIN (bridge network, lebih aman untuk eksperimen):

```bash
make dev                    # docker compose -f docker-compose.dev.yml up -d --build
```

## Penyempurnaan setup

| Fitur | Keterangan |
|---|---|
| `healthcheck` | Memanggil `/api/health` tiap 30 detik; container unhealthy jika gagal |
| `init: true` | `tini` sebagai PID 1 agar sinyal & zombie process tertangani |
| `mem_limit` / `cpus` | 512 MB / 1 CPU (produksi), 256 MB / 0.5 CPU (dev) |
| `logging` | Rotasi log JSON, maksimal 10 MB × 3 file |
| `tmpfs` | `/tmp` dan `/var/tmp` ditulis ke memori |
| `locales` | `id_ID.UTF-8` benar-benar digenerate di image |
| Fallback iptables | `iptables-legacy` dipakai otomatis jika `iptables` absen |
| `.env.example` | Konfigurasi `BIND_HOST` / `BIND_PORT` |
| `Makefile` | `make help` untuk semua target |

## Perintah di dalam kontainer

```bash
docker compose exec infinity status
docker compose exec infinity verify
docker compose exec infinity protect --seconds 10
docker compose exec infinity drill
docker compose exec infinity live-drill
docker compose exec infinity shell
```

## Komponen yang membutuhkan CAP_NET_ADMIN

| Komponen | Cara memberikan | File |
|---|---|---|
| Docker daemon (`dockerd`) | dijalankan privileged oleh host | host |
| Kontainer produksi | `cap_add: NET_ADMIN` | `docker-compose.yml` |
| `FirewallAgent` / `iptables` | `AmbientCapabilities=CAP_NET_ADMIN` | `systemd/infinity-security.service` |
| Biner `iptables` | `setcap cap_net_admin+ep` | `capability-setup.sh` (strategi 3) |
| Proses interaktif | `capsh --addamb` / `setpriv` | `capability-setup.sh` (strategi 1–2) |

Jalankan `bash capability-setup.sh` untuk mencoba semua strategi dan melihat
mana yang tersedia. `security/firewall/capbnd.sh` menjelaskan dan menunjukkan
cara meluncurkan proses dengan **CapBnd** yang memuat `CAP_NET_ADMIN` (CapBnd
hanya bisa dikurangi, tidak ditambah, dari dalam proses).
`security/firewall/setup-capbnd.sh` adalah satu entry point untuk mengisi
CapBnd lewat systemd, Docker, dan file capability — jalankan dengan
`--dry-run` untuk simulasi. Untuk instalasi firewall kernel sekali jalan di
host yang sudah memiliki capability:

```bash
sudo bash security/firewall/install-net-admin.sh
```

Skrip itu memasang iptables, menerapkan baseline aturan, memverifikasi dengan
`iptables -S`, dan menulis `security/reports/firewall_kernel.json`. Mode dev
sengaja **tanpa** capability.

## CAP_NET_ADMIN

`docker-compose.yml` menyertakan:

```yaml
cap_add:
  - NET_ADMIN
network_mode: host
```

- `cap_add: NET_ADMIN` memberi capability yang sebelumnya tidak bisa diperoleh
  dari dalam container lama (`CapBnd = 0`).
- `network_mode: host` membuat aturan iptables berdampak pada antarmuka hardware
  host, bukan network namespace terisolasi.
- Jika capability/backend tetap tidak tersedia, entrypoint otomatis memakai
  `userspace-policy` dan mencatat alasannya — sistem tidak crash.

Verifikasi di dalam kontainer:

```bash
docker compose exec infinity python3 security/security_cli.py firewall capability
```

Output yang diharapkan: `cap_net_admin: true`, `kernel_enforcement: true`.

## Volume persisten

| Volume | Path | Isi |
|---|---|---|
| `reports` | `/workspace/security/reports` | laporan SOC & verifikasi |
| `logs` | `/workspace/security/logs` | audit log |
| `quarantine` | `/workspace/security/quarantine` | berkas terinfeksi |
| `firewall` | `/workspace/security/firewall` | `rules.json` |

## Catatan keamanan

- Kontainer berjalan sebagai root karena iptables memerlukan capability.
- Dashboard sengaja bind ke `127.0.0.1`, bukan `0.0.0.0`.
- Serangan malware tetap simulasi jinak (EICAR); tidak ada malware destruktif.
- Surat izin `surat-izin-keamanan.md` dan surat kuasa tetap menjadi dasar
  otorisasi penggunaan.

## Menjalankan tanpa Compose

```bash
docker build -t infinity-security:1.0 .
docker run --rm --cap-add=NET_ADMIN --network host \
  -p 127.0.0.1:8765:8765 \
  infinity-security:1.0 serve
```

> Catatan: dengan `--network host`, opsi `-p` diabaikan; port tetap mendengar
> di `127.0.0.1:8765` pada host sesuai `BIND_HOST`.
