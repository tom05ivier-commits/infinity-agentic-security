# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Scorecard kualitas chip — 10 kriteria × 10 poin, dihitung dari bukti.

Nilai tidak pernah di-hardcode. Setiap kriteria membaca laporan atau berkas
yang dihasilkan jalur verifikasi nyata. Skor 100/100 hanya mungkin bila semua
bukti masih konsisten.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chip.reference import MODULES  # noqa: E402

CHIP = ROOT / "chip"
REPORTS = CHIP / "reports"
REPORT_PATH = REPORTS / "chip_score.json"
LICENSE_LINE = "SPDX-License-Identifier: Tom05ivier-commits-1.0"
LICENSE_ID = "Tom05ivier-commits-1.0"
OWNER_LINE = "Copyright (c) 2026 Tomi vier"


def _load(name: str) -> dict[str, Any]:
    """Baca bukti dengan retry singkat agar race penulisan daemon tidak
    menurunkan skor. Proses proteksi/supervisor dapat menimpa laporan saat
    scorecard dihitung; tanpa retry, pembacaan sesaat menghasilkan JSON
    kosong dan kriteria gagal walaupun bukti akhirnya valid."""
    path = REPORTS / name
    for attempt in range(3):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            if attempt == 2:
                raise
            time.sleep(0.1)
    return {}


def _result(passed: bool, detail: str) -> dict[str, Any]:
    return {"pass": bool(passed), "points": 10 if passed else 0, "detail": detail}


def check_license() -> dict[str, Any]:
    files = sorted((CHIP / "rtl").glob("*.v"))
    files += [
        CHIP / "reference.py",
        CHIP / "chip_cli.py",
        CHIP / "iverilog_check.py",
        CHIP / "synth_report.py",
        CHIP / "scorecard.py",
    ]
    files += sorted((CHIP / "tests").glob("test_*.py"))
    bad = [
        path.name
        for path in files
        if not path.exists()
        or not all(token in path.read_text(encoding="utf-8")[:800]
                   for token in (LICENSE_LINE, OWNER_LINE))
    ]
    return _result(not bad, f"{len(files)} berkas diperiksa; tanpa header: {bad or 'tidak ada'}")


def check_model() -> dict[str, Any]:
    report = _load("chip_verification.json")
    ok = (
        report.get("status") == "PASS"
        and report.get("modules") == len(MODULES)
        and report.get("vectors", 0) >= 2612
        and all(item.get("mismatches") == 0 for item in report.get("results", []))
    )
    return _result(ok, f"status={report.get('status')}, modul={report.get('modules')}, vektor={report.get('vectors')}")


def check_synthesis() -> dict[str, Any]:
    report = _load("chip_synthesis.json")
    modules = report.get("modules", [])
    netlists_ok = all(
        (CHIP / "synth" / f"{item['module']}_gate.v").exists()
        and (CHIP / "synth" / f"{item['module']}_netlist.json").exists()
        for item in modules
    )
    ok = (
        report.get("status") == "PASS"
        and len(modules) == len(MODULES)
        and report.get("total_cells", 0) > 0
        and all(item.get("gate_netlist") and item.get("json_netlist") for item in modules)
        and netlists_ok
    )
    return _result(ok, f"status={report.get('status')}, sel={report.get('total_cells')}, netlist={len(modules)}")


def check_iverilog() -> dict[str, Any]:
    report = _load("iverilog.json")
    vcd = report.get("vcd") or {}
    vcd_path = Path(vcd.get("path", "")) if isinstance(vcd, dict) else Path(str(vcd))
    ok = (
        report.get("status") == "PASS"
        and report.get("lint_warnings") == 0
        and report.get("compile_warnings") == 0
        and report.get("errors") == 0
        and report.get("checks", 0) >= 5704
        and len(report.get("modules", [])) == len(MODULES)
        and vcd_path.exists()
    )
    return _result(
        ok,
        f"status={report.get('status')}, checks={report.get('checks')}, "
        f"warning={report.get('lint_warnings')}/{report.get('compile_warnings')}, vcd={vcd_path.exists()}",
    )


def check_browser() -> dict[str, Any]:
    report = _load("browser_presets.json")
    presets = report.get("presets", [])
    errors = report.get("scopedErrors")
    external = (report.get("page") or {}).get("externalResources", [])
    ok = (
        report.get("status") == "PASS"
        and not errors
        and not external
        and len(presets) >= 4
        and all(item.get("pass") and item.get("mismatches") == 0 for item in presets)
    )
    return _result(
        ok,
        f"status={report.get('status')}, preset={len(presets)}, "
        f"error={len(errors) if errors is not None else 0}, eksternal={len(external)}",
    )


def check_testbench() -> dict[str, Any]:
    text = (CHIP / "tb" / "tb_chip.v").read_text(encoding="utf-8")
    missing = [name for name in MODULES if name not in text]
    ok = not missing and "initial begin" in text and "$finish" in text
    return _result(ok, f"modul terinstansi={len(MODULES) - len(missing)}/{len(MODULES)}")


def check_metadata() -> dict[str, Any]:
    data = json.loads((CHIP / "hy4_chip.json").read_text(encoding="utf-8"))
    names = {item.get("name") for item in data.get("modules", [])}
    expected = {
        "hy4_dot4", "hy4_quant", "hy4_top", "index_match4",
        "tom05_soc", "tom05_ai_accel",
    }
    ok = (
        data.get("model") == "opencode/hy4-flash-free"
        and data.get("license") == LICENSE_LINE.split(":")[1].strip()
        and names == expected
    )
    return _result(ok, f"model={data.get('model')}, modul={sorted(names)}")


def check_tests() -> dict[str, Any]:
    files = [CHIP / "tests" / f"test_{name}.py" for name in ("chip", "foundry", "tapeout")]
    ok = all(path.exists() and "unittest" in path.read_text(encoding="utf-8") for path in files)
    return _result(ok, f"berkas tes={sum(p.exists() for p in files)}/{len(files)}")


def check_docs() -> dict[str, Any]:
    text = (CHIP / "README.md").read_text(encoding="utf-8")
    needed = [f"`{name}`" for name in MODULES] + [
        "chip_cli.py verify", "chip_cli.py iverilog", "test_presets.sh", "chip-verify"
    ]
    missing = [token for token in needed if token not in text]
    return _result(not missing, f"dokumen lengkap; kurang={missing or 'tidak ada'}")


def check_privacy() -> dict[str, Any]:
    from security.privacy import release_ready

    report = release_ready(ROOT / "publish" / "infinity-agentic-security")
    ok = report.get("status") == "SIAP" and not report.get("findings") and not report.get("alasan")
    return _result(ok, f"rilis={report.get('status')}, temuan={len(report.get('findings', []))}")


CHECKS: tuple[tuple[str, str, Callable[[], dict[str, Any]]], ...] = (
    ("lisensi", "Header SPDX & copyright pada RTL/modul inti", check_license),
    ("model", "Verifikasi RTL terhadap model referensi", check_model),
    ("sintesis", "Sintesis gate-level & netlist", check_synthesis),
    ("iverilog", "Lint, kompilasi, vvp, dan waveform", check_iverilog),
    ("browser", "Preset simulator hy4 di browser", check_browser),
    ("testbench", "Cakupan seluruh modul di testbench", check_testbench),
    ("metadata", "Metadata hy4_chip.json", check_metadata),
    ("tes", "Berkas tes chip tersedia", check_tests),
    ("dokumentasi", "README memuat modul & cara verifikasi", check_docs),
    ("privasi", "Kesiapan rilis publik", check_privacy),
)


def build() -> dict[str, Any]:
    """Hitung skor 0–100 dari semua kriteria dan tulis laporan."""
    results = []
    for key, label, check in CHECKS:
        try:
            item = check()
        except Exception as exc:  # bukti rusak dianggap gagal, bukan crash
            item = _result(False, f"gagal membaca bukti: {type(exc).__name__}")
        results.append({"kriteria": key, "label": label, **item})

    score = sum(item["points"] for item in results)
    report = {
        "license": LICENSE_ID,
        "owner": "Tomi vier",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": "opencode/hy4-flash-free",
        "score": score,
        "maximum": 100,
        "status": "PERFECT" if score == 100 else "PARTIAL",
        "grade": "100/100" if score == 100 else f"{score}/100",
        "checks": results,
        "failed": [item["kriteria"] for item in results if not item["pass"]],
    }
    # Penulisan idempoten: jangan ubah berkas bila isi semantiknya sama.
    # `generated_at` sengaja tidak ikut dibandingkan karena bersifat volatil;
    # rewrite terus-menerus mengganti hash laporan dan membuat pemeriksaan
    # mirror (digest cermin) gagal saat gate dijalankan berurutan.
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if REPORT_PATH.exists():
        try:
            old = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
            old.pop("generated_at", None)
            current = {k: v for k, v in report.items() if k != "generated_at"}
            if old == current:
                return report
        except (OSError, json.JSONDecodeError):
            pass
    REPORTS.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(payload, encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, ensure_ascii=False))
