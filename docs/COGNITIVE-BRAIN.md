<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Otak Kognitif Supervisor IT Agenty

`system/cognitive_brain.py` memetakan empat fungsi kognitif otak manusia ke
komponen nyata di supervisor. Ini **analogi fungsional**, bukan klaim bahwa
perangkat lunak memiliki kesadaran, tubuh biologis, atau model neural baru.

Alur: **indra → memori → perencanaan → aksi**, lalu refleksi menutup siklus.

| No | Otak manusia | Fungsi kognitif | Komponen supervisor |
|---|---|---|---|
| 1 | Mata, telinga, kulit, lidah (rasa), propriosepsi | Menerima informasi dari indra, termasuk pengetahuan rasa | `advanced/engine.py` (`perceive`), `system/hardware_agent.py`, `system/service_watch.py`, `system/supervisor.py`, `config/tom05-connections.json`, `system/taste_knowledge.py`, `config/taste_knowledge.json` |
| 2 | Hippocampus & korteks asosiasi | Menyimpan pengalaman dan pengetahuan | `advanced/knowledge.py`, `system/tom05_knowledge.py`, `dataset/data/tom05_dataset.jsonl`, `advanced/memory.jsonl`, `agent/state.json`, `system/reports/` |
| 3 | Korteks prefrontal | Memutuskan tindakan dengan latar keseimbangan kepentingan–hak | `agent/brain.py`, `system/idea_engine.py`, `system/services.json`, `security/permission_automation.py`, `system/final_status.py`, `system/rights_balance.py`, `config/rights_balance.json` |
| 4 | Korteks motorik & otot | Melaksanakan tindakan / respon teks | `agent/runtime.py`, `system/chat_dispatch.py`, `config/chat_dispatch.json`, `system/cli.py`, `security/firewall/`, skill `android-device` |

## Penjelasan tiap lapisan

### 1. Indra = persepsi dan sensor

Sensor di dunia nyata digantikan oleh pembacaan status: `AdvancedComputer.perceive()`
mengumpulkan snapshot sistem, Hardware CLI membaca info perangkat lewat skill
`android-device`, Service Watch memeriksa kesehatan layanan, dan supervisor
menjaga heartbeat serta PID (propriosepsi / "tahu kondisi tubuh sendiri").

Batas jujur: bridge perangkat **tidak** mengekspos kamera, mikrofon, lidah, GPU,
atau Vulkan. Tidak ada input biometrik dan tidak ada probe jaringan baru dari
lapisan pemetaan ini.

**Pengetahuan rasa.** Karena tidak ada sensor kimia yang terhubung, rasa
dimasukkan sebagai kosakata simbolik: `config/taste_knowledge.json` mendefinisikan
lima kategori (`manis`, `asin`, `asam`, `pahit`, `umami`) dan
`system/taste_knowledge.py` menyajikannya read-only lewat `describe()`. Field
`perceive()["rasa"]` memuat `"sensor": false` dan kelima kategori tersebut.
Ini pengetahuan untuk penalaran, bukan pengukuran lidah, preferensi konsumsi,
atau data kesehatan subjek.

### 2. Memori = basis pengetahuan dan pengalaman

`KnowledgeBase` mengindeks dokumen workspace dengan checksum; `tom05_knowledge`
mengambil potongan relevan memakai TF-IDF ringan; dataset menyimpan 292 rekord
instruksi→jawaban yang sudah disaring privasinya; `advanced/memory.jsonl` dan
`agent/state.json` menyimpan jejak pengalaman dan keputusan.

Ini **retrieval berbasis berkas**, bukan pelatihan: tidak ada bobot neural dan
tidak ada proses training. Kredensial tidak pernah diindeks atau dicetak.

### 3. Perencanaan = korteks prefrontal

`AgentBrain.plan()` mengubah tujuan menjadi langkah dengan aturan deterministik.
`idea_engine` menyiapkan sepuluh ide supervisor, `services.json` menentukan
komponen yang dijalankan, `permission_automation` menjadi pengendali impuls
(TTL maksimal 300 detik, kategori terlarang ditolak), dan `final_status`
menjadi gerbang terakhir.

Aksi ofensif tidak pernah dipilih otomatis tanpa otorisasi. Ini perencana
aturan, bukan penalaran umum atau keputusan sadar.

**Latar keseimbangan kepentingan–hak.** `config/rights_balance.json` memuat
empat kepentingan operasional, lima hak (privasi, lisensi, izin tertulis yang
dapat dicabut, penolakan kategori dilarang, jejak audit), TTL maksimal 300
detik, dan prioritas `hak_mendahului_bila_bertentangan`. `system/rights_balance.py`
menyediakan `evaluate()`, `check()`, dan `describe()`. Setiap `plan()` kini
mengembalikan `"keseimbangan"`; tanpa izin pada aksi terbatas keputusannya
`hak_mendahului`, dengan izin menjadi `seimbang_terbatas`, sisanya `seimbang`.
Peta lengkap menyimpan ringkasannya di `"latar"`. Ini kebijakan perangkat
lunak, bukan nasihat hukum atau otoritas baru.

### 4. Aksi = otot dan saraf motorik

`AgentRuntime.execute()` menjalankan tugas dan mencatat audit. Relai chat
mengirim respon teks ke 11 responder lokal yang terdaftar di
`config/chat_dispatch.json`; perintah memakai argv (tanpa shell), sehingga
setiap eksekusi dapat diaudit. Aktuator perangkat berupa notifikasi, toast, clipboard,
dan `open-url` lewat skill. Firewall bertindak sebagai aktuator kebijakan
jaringan userspace.

Lapisan pemetaan **hanya mendeskripsikan** aktuator; ia tidak menjalankan
responder dan tidak mengubah layanan.

## Perintah

```bash
python3 system/cognitive_brain.py             # peta lengkap + tulis laporan
python3 system/cognitive_brain.py --verify    # kode 1 bila belum terpetakan
python3 system/cognitive_brain.py --no-write  # tanpa menulis laporan
python3 system/cognitive_brain.py --cycle "status sistem"  # satu siklus simulasi

./run_system.sh cognitive-map                 # lewat CLI supervisor
make cognitive-map                            # lewat Makefile
make cognitive-map-test                       # 18 kasus pengujian
tom05 --cognitive-map                         # lewat CLI tom05
```

Laporan: `system/reports/cognitive_brain.json` (skema
`tom05-cognitive-brain-map/1`). Status `TERPETAKAN` hanya berarti keempat
lapisan memiliki komponen nyata yang ada di workspace; status teknis ini tidak
mengubah lisensi, otorisasi, atau batas izin.

## Integrasi

- `system/cli.py` — perintah `cognitive-map`.
- `system/infinity_connectivity.py` — simpul `cognitive-brain`, `taste-knowledge`,
  dan `rights-balance` dalam graph konektivitas supervisor; `cognitive-brain`
  terhubung ke `advanced`, `agent`, `knowledge`, `chat-dispatch`, `dataset`,
  dan `device`.
- `config/taste_knowledge.json` + `system/taste_knowledge.py` — pengetahuan rasa
  simbolik pada indra.
- `config/rights_balance.json` + `system/rights_balance.py` — latar keseimbangan
  kepentingan dan hak pada perencanaan.
- `system/tests/test_cognitive_brain.py` — 18 kasus pengujian lapisan, bukti,
  rasa, latar hak, siklus, dan jaminan tanpa kredensial.
