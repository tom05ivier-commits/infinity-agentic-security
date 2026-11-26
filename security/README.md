<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Infinity Security Suite

Platform **cyber range** untuk melindungi hardware sekaligus menguji pertahanan
dengan simulasi serangan malware. Dibuat oleh **Tomi vier** di bawah
lisensi **Tom05ivier-commits-1.0**.

## Ruang lingkup & batas aman

- **Pertahanan (blue team):** inventaris hardware, firewall host, antivirus,
  dan SOC agent — berjalan nyata (firewall default `dry_run`).
- **Serangan (red team):** **simulasi jinak** untuk latihan. Hanya menarget
  `localhost` atau direktori `security/lab`. Mensyaratkan token otorisasi.
- **Tidak dibuat:** ransomware, wiper, keylogger, worm, atau eksploit nyata.
  "Malware" di sini adalah berkas uji EICAR dan pola teks mencurigakan.

## Arsitektur

```
security/
├── common/            # konfigurasi, model, logging JSON, otorisasi
├── blue/              # pertahanan
│   ├── hardware_agent.py    # inventaris NIC/CPU dari /sys & /proc
│   ├── firewall_agent.py    # aturan iptables (dry_run default)
│   ├── antivirus_agent.py   # EICAR + hash SHA-256 + heuristik
│   ├── soc_agent.py         # korelasi alert, skor risiko, laporan JSON
│   ├── policy.py            # policy engine firewall userspace
│   ├── monitor.py           # antivirus real-time + karantina otomatis
│   └── defense_agent.py     # fasade perlindungan + respons insiden
├── red/               # ofensif tersah
│   ├── attack_agent.py      # orkestrator dengan gating token
│   ├── malware.py           # simulator malware jinak
│   └── modules/             # recon, scanner, simulator
├── lab/               # target simulasi (payload jinak, konfigurasi uji)
├── blue/signatures/   # basis hash + aturan YARA contoh
├── security_cli.py    # CLI terpadu
└── tests/             # pengujian unit
```

## Cara pakai

Jalankan dari direktori `security/`:

```bash
cd security

# 1. Lindungi hardware + buat baseline
python3 security_cli.py protect

# 2. Inisialisasi data lab & hash uji
python3 security_cli.py lab setup 2>/dev/null || python3 security_cli.py lab

# 3. Terbitkan token otorisasi (5 menit)
export AGENTY_RED_AUTH_TOKEN="$(python3 security_cli.py red issue-token --minutes 5)"

# 4. Latihan penuh: lindungi → serang lab → respons insiden
python3 security_cli.py drill

# Atau per langkah:
python3 security_cli.py red recon
python3 security_cli.py red scan --target 127.0.0.1 --ports 22,80,443,8080
python3 security_cli.py red attack
python3 security_cli.py red severe --intensity severe
python3 security_cli.py red repeat --times 3 --intensity moderate
python3 security_cli.py campaign --times 3 --intensity moderate
python3 security_cli.py av scan lab
python3 security_cli.py firewall debug
python3 security_cli.py firewall block-ip 203.0.113.66

# Uji unit
python3 -m unittest discover -s tests -v
```

## Alur latihan (`drill`)

1. **protect** — inventaris hardware, aturan firewall dasar, pemindaian AV baseline.
2. **attack** — token otorisasi → recon → port scan localhost → penempatan
   artefak EICAR & pola mencurigakan di `lab/` → pemeriksaan konfigurasi lemah.
3. **respond** — AV memindai ulang lab, mengkarantina berkas terinfeksi,
   firewall memblokir IP uji (RFC 5737), SOC membuat `incident_report.json`.

### Perlindungan real-time

`monitor` menjalankan antivirus continuous-polling pada direktori lab dan
mengarantina berkas terinfeksi otomatis. `live-drill` menyalakan monitor,
menjalankan serangan serius, lalu membuktikan deteksi terjadi **saat serangan
berlangsung**:

```bash
python3 security_cli.py monitor --seconds 5 --interval 0.5
python3 security_cli.py live-drill
```

### Serangan serius ke hardware

`red severe --intensity {light,moderate,severe}` menjalankan `MalwareSimulator`
ditambah `hardware_stress`: beban CPU terukur, alokasi memori sementara,
penulisan berkas di lab, dan probe soket localhost. Semua parameter dibatasi
(durasi ≤ 2 detik, memori ≤ 16 MB, ≤ 20 berkas, ≤ 30 soket) dan tidak menyentuh
jaringan eksternal. `full_drill()` memakai profil `moderate`.

`red repeat --times 3` mengulang serangan tiga kali dan melakukan debug di
antara siklus: status capability, policy firewall, dan perubahan integritas
dicatat per putaran. `campaign` menggabungkan semuanya — proteksi, debug awal,
3 siklus serangan, debug akhir, respons SOC, dan laporan
`reports/campaign.json`.

`modules/telemetry.py` menangkap metrik nyata (`/proc/stat`, `/proc/meminfo`,
disk usage) sebelum dan sesudah serangan, lalu menghitung delta CPU, memori,
dan disk. Delta ini disimpan di `metadata.telemetry` pada hasil serangan
sebagai bukti terukur dampak ke hardware.

> Catatan lingkungan: pada container Android ini `/proc/stat` bernilai nol
> statis, sehingga `cpu_active_delta` dapat bernilai 0 meski beban CPU tetap
> berjalan. Memori dan disk tetap terukur (misalnya `memory_available_delta_kb`
> negatif dan `disk_used_delta` positif setelah serangan `severe`).

Laporan tersimpan di `security/reports/`, audit log di `security/logs/`.

## Firewall tanpa CAP_NET_ADMIN

Container ini tidak memiliki kemampuan kernel untuk memasang aturan iptables.
`FirewallAgent` tetap menghasilkan perintah yang benar (dry run), sementara
`FirewallPolicy` menyimpan dan mengevaluasi kebijakan secara persisten di
`security/firewall/rules.json`. Agen pertahanan menerapkan baseline
(`deny tcp/23`, `allow tcp/22`) dan memblokir IP uji saat respons insiden.

**Enforcement userspace nyata:** aturan policy juga dipatuhi oleh agen ofensif —
`AttackAgent.port_scan()` melewati port yang ditolak dan mencatatnya di
`metadata.skipped_ports`. Dengan demikian perlindungan tetap efektif walau
`CapBnd = 0`, meski ini bukan pengganti packet filtering kernel pada host.

Periksa dengan:

```bash
python3 security_cli.py firewall capability
python3 security_cli.py firewall debug
python3 security_cli.py firewall policy
python3 security_cli.py verify
```

### CAP_NET_ADMIN

CAP_NET_ADMIN **tidak dapat dibuat dari dalam proses**. Nilainya harus diberikan
oleh host/container runtime saat proses dimulai. Di lingkungan ini `CapBnd = 0`
(bounding set kosong), `capsh`/`setcap` tidak tersedia, dan `unshare --user
--map-root-user --net` tetap menghasilkan `CapEff = 0` — jadi mustahil
menambahkannya dari dalam.

Cara yang benar di host yang mendukung:

```bash
# Docker / container runtime
docker run --cap-add=NET_ADMIN ...

# Host Linux dengan file capability
sudo setcap cap_net_admin+ep "$(command -v iptables)"

# Jalankan pada sistem yang sudah memiliki capability
bash security/firewall/enable_kernel.sh
```

Jika capability dan backend tersedia, `FirewallAgent(dry_run=False)` akan
benar-benar memasang aturan iptables. Jika tidak, sistem otomatis tetap memakai
policy engine userspace dan melaporkan `userspace-policy`.

`verify` memeriksa 7 aspek objective (lisensi, surat izin, hardware, antivirus,
firewall, debugging, serangan serius) dan menulis `reports/verification.json`.

## Efikasi pertahanan

Setelah `campaign --times 3`, jalankan `security_cli.py efficacy`. Modul
`efficacy.py` menilai setiap siklus (deteksi, tingkat keparahan, telemetri,
integritas, policy, mode) dan menulis `reports/efficacy.json` dengan status
`EFEKTIF` bila semua serangan terdeteksi dan skor rata-rata ≥ 80.

## Batasan etis & otorisasi

Sistem ini **tidak** menyediakan:

- pencurian/ekstraksi data: `dlp` hanya **mendeteksi paparan**, tidak mengambil
  atau mengirim data ke mana pun;
- izin tanpa batas: semua token otorisasi memiliki scope, masa berlaku
  maksimal 300 detik, dan dapat dicabut.

Perintah `security_cli.py authorization` menampilkan kebijakan ini. Menambahkan
kemampuan pencurian data atau izin permanen akan bertentangan dengan surat izin
yang ditandatangani dan tidak akan dilakukan.

## Pencegahan kebocoran data (DLP)

```bash
python3 security_cli.py dlp lab
python3 security_cli.py dlp lab --protect   # karantina berkas sensitif
```

`blue/dlp.py` memindai pola generik (kunci privat, kredensial, email, telepon)
dan mengembalikan **jumlah + label** saja — nilai data sensitif tidak pernah
diekraksi atau disimpan. Hasil DLP juga masuk ke laporan `protect`.

## Pemantauan integritas

`IntegrityMonitor` menyimpan baseline SHA-256 berkas kritis di
`security/reports/integrity_baseline.json` dan membandingkannya setiap kali
`protect` / `respond` dijalankan. Perubahan, penambahan, atau penghapusan
berkas dilaporkan di `metadata.integrity`.

```bash
python3 security_cli.py integrity          # cek
python3 security_cli.py integrity --reset  # perbarui baseline
```

## Otorisasi

Token adalah JSON di `AGENTY_RED_AUTH_TOKEN` berisi `token_id`, `issued_by`,
`scope.allowed_targets` (hanya `lab`, `127.0.0.1`, `localhost`, `::1`),
`issued_at`, dan `expires_at`. Tanpa token, semua metode `AttackAgent`
menaikkan `AuthorizationError`.

## Debugging

Gunakan `python3 security_cli.py debug` untuk memeriksa kesehatan sistem.
Perintah ini melaporkan writable directory, ketersediaan backend firewall,
validitas token otorisasi, dan jumlah antarmuka hardware yang terdeteksi.

Masalah yang sudah ditemukan dan diperbaiki saat pengembangan:

| Masalah | Perbaikan |
|---------|-----------|
| `ImportError: attempted relative import beyond top-level` | Semua impor diseragamkan ke paket `security.*`; CLI dan test menyisipkan root workspace ke `sys.path`. |
| `PermissionError: /sys/class/net` | `HardwareAgent` jatuh ke `/proc/net/dev`, lalu ke alamat `socket` lokal. |
| `AuthorizationError: target 127.0.0.1 di luar scope` | `full_drill()` memilih target yang memang diizinkan token; token `drill` mencakup `lab` dan `127.0.0.1`. |
| Firewall tidak mengubah sistem | Disengaja: `FirewallAgent` default `dry_run=True`. Gunakan `dry_run=False` hanya dengan hak root. |

Status `DEGRADED` pada lingkungan ini wajar: `iptables` tidak terpasang dan
token otorisasi tidak diset secara default. Keduanya tidak menghalangi latihan.

## Lisensi

Seluruh berkas menggunakan header `SPDX-License-Identifier: Tom05ivier-commits-1.0`.
Berkas data X11 (`lab/`) dan konfigurasi sistem tetap mempertahankan header aslinya.
