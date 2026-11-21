# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
# Pembangkit dashboard HTML statis dari snapshot sistem.

from __future__ import annotations

import html
import json
from pathlib import Path

from .core import WORKSPACE, ComputerSystem

OUTPUT = WORKSPACE / "dashboard.html"


def _esc(value: object) -> str:
    return html.escape(str(value))


def _card(title: str, rows: list[tuple[str, object]]) -> str:
    body = "".join(
        f"<div class='row'><span class='key'>{_esc(k)}</span>"
        f"<span class='val'>{_esc(v)}</span></div>"
        for k, v in rows
    )
    return f"<section class='card'><h2>{_esc(title)}</h2>{body}</section>"


def _links_card() -> str:
    """Kartu tautan ke situs statis yang dikelola supervisor."""
    links = (
        ("Hub situs", "http://127.0.0.1:8769/"),
        ("Chip Merah Putih", "http://127.0.0.1:8769/chip/"),
        ("Simulator chip", "http://127.0.0.1:8769/chip/simulator.html"),
        ("Mirror aplikasi asli", "http://127.0.0.1:8770/"),
        ("Tentang mirror", "http://127.0.0.1:8769/mirror/"),
        ("Landing page IT Agenty", "http://127.0.0.1:8769/agency/"),
        ("Situs asli (eksternal)", "https://chip.peruri.co.id/"),
    )
    body = "".join(
        f"<div class='row'><a class='val' href='{_esc(url)}'>{_esc(label)}</a></div>"
        for label, url in links
    )
    return f"<section class='card'><h2>Situs &amp; Layanan</h2>{body}</section>"


def _score_card() -> str:
    """Tampilkan skor chip dan keamanan dari laporan terbaru."""
    sources = (
        ("Chip", WORKSPACE / "chip" / "reports" / "chip_score.json", "grade"),
        ("Keamanan", WORKSPACE / "security" / "reports" / "security_score.json", "skor_keamanan"),
    )
    rows: list[tuple[str, object]] = []
    for label, path, key in sources:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            value = data.get(key, data.get("grade", "-"))
        except (OSError, json.JSONDecodeError):
            value = "-"
        rows.append((label, value))
    return _card("Skor Kualitas", rows)


def render(snapshot: dict[str, object]) -> str:
    """Render snapshot menjadi dokumen HTML mandiri."""
    ident = snapshot["identitas"]  # type: ignore[index]
    lis = snapshot["lisensi"]  # type: ignore[index]
    otor = snapshot["otorisasi"]  # type: ignore[index]
    ling = snapshot["lingkungan"]  # type: ignore[index]
    keamanan = snapshot["keamanan"]  # type: ignore[index]
    berkas = snapshot["berkas"]  # type: ignore[index]
    agen = snapshot["agen"]  # type: ignore[index]
    kampanye = snapshot["kampanye"]  # type: ignore[index]
    advanced = snapshot["advanced"]  # type: ignore[index]

    cards = [
        _card(
            "Identitas Pemilik",
            [(k, v) for k, v in ident.items()],
        ),
        _card(
            "Lisensi",
            [
                ("Identitas", lis["identitas"]),
                ("Versi", lis["versi"]),
                ("Pemilik", lis["pemilik"]),
                ("Status", lis["status"]),
            ],
        ),
        _card(
            "Otorisasi",
            [
                ("Surat izin", otor["surat_izin"]),
                ("Surat kuasa", otor["surat_kuasa"]),
                ("Nomor izin", otor["nomor_izin"]),
                ("Bertanda tangan", otor["bertanda_tangan"]),
                ("Berlaku", otor["berlaku"]),
            ],
        ),
        _card(
            "Lingkungan Sistem",
            [
                ("Script profile.d", ling["jumlah_script"]),
                ("Daftar script", ", ".join(ling["profile_scripts"])),
                ("Warna rgb.txt", ling["rgb_colors"]),
                ("sitecustomize.py", ling["sitecustomize"]),
            ],
        ),
        _card(
            "Keamanan",
            [
                ("Verifikasi", keamanan["verifikasi"]),
                ("Pemeriksaan lulus", keamanan["verifikasi_pass"]),
                (
                    "IP diblokir",
                    ", ".join(keamanan["firewall_policy"]["daftar_ip_diblokir"]) or "-",
                ),
                (
                    "Port ditolak",
                    ", ".join(keamanan["firewall_policy"]["daftar_port_ditolak"]) or "-",
                ),
                (
                    "Integritas",
                    "perubahan" if keamanan["integritas"]["changed"] else "stabil",
                ),
                ("Berkas dipantau", keamanan["integritas"]["total"]),
                ("Laporan", ", ".join(keamanan["laporan"])),
            ],
        ),
        _card(
            "Agent Computer",
            [
                ("Aktif", agen["aktif"]),
                ("Jalankan", agen["jalankan"]),
                ("Status terakhir", agen["status_terakhir"]),
            ],
        ),
        _card(
            "Kampanye Terakhir",
            [
                ("Status", kampanye["status"]),
                ("Siklus", kampanye["siklus"]),
                ("Skor risiko", kampanye["skor_risiko"]),
            ],
        ),
        _card(
            "Advanced Computer",
            [
                ("Dokumen knowledge", advanced["dokumen"]),
                ("Rekam memori", advanced["memori"]),
                ("Mode", "tanpa batas iterasi"),
            ],
        ),
        _card(
            "Inventaris Berkas",
            [(k, v) for k, v in berkas.items()],
        ),
        _score_card(),
        _links_card(),
    ]

    return f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{_esc(snapshot['sistem'])}</title>
<style>
  :root {{ --bg:#0b1220; --card:#121c2e; --accent:#28a4a0; --text:#e6edf3; --muted:#8b9bb4; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--text);
         font-family:system-ui,-apple-system,"Segoe UI",sans-serif; }}
  header {{ padding:2.5rem 1.5rem; background:linear-gradient(135deg,#0f5b8c,#28a4a0); }}
  header h1 {{ margin:0; font-size:2rem; }}
  header p {{ margin:.5rem 0 0; opacity:.85; }}
  main {{ max-width:1100px; margin:2rem auto; padding:0 1.25rem;
          display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:1.2rem; }}
  .card {{ background:var(--card); border:1px solid #1f2c44; border-radius:14px; padding:1.4rem; }}
  .card h2 {{ margin:0 0 1rem; font-size:1.1rem; color:var(--accent); }}
  .row {{ display:flex; justify-content:space-between; gap:1rem; padding:.35rem 0;
          border-bottom:1px solid #1b2740; font-size:.9rem; }}
  .row:last-child {{ border:none; }}
  .key {{ color:var(--muted); }}
  .val {{ text-align:right; word-break:break-word; }}
  a.val {{ color:var(--accent); text-decoration:none; }}
  a.val:hover {{ text-decoration:underline; }}
  footer {{ text-align:center; color:var(--muted); padding:2rem 1rem; font-size:.85rem; }}
</style>
</head>
<body>
<header>
  <h1>{_esc(snapshot['sistem'])}</h1>
  <p>Snapshot terakhir: {_esc(snapshot['generated_at'])}</p>
</header>
<main>
{''.join(cards)}
</main>
<footer>
  {_esc(snapshot['identitas']['nama'])} &mdash; {_esc(snapshot['lisensi']['identitas'])} v{_esc(snapshot['lisensi']['versi'])}
</footer>
</body>
</html>
"""


def generate() -> Path:
    """Tulis dashboard.html dan kembalikan path-nya."""
    snapshot = ComputerSystem().snapshot()
    OUTPUT.write_text(render(snapshot), encoding="utf-8")
    return OUTPUT
