<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Agent Computer

Otak agen otonom yang menyatukan **Infinity Computer System** dan
**Infinity Security Suite** menjadi satu runtime. Agen menerima tujuan berbahasa
Indonesia/Inggris sederhana, menyusun rencana, menjalankan tugas, dan
menyimpan jejak keputusan.

## Arsitektur

| Modul | Fungsi |
|---|---|
| `brain.py` | `AgentBrain.plan()` — tujuan → daftar langkah |
| `tasks.py` | Registri 7 tugas + kata kunci pemetaan |
| `runtime.py` | `AgentRuntime.run()` — eksekusi, audit, refleksi |
| `cli.py` | Antarmuka `run`, `plan`, `tasks`, `history` |

## Tugas yang tersedia

| Tugas | Fungsi |
|---|---|
| `status` | Snapshot seluruh sistem |
| `verify` | Verifikasi kepatuhan 8 pemeriksaan |
| `protect` | Daemon proteksi hardware berkelanjutan |
| `integrity` | Cek integritas hash berkas kritis & lab |
| `dashboard` | Bangkitkan `dashboard.html` |
| `capability` | Status CAP_NET_ADMIN & backend firewall |
| `perfect` | Siklus lengkap: capability → integrity → protect → verify → dashboard |
| `campaign` | Kampanye: proteksi → debug → serangan 3× → respons SOC |
| `drill` | Latihan serangan — **hanya dengan `authorize=True`** |

## Cara pakai

```bash
./run_agent.sh tasks
./run_agent.sh plan "lindungi hardware dan verifikasi"
./run_agent.sh run "lindungi hardware dengan antivirus"
./run_agent.sh run "sempurnakan sistem"
./run_agent.sh run "jalankan kampanye keamanan"
./run_agent.sh run "serang lab dengan malware" --authorize
./run_agent.sh history
```

## Keamanan

- Tugas ofensif (`drill`) **tidak akan berjalan** tanpa `--authorize`.
- Setiap langkah dicatat di `agent/state.json` beserta status dan hasilnya.
- Kegagalan satu langkah tidak menghentikan langkah lain; status akhir
  `SUCCESS`, `PARTIAL`, atau `FAILED`.
- Seluruh aksi tetap berada di dalam batas laboratorium (lab/localhost).

## Pengujian

```bash
python3 -m unittest discover -s agent/tests -v
```

## Lisensi

`Tom05ivier-commits-1.0` — Copyright (c) 2026 Tomi vier.
