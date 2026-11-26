<!-- SPDX-License-Identifier: Tom05ivier-commits-1.0 -->
<!-- Copyright (c) 2026 Tomi vier -->

# Peta koneksi supervisor ↔ model

Supervisor tidak menjalankan model sebagai proses. Yang dijaga supervisor adalah
layanan yang menyajikan model:

| Endpoint | Fungsi |
|---|---|
| `opencode_server` (8765) | server OpenCode; memuat semua model `opencode/*` |
| `copilot_bridge` (8766) | bridge ke `hy4-flash-free` |
| `tom05_provider` (8772) | provider tom05; alias `tom05-flash-free` + 94 model proxied |

`system/model_connectivity.py` menggabungkan identifier dari
`config/tom05-models.json`, `config/hy4-free-models.json`,
`config/tom05-provider-models.json`, dan `opencode.json`, lalu memetakan model
yang disebut pemilik ke endpoint yang diperlukan.

Model yang dipetakan eksplisit:

| Identifier | Catatan |
|---|---|
| `tom05/tom05-flash-free` | alias identitas; diteruskan lewat provider + bridge |
| `opencode/hy4-flash-free` | upstream alias tom05; lewat bridge + server |
| `opencode/deepseek-v4.1-flash-free` | model proxied, biaya nol |
| `opencode/glm-5.3-flash` | **tidak ada ID `glm-5.3-flash-free`**; ini alias proxied dengan biaya nol |
| `opencode/tidepool-alpha-free` | model proxied, biaya nol |

## Pemakaian

```bash
tom05 --model-connectivity
make model-connectivity
python3 system/model_connectivity.py
```

Laporan ditulis ke `system/reports/model_connectivity.json`. Status `TERHUBUNG`
hanya bila kelima model di atas memiliki semua endpoint aktif, supervisor
sehat, dan minimal tiga endpoint terhubung; selain itu `SEBAGIAN`.

## Batasan

- Pemeriksaan read-only terhadap layanan; tidak memulai atau mematikan proses.
- Tidak ada kredensial yang dibaca, dikirim, atau dicetak.
- Seluruh identifier adalah alias/proxy pihak ketiga, bukan model terlatih baru
  tom05; lisensi pihak ketiga tetap berlaku.
- Satu-satunya tulisan adalah file laporan JSON di `system/reports/`.
