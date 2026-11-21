<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE.
-->

# Infinity Agentic Security

Platform keamanan siber **agentik** untuk laboratorium dan produksi: antivirus,
DLP, integritas, firewall agent, SOC, red-team simulasi, medikasi insiden,
laporan efikasi, orkestrasi alur kerja, dan dashboard/API.

Dibangun oleh **Tomi vier** / IT Agenty di bawah lisensi **Tom05ivier-commits-1.0**.

**Repository resmi:** https://github.com/tom05ivier-commits/infinity-agentic-security

## Kemampuan

- Perlindungan hardware: antivirus real-time + karantina otomatis.
- Firewall agent dengan policy userspace + enforcement di agen.
- DLP: deteksi & karantina paparan data sensitif.
- Red-team laboratorium: malware jinak (EICAR), beban CPU/memori/disk terukur.
- Kampanye 3×, respons insiden, efikasi, dan laporan debugging.
- Agent Computer + Advanced Computer dengan knowledge base & memori.
- Copilot CLI terhubung ke model `hy4-flash-free` lewat bridge lokal.
- Supervisor dengan registry server dan hot-reload.
- Docker + Cloudflare Tunnel + Basic Auth untuk akses terkendali.

## Mulai

```bash
python3 security/security_cli.py verify
python3 security/security_cli.py campaign --times 3
python3 security/security_cli.py efficacy
python3 security/security_cli.py sempurnakan
./run_system.sh status
```

## Batas etis

Tidak ada pencurian data, izin tanpa batas, atau penghapusan lisensi pihak
ketiga. Detail: lihat `BLOCKERS.md` di repositori kerja asli.

## Lisensi

`Tom05ivier-commits-1.0` — Copyright (c) 2026 Tomi vier.

> Repositori ini adalah rilis bersih: dokumen otorisasi pribadi dan klon sumber
> pihak ketiga sengaja tidak disertakan.
