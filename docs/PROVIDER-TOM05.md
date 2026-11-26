<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Provider mandiri `provider-tom05`

## Status: AKTIF

Repository [`tom05ivier-commits/provider-tom05`](https://github.com/tom05ivier-commits/provider-tom05)
berisi implementasi provider yang dapat dipanggil, dengan commit
`a634da70ffab0c57cc42fe3b4977c449fa4f8b7f`.

| Item | Nilai |
|---|---|
| Isi repo | `.gitignore`, `LICENSE`, `NOTICE`, `README.md`, `provider.json`, `server.py` |
| Lisensi kode provider | **GNU AGPL-3.0** (dipertahankan, tidak diubah) |
| Endpoint lokal | `http://127.0.0.1:8772/v1` |
| Model OpenCode | `tom05/tom05-flash-free` |
| Model proxied | **94 identifier model pihak ketiga** dari `opencode models` |
| Katalog terpisah | `config/tom05-provider-models.json` |
| Surat persetujuan | `surat-persetujuan-tom05-model.md` (operasional, terbatas) |
| Draf izin | `DRAF-surat-izin-gratis-model-tom05.md` (**draf, belum berlaku**) |
| Layanan | `tom05-provider` di `system/services.json` (hot-reload supervisor) |

## Pemisahan model dari OpenCode

Daftar seluruh model yang tersedia di `opencode models` diekstrak ke
`config/tom05-provider-models.json` dan disajikan oleh provider lokal melalui
`GET /v1/models`. Ini adalah **alias/proxy**, bukan model baru:

- identifier pihak ketiga (`opencode/`, `opencode-go/`, `claude-code/`,
  `console-meta/`) diteruskan apa adanya ke runtime;
- alias `tom05/*` diterjemahkan ke model upstream `hy4-flash-free`;
- tidak ada bobot model yang disalin, dilatih, atau diklaim sebagai karya
  tom05 — lisensi dan kepemilikan tetap pada pihak ketiga;
- endpoint tetap di loopback dan tidak membuka akses publik.

Lihat `surat-persetujuan-tom05-model.md` untuk ruang lingkup dan batas izin
operasionalnya. Daftar lengkap bisa dilihat dengan `tom05 --list-all-models`.

## Draf izin gratis dan larangan komersial (belum berlaku)

`DRAF-surat-izin-gratis-model-tom05.md` menyiapkan dua ketentuan: penggunaan
gratis alias `tom05/*` pada tier gratis, dan larangan tier pro serta
pemanfaatan komersial. **Draf ini bukan otorisasi dan belum mengikat.** Ada
konflik yang harus diselesaikan pemilik: `LICENSE` Tom05ivier-commits v1.0
yang aktif **mengizinkan** penggunaan komersial dan penjualan salinan dengan
atribusi, sedangkan draf itu melarang pengambilan keuntungan. Larangan tersebut
dirancang **tidak berlaku surut** dan baru mengikat setelah amandemen lisensi
ditandatangani manual oleh pemilik dan diterbitkan. Sampai saat itu, `LICENSE`
v1.0 tetap menjadi sumber hak yang berlaku.

Draf ini juga **tidak** mengatur lisensi atau paywall penyedia pihak ketiga,
tidak menghapus mekanisme pembayaran mereka, dan tidak boleh dipakai untuk
mengklaim alias `tom05/*` sebagai model latihan Tom05. Tidak ada tanda tangan
`(__signature__)` yang diisi otomatis; semua kolom penandatanganan sengaja
ditinggalkan kosong untuk diisi manual oleh pemilik.

## Lisensi

Repo memakai AGPL-3.0. Kode di dalamnya tunduk pada lisensi itu; karya IT Agenty
di workspace tetap memakai `Tom05ivier-commits-1.0`. Keduanya tidak dicampur dan
pembatas lisensi tidak dihapus.

`TOM05-FLASH-FREE-NOTICE.md` adalah pernyataan hak cipta **terpisah** atas karya
orisinal IT Agenty pada "Tom05 flash Free" (nama, katalog, konfigurasi, prompt,
dan dokumentasi). NOTICE itu tidak mengubah fakta teknis bahwa
`tom05/tom05-flash-free` saat ini adalah alias/proxy ke `opencode/hy4-flash-free`,
tidak menciptakan hak atas model pihak ketiga, dan tidak menggantikan `LICENSE`
v1.0. Pendaftaran formal dan penandatanganan tetap menjadi keputusan pemilik.

## Kesetaraan dengan hy4-flash-free

```bash
tom05 --parity
python3 system/model_parity.py
python3 system/model_parity.py --live   # uji prompt identik (opsional)
```

Laporan memastikan `tom05/tom05-flash-free` memakai `modelID: hy4-flash-free`,
varian `none`/`high`, biaya nol, dan `resolve_upstream()` mengarah ke
`hy4-flash-free`. Ini alias/proxy, bukan model terlatih baru.

Parity deklarasi model gratis/proxied lain (misalnya DeepSeek) membandingkan
empat sumber: `config/tom05-models.json`, `config/hy4-free-models.json`,
`config/tom05-provider-models.json`, dan entri di `opencode.json`:

```bash
tom05 --parity-model opencode/deepseek-v4.1-flash-free
tom05 --parity-all
python3 system/model_parity.py --model opencode/deepseek-v4.1-flash-free
python3 system/model_parity.py --all
```

Hasil `SAMA` berarti nama, varian, status aktif, ctl 100M, biaya nol, dan
penanda `proxied/declared_only` konsisten. Model tetap milik pihak ketiga;
ini bukan klaim model baru tom05.

## Integrasi

`server.py` menyajikan `/v1/models` dan `/v1/chat/completions` pada loopback,
lalu meneruskan permintaan ke bridge yang ada. OpenCode mendaftarkannya sebagai
provider kustom:

```jsonc
{
  "providers": {
    "tom05": {
      "name": "Tom05",
      "package": "@opencode/ai/providers/openai-compatible",
      "settings": { "baseURL": "http://127.0.0.1:8772/v1" },
      "models": {
        "tom05-flash-free": {
          "name": "Tom05 flash Free",
          "modelID": "hy4-flash-free"
        }
      }
    }
  }
}
```

Verifikasi:

```bash
opencode models                     # memuat tom05/tom05-flash-free
python3 system/tom05_provider.py    # server (biasanya otomatis via supervisor)
curl http://127.0.0.1:8772/health    # status, model, jumlah model proxied
curl http://127.0.0.1:8772/v1/models  # 94 model + alias tom05
curl -sS -X POST http://127.0.0.1:8772/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"tom05/tom05-flash-free","messages":[{"role":"user","content":"Balas hanya: OK"}]}'
tom05 --list-all-models             # daftar model proxied
./tom05 "Balas hanya: OK"           # menjalankan model tom05
```

Server hanya mendengar di loopback, tidak membaca kredensial, dan meneruskan
ke model upstream yang sudah ada. Ini alias/proxy gratis; lisensi dan paywall
pihak ketiga tetap berlaku.

### Konfigurasi workspace dan keselarasan endpoint

Sumber konfigurasi yang dipakai:

| Berkas | Peran |
|---|---|
| `~/.config/opencode/opencode.json` | Konfigurasi OpenCode global (provider + model aktif) |
| `opencode.json` di root workspace | Konfigurasi proyek; mencerminkan provider yang sama |
| `config/tom05-provider.json` | Status `AKTIF` dan endpoint resmi layanan |
| `provider-tom05/provider.json` | Metadata repo hulu (lisensi AGPL-3.0 dipertahankan) |

Keempatnya harus menunjuk ke **`http://127.0.0.1:8772/v1`**. Layanan `tom05-selfhost`
di `8773` adalah jalur terpisah (satu model, mode retrieval) dan **bukan**
endpoint provider; jangan memakai `8773` sebagai `baseURL` provider OpenCode.
Salinan kerja repo tersedia di `tom05ivier-commits/provider-tom05/` dengan isi
dan lisensi hulu yang tidak diubah.

Verifikasi keselarasan:

```bash
python3 -m json.tool ~/.config/opencode/opencode.json >/dev/null
python3 -m json.tool opencode.json >/dev/null
python3 -c "import json;print(json.load(open('opencode.json'))['providers']['tom05']['settings']['baseURL'])"
curl -sS http://127.0.0.1:8772/health
```

## Batas konteks yang dideklarasikan

Model `tom05/tom05-flash-free` mengalokasikan `limit.context` dan `limit.input`
sebesar **100.000.000 token** (1M × 100) di konfigurasi OpenCode, dengan biaya
`0`. Nilai yang sama tersedia sebagai `ctl` di CLI (`tom05 --ctl` → `100000000`)
dan di metadata provider repo (`context_length`, `declared_only: true`).
Cadangan konfigurasi sebelum perubahan ada di
`/root/.config/opencode/opencode.json.before-ctx-*`.

**Cakupan penuh.** Seluruh model yang dilayani provider (`GET /v1/models`,
94 alias proxied + entri alias Tom05) kini menyatakan `ctl` / `context_length`
= **100.000.000** secara seragam. Nilai per model tersimpan di katalog
`config/tom05-provider-models.json` (kunci `ctl`, `declared_only: true`) dan
diteruskan oleh `system/tom05_provider.py` lewat `model_entries()`. Serve default
jika kunci tidak ada tetap memakai `TOM05_CTL` (bawaan `100000000`). Ini hanya
deklarasi ambang kompaksi OpenCode, bukan kapasitas fisik model pihak ketiga.

**Ini adalah batas yang dideklarasikan, bukan kapasitas fisik yang dijamin.**
Nilai itu hanya menentukan kapan OpenCode melakukan kompaksi/pemotongan riwayat.
Model yang mendasari tetap memiliki batas nyata di runtime; memaksa konteks
jauh melebihi kemampuan dapat menyebabkan error, pemotongan diam-diam, atau
penggunaan memori besar. Jika terjadi masalah, kembalikan dari berkas backup
dan turunkan nilainya.

CLI `hy4` di root sudah dinonaktifkan menjadi `hy4.nonaktif-20261122` dan tidak
dipasang di PATH; `./tom05` adalah CLI kanonik. Tidak ada kredensial yang dibaca,
disimpan, atau dicetak oleh provider ini.
