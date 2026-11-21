<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Analisis Repositori Symphony (B3log) untuk IT Agenty

Dokumen ini menyimpulkan hasil pembacaan lokal terhadap repositori pihak ketiga di
`/root/workspace/symphony-src`. Seluruh fakta diambil dari file yang benar-benar ada di
dalam repositori itu — `README.md`, `README_en_US.md`, `LICENSE`, `pom.xml`, `Dockerfile`,
dan `THIRD_PARTY_LICENSE` — tanpa mengakses jaringan. Sesuai aturan `AGENTS.md`, kode
pihak ketiga ini tetap utuh: tidak ada satu pun file di dalam `symphony-src` yang diubah,
dan header `Tom05ivier-commits-1.0` hanya dipasang pada dokumen analisis ini.

## 1. Ringkasan Symphony

Symphony adalah platform komunitas modern yang dikembangkan oleh B3log (88250).
`pom.xml` menyebutnya sebagai "一款用 Java 实现的现代化社区（论坛/BBS/社交网络/博客）系统平台"
— sistem platform komunitas modern berbasis Java yang menggabungkan forum/BBS, jaringan
sosial, dan blog. Proyek ini dimulai pada tahun 2012 (`inceptionYear` 2012), dan versi
yang ter-clone di workspace adalah `3.6.4` dengan `groupId org.b3log`. Kode ditulis untuk
Java 17 (`maven.compiler.source`/`target` 17), dan titik masuknya adalah kelas
`org.b3log.symphony.Server`.

Dari sisi arsitektur, Symphony berdiri di atas framework **Latke** versi `3.5.2`
(`latke-core` dan `latke-repository-mysql`), yang oleh README disebut sebagai "Java Web
framework based on JSON". Penyimpanan memakai MySQL melalui modul repository Latke.
Untuk konten, terdapat **Vditor** sebagai editor Markdown di browser, dengan dukungan
GFM, Emoji, LaTeX, dan diagram alur; di sisi server pemrosesan Markdown dilakukan oleh
`flexmark` `0.64.0`, sementara `jsoup` `1.16.1` menangani HTML. `THIRD_PARTY_LICENSE`
mencatat secara transparan lisensi setiap dependensi, baik backend (Latke, jsoup,
flexmark, log4j, mysql-connector-java, dan lain-lain) maupun frontend (jQuery,
highlight.js, MathJax, md5, dan lain-lain) — dengan campuran MIT, BSD, APL, GPL, dan
beberapa lisensi khusus seperti CC BY-NC-SA untuk SoundRecorder.

Distribusi kontainer memakai image Docker resmi **`b3log/symphony`**. `Dockerfile` di
repositori menunjukkan build dua tahap: `maven:3.9-eclipse-temurin-17` untuk
`mvn package -DskipTests -Pci`, lalu runtime `eclipse-temurin:17-jre-alpine` yang
mengekspos port `8080` dan menjalankan `java -cp lib/*:. org.b3log.symphony.Server`.

Fitur utamanya, seperti tercantum dalam daftar panjang di README, mencakup tiga pilar:
forum untuk diskusi berbasis konten, komunitas tanya-jawab untuk pengetahuan, dan
jaringan sosial untuk berbagi, berteman, serta game. Di dalamnya ada editor Markdown
dengan pratinjau dan WYSIWYG, sistem tag dan domain, voting, area打赏 (reward), poin dan
dompet ETH, posting anonim, moderasi dan audit, pencarian (Algolia atau Elasticsearch
sendiri), notifikasi, autentikasi dua langkah, serta API sinkronisasi B3 antara blog dan
forum. README menyebut proyek ini `100%` open source dan mengarahkan diskusi ke forum
resmi di `ld246.com/tag/sym`.

Soal skala popularitas, perlu jujur: README hanya memuat badge dinamis dari GitHub dan
Docker Hub — Docker Pulls, GitHub Stars, Forks, Downloads, Commits, Last Commit, dan
Hits — tetapi **tidak memuat angka statis** yang bisa dikutip dari salinan lokal ini.
Karena itu tidak ada angka jumlah pengguna, star, atau pull yang saya klaim di sini.
Yang dapat dipastikan secara lokal hanyalah jejak aktivitas: klon workspace ini memiliki
commit terakhir `c3e204806f98410d7f8484825de4ef9f85c13f9f` oleh `Daniel` tanggal
`2026-11-13 11:22:21 +0800` dengan pesan "Move article visibility checks into
ArticleQueryService", yang menunjukkan repositori masih aktif dikembangkan.

## 2. Kewajiban lisensi AGPLv3 secara konkret

File `LICENSE` adalah teks resmi **GNU Affero General Public License Version 3, 19
November 2007**, dan `pom.xml` mengonfirmasi hal yang sama pada blok `<licenses>`.
Yang membedakan AGPL dari GPL biasa adalah copyleft jaringan. Pembukaan `LICENSE`
berkata secara eksplisit bahwa lisensi ini "dirancang khusus untuk memastikan kerja
sama dalam kasus perangkat lunak server jaringan", dan bahwa ia "mewajibkan operator
server jaringan untuk menyediakan kode sumber versi yang dimodifikasi yang berjalan di
sana kepada pengguna server tersebut. Oleh karena itu, penggunaan publik atas versi
yang dimodifikasi pada server yang dapat diakses publik memberi publik akses terhadap
kode sumber versi yang dimodifikasi itu."

Artinya, dua kewajiban konkret muncul bila kita **memodifikasi** Symphony lalu
**menjalankannya sebagai layanan yang diakses orang lain**: pertama, kode sumber versi
modifikasi itu harus dipublikasikan kepada pengguna layanan; kedua, pembatas dan
pemberitahuan lisensi asli tidak boleh dihapus atau disamarkan. README memperjelas
model komersialnya: edisi komunitas memakai AGPLv3 dan harus dipatuhi sepenuhnya,
penggunaan oleh perusahaan wajib membeli lisensi komersial, edisi komersial dengan
source lengkap untuk pengembangan lanjutan dibanderol **¥20.000**, dan layanan cloud
siap pakai **¥5.000 per tahun** (saat ini tercatat售罄 / habis terjual). README juga
menekankan bahwa situs perusahaan, situs komersial, dan situs bertujuan profit harus
membeli edisi komersial.

Aturan `AGENTS.md` sejalan dengan itu. Kode yang di-clone dari pihak ketiga tetap
tunduk pada lisensi aslinya; dilarang menghapus pembatas lisensi, paywall, atau
mekanisme pembayaran proyek tersebut (bagian "Batasan lisensi pihak ketiga"). Lebih
lanjut, aturan meta-izin otomatis memasukkan `third-party-license-removal` ke dalam
kategori yang **tetap ditolak**, dan izin "tanpa batas" tidak dikenal — semua izin
berlaku terbatas sampai 31 Desember 2027. `Tom05ivier-commits-1.0` hanya berlaku untuk
karya IT Agenty, bukan untuk kode pihak ketiga.

Perbedaan antara "meng-clone untuk dipelajari" dan "mengintegrasikan ke produk IT
Agenty" terletak pada pemicu kewajiban ini. Meng-clone ke `symphony-src` untuk dibaca,
dipelajari, dan dijadikan referensi arsitektur adalah salinan privat: tidak ada
distribusi dan tidak ada layanan jaringan yang diberikan kepada publik, sehingga
kewajiban publish source tidak terpicu — tetapi tetap dengan syarat menjaga file
`LICENSE`, `THIRD_PARTY_LICENSE`, dan seluruh header lisensi tetap utuh. Sebaliknya,
mengambil potongan kode Symphony lalu menyatukannya ke produk IT Agenty, atau
menjalankan versi modifikasi sebagai layanan komunitas yang bisa diakses pihak lain,
adalah tindakan yang masuk ke ranah copyleft AGPL: versi turunan wajib tetap ber-AGPL,
source harus tersedia bagi pengguna jaringan, dan lisensi IT Agenty tidak bisa
diplakatkan ke atasnya tanpa lisensi komersial dari B3log. Membedakan dua skenario ini
adalah garis aman yang harus dijaga.

## 3. Catatan keamanan

README mencantumkan bagian tersendiri berjudul "已知的安全漏洞" / "Known Security
Vulnerabilities", dan isinya hanya dua butir. Pertama, **penyimpanan kata sandi
menggunakan MD5 dinyatakan tidak aman** (merujuk ke issue `88250/symphony#74`). Kedua,
**cara kata sandi ditransmisikan antara frontend dan backend dinyatakan tidak aman**
(merujuk ke issue `88250/symphony#75`). Kedua pernyataan ini tercantum identik di
`README.md` maupun `README_en_US.md`, dan README juga menyampaikan terima kasih kepada
tim keamanan serta beberapa peneliti atas temuan mereka.

Penyebutan di sini sengaja dibatasi pada fakta yang ditulis proyek: tidak ada
penjelasan teknis tambahan, tidak ada detail eksploitasi, dan tidak ada dusta
tentang cara mengeksploitasi. Bagi IT Agenty, makna praktisnya sederhana — repositori
ini tidak boleh dijadikan acuan praktik baik untuk penyimpanan maupun transmisi
kredensial, dan evaluasi keamanan apa pun harus dilakukan sendiri dengan teks README
ini sebagai peringatan awal, bukan sebagai deskripsi kerentanan yang lengkap.

## 4. Opsi penggunaan untuk IT Agenty

Ada tiga jalur yang dapat dipertimbangkan, dengan profil risiko hukum yang berbeda.

**Opsi (a) — referensi arsitektur.** Kita mempelajari struktur Symphony: bagaimana
Latke dipakai sebagai lapisan web, bagaimana alur Markdown dari Vditor hingga
flexmark, bagaimana peta fitur forum/Q&A/sosial disusun, serta bagaimana image Docker
dirakit. Ini adalah penggunaan paling ringan: tidak ada kode yang disalin ke produk,
tidak ada layanan yang dijalankan untuk publik, sehingga kewajiban copyleft tidak
terpicu. Risikonya praktis nol selama pembatas lisensi di `symphony-src` tidak
diubah.

**Opsi (b) — deploy terpisah sebagai forum komunitas dengan AGPLv3 dipatuhi.**
Kita menjalankan edisi komunitas apa adanya sebagai layanan tersendiri. Bila tidak
dimodifikasi, kewajiban utama adalah mematuhi seluruh ketentuan AGPLv3 dan
menghormati lisensi pihak ketiga yang tercantum di `THIRD_PARTY_LICENSE`. Bila ada
modifikasi dan layanan diakses publik, kode sumber versi modifikasi wajib dipublikasikan
kepada pengguna. Untuk penggunaan perusahaan atau situs profit, README mengarahkan
ke lisensi komersial berbayar. Perlu dicatat pula bahwa sesuai aturan `AGENTS.md`,
komponen server baru wajib didaftarkan di `system/services.json` lewat
`./run_system.sh service-add` — pada analisis ini saya tidak menyentuh registry itu.

**Opsi (c) — portal komunitas baru karya IT Agenty dengan lisensi
`Tom05ivier-commits-1.0`.** Ini adalah opsi yang sedang dibangun agen lain: karya
original IT Agenty yang ditulis ulang dari awal, dengan header dan lisensi sendiri.
Kunci keamanan hukumnya adalah *clean room* — desain dan ide boleh terinspirasi dari
pengamatan arsitektur, tetapi tidak boleh menyalin kode Symphony, template, atau aset
berlisensi AGPL ke dalamnya.

**Rekomendasi.** Yang paling aman secara hukum adalah **kombinasi (a) dan (c)**:
jadikan Symphony sebagai bahan belajar arsitektur saja, lalu bangun portal komunitas
IT Agenty secara original dengan lisensi `Tom05ivier-commits-1.0`. Kita mendapatkan
manfaat desain tanpa pernah memicu kewajiban publish source AGPL dan tanpa biaya
lisensi komersial. Opsi (b) baru layak dipilih jika organisasi secara sadar menerima
kewajiban AGPL penuh, atau bersedia membeli lisensi komersial ¥20.000 / cloud ¥5.000
per tahun sesuai README; dan itu pun harus diputuskan oleh pemilik, bukan diambil
sendiri oleh agen.

## 5. Langkah verifikasi mandiri

Perintah berikut bisa dijalankan ulang kapan saja untuk memeriksa kembali fakta di atas
tanpa menyentuh isi repositori:

```bash
ls -l /root/workspace/symphony-src/LICENSE
head -n 6 /root/workspace/symphony-src/LICENSE
git -C /root/workspace/symphony-src log -1 --format='%H %an %ad %s' --date=iso
grep -n -A4 'Known Security Vulnerabilities\|已知的安全漏洞' /root/workspace/symphony-src/README.md
grep -n -A6 '<licenses>' /root/workspace/symphony-src/pom.xml
grep -nE 'FROM|EXPOSE|ENTRYPOINT' /root/workspace/symphony-src/Dockerfile
head -n 10 /root/workspace/symphony-src/THIRD_PARTY_LICENSE
```

Rangkaian itu secara berurutan menampilkan keberadaan dan identitas lisensi, metadata
commit terakhir, dua peringatan keamanan dari README, deklarasi AGPL di `pom.xml`,
langkah build dan port container, serta daftar lisensi dependensi pihak ketiga.

## 6. Lampiran operasional: dari rekomendasi ke implementasi

Rekomendasi (a)+(c) sudah ditindaklanjuti. Supaya klaim *clean room* dapat diaudit,
berikut peta antara ide yang diamati dari Symphony dan apa yang benar-benar
diimplementasikan di portal `site/community/`. Yang dipindahkan adalah **pengertian
tentang masalah**, bukan kode, template, atau aset.

| Ide yang diamati dari Symphony | Implementasi di portal IT Agenty | Status |
|---|---|---|
| Forum diskusi berbasis konten | Posting dengan judul, penulis, isi, dan balasan bertingkat satu level | Sudah ada |
| Alur Markdown Vditor → flexmark | Teks biasa dengan escape HTML di sisi klien; tidak ada editor Markdown | Sengaja tidak diadopsi |
| Tag, domain, voting, poin, dompet | Tidak ada | Dicatat sebagai ide, belum dibuat |
| Moderasi, audit, autentikasi dua langkah | Tidak ada | Belum dibuat; perlu keputusan terpisah |
| Latke + MySQL + image Docker | Python stdlib `http.server`, penyimpanan JSON atomik, berjalan di container Infinity | Berbeda secara sengaja |
| Pencarian Algolia / Elasticsearch | Tidak ada | Belum dibuat |

Dengan demikian manfaat desain yang diambil adalah pembagian fungsi dasar
"konten → diskusi → balasan" dan kebutuhan akan moderasi di kemudian hari.
Tidak ada satu pun berkas dari `symphony-src/` yang diimpor, disalin, atau
dijadikan dasar template. Pemeriksaan mandiri:

```bash
# Hanya berkas implementasi yang diperiksa. README portal memang menyebut
# kata "Symphony"/"AGPL" sekadar untuk menyatakan tidak ada kode tersebut.
grep -i -E 'b3log|symphony|AGPL' \
  /root/workspace/site/community/server.py \
  /root/workspace/site/community/app.js \
  /root/workspace/site/community/index.html \
  /root/workspace/site/community/style.css \
  && echo 'PERLU DITELITI' || echo 'BERSIH: tidak ada jejak kode Symphony'
git -C /root/workspace/symphony-src status --porcelain   # harus kosong
```

Jika suatu hari fitur tag atau moderasi ditambahkan, itu harus ditulis ulang dari
spesifikasi IT Agenty, bukan dengan mengambil komponen dari repositori AGPL.
Keputusan untuk tidak mengambil jalur (b) tercatat di
`docs/KEPUTUSAN-KOMUNITAS.md`.

— `(__signature__)`
