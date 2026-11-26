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
        ("Tom05", WORKSPACE / "system" / "reports" / "tom05_score.json", "grade"),
        ("Perangkat", WORKSPACE / "system" / "reports" / "device_score.json", "grade"),
        ("Container", WORKSPACE / "system" / "reports" / "container_score.json", "grade"),
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


def _display_card() -> str:
    """Kartu profil tampilan Tom05 dari katalog (nama, lanskap, GPU)."""
    data: dict[str, object] = {}
    try:
        data = json.loads(
            (WORKSPACE / "config" / "tom05-models.json").read_text(encoding="utf-8")
        )
        disp = data["capabilities"]["display"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        disp = {}
    gpu = disp.get("gpu_acceleration", {})
    if not isinstance(gpu, dict):
        gpu = {}
    container = data.get("capabilities", {}).get("container", {})  # type: ignore[union-attr]
    if not isinstance(container, dict):
        container = {}
    rows = [
        ("Nama tampilan", disp.get("name", "-")),
        ("Orientasi", disp.get("orientation", "-")),
        ("Output", disp.get("output", "-")),
        ("Akselerasi GPU", ", ".join(gpu.get("backends", [])) or "-"),
        ("Backend utama", gpu.get("preferred", "-")),
        ("Mode", gpu.get("mode", "-")),
        ("Manager", f"{container.get('manager', '-')}:8766"),
        ("Jaringan", container.get("network", "-")),
        ("Catatan", gpu.get("catatan", "-")),
    ]
    return _card("Tampilan Tom05", rows)


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
        _display_card(),
        _links_card(),
    ]

    return f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{_esc(snapshot['sistem'])}</title>
<style>
  :root {{ --bg:#0a1020; --card:#121c2e; --card-2:#16223a; --accent:#2dd4bf; --accent-2:#38bdf8; --text:#e6edf3; --muted:#94a3c4; --line:#1e2c47; --shadow:rgba(0,0,0,.35); }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; color:var(--text); min-height:100vh;
          font-family:system-ui,-apple-system,"Segoe UI",sans-serif;
          background:radial-gradient(1200px 600px at 12% -10%, #123a5a 0%, transparent 60%),
                     radial-gradient(900px 500px at 100% 0%, #0d3b46 0%, transparent 55%),
                     var(--bg); }}
  header {{ padding:3rem 1.5rem 2.5rem; position:relative; overflow:hidden;
            background:linear-gradient(135deg,#0f5b8c 0%,#136c86 45%,#28a4a0 100%);
            box-shadow:0 10px 30px var(--shadow); }}
  header::after {{ content:""; position:absolute; inset:0; pointer-events:none;
            background:radial-gradient(circle at 85% 15%,rgba(255,255,255,.14),transparent 42%); }}
  header h1 {{ margin:0; font-size:clamp(1.6rem,4vw,2.4rem); letter-spacing:.02em;
               text-shadow:0 2px 12px rgba(0,0,0,.3); }}
  header p {{ margin:.65rem 0 0; opacity:.9; font-size:.95rem; }}
  main {{ max-width:1180px; margin:2.5rem auto; padding:0 1.25rem;
          display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:1.25rem; }}
  .card {{ background:linear-gradient(180deg,var(--card-2),var(--card));
           border:1px solid var(--line); border-radius:16px; padding:1.4rem 1.5rem;
           box-shadow:0 8px 24px var(--shadow); animation:rise .5s ease both;
           transition:transform .2s ease, box-shadow .2s ease, border-color .2s ease; }}
  .card:nth-child(2) {{ animation-delay:.04s; }}
  .card:nth-child(3) {{ animation-delay:.08s; }}
  .card:nth-child(n+4) {{ animation-delay:.12s; }}
  .card:hover {{ transform:translateY(-4px); border-color:var(--accent);
                 box-shadow:0 16px 36px var(--shadow); }}
  .card h2 {{ margin:0 0 1rem; font-size:1.02rem; letter-spacing:.06em; text-transform:uppercase;
              color:var(--accent); display:flex; align-items:center; gap:.6rem; }}
  .card h2::before {{ content:""; width:8px; height:8px; border-radius:50%;
              background:var(--accent); box-shadow:0 0 10px var(--accent); }}
  .row {{ display:flex; justify-content:space-between; gap:1rem; padding:.45rem 0;
          border-bottom:1px solid var(--line); font-size:.9rem; transition:background .15s ease; }}
  .row:hover {{ background:rgba(45,212,191,.05); }}
  .row:last-child {{ border:none; }}
  .key {{ color:var(--muted); }}
  .val {{ text-align:right; word-break:break-word; font-weight:500; }}
  a.val {{ color:var(--accent-2); text-decoration:none; }}
  a.val:hover {{ text-decoration:underline; }}
  footer {{ text-align:center; color:var(--muted); padding:2rem 1rem; font-size:.85rem;
            border-top:1px solid var(--line); }}
  @keyframes rise {{ from {{ opacity:0; transform:translateY(10px); }}
                     to {{ opacity:1; transform:none; }} }}
  @media (prefers-reduced-motion: reduce) {{ .card {{ animation:none; }} }}
  ::-webkit-scrollbar {{ width:10px; }}
  ::-webkit-scrollbar-thumb {{ background:var(--line); border-radius:8px; }}
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
