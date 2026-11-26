# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Eksekusi otomatis untuk skill "sre-engineer" (replika IT Agenty dari
# jshsakura/awesome-opencode-skills, MIT © 2026 VoltAgent). Aturan kerja skill
# diterjemahkan ke pemeriksaan terukur; lihat docs/SRE-SKILL.md.
"""SRE watch: SLO/error budget dan triage sinyal dari laporan service-watch.

Berjalan sebagai proses supervisor. Tidak mengubah registry, lisensi, izin,
atau konfigurasi jaringan; hanya membaca laporan dan menulis laporan turunan.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SKILL = ROOT / ".github" / "skills" / "sre-engineer" / "SKILL.md"
WATCH_REPORT = ROOT / "system" / "reports" / "service_watch.json"
SRE_REPORT = ROOT / "system" / "reports" / "sre_watch.json"
HISTORY = ROOT / "system" / "reports" / "sre_history.jsonl"
DEFAULT_TARGET = 0.99
MAX_HISTORY = 200


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else default
    except (OSError, ValueError, TypeError):
        return default


def read_history(path: Path = HISTORY) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    entries: list[dict[str, Any]] = []
    for line in lines[-MAX_HISTORY:]:
        try:
            item = json.loads(line)
            if isinstance(item, dict):
                entries.append(item)
        except ValueError:
            continue
    return entries


def append_history(entry: dict[str, Any], path: Path = HISTORY) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    entries = read_history(path) + [entry]
    path.write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in entries[-MAX_HISTORY:]),
        encoding="utf-8",
    )


def assess(
    watch: dict[str, Any], history: list[dict[str, Any]], target: float = DEFAULT_TARGET
) -> dict[str, Any]:
    """Triage sinyal: apa yang terjadi, siapa pemiliknya, apa tindakan terkecil."""
    results = watch.get("results", [])
    # kind "monitor" hanya dipantau, bukan layanan yang dijalankan supervisor.
    # Memasukkannya ke denominator SLO akan mengubah noise jadi alarm palsu.
    targets = [
        item for item in results
        if isinstance(item, dict) and item.get("kind") != "monitor"
    ]
    informational = [
        {"name": item.get("name"), "status": item.get("status")}
        for item in results
        if isinstance(item, dict) and item.get("kind") == "monitor"
    ]
    total = len(targets) if targets else int(watch.get("total", 0) or 0)
    up = sum(1 for item in targets if item.get("status") == "UP")
    if not targets:
        up = int(watch.get("up", 0) or 0)
    availability = (up / total) if total else 0.0
    budget_minutes = round(max(0.0, 1.0 - target) * 1440, 1)
    consumed = round(max(0.0, 1.0 - availability) * 1440, 1)
    fraction = round(consumed / budget_minutes, 3) if budget_minutes else 0.0

    failing = [
        item for item in targets
        if item.get("status") in ("DOWN", "DEGRADED")
    ]
    baseline = [
        float(item["availability"]) for item in history
        if isinstance(item, dict) and isinstance(item.get("availability"), (int, float))
    ]
    if len(baseline) >= 3 and total:
        mean = statistics.fmean(baseline)
        spread = statistics.pstdev(baseline)
        regression = availability < mean - 2 * spread and (mean - availability) > 0.01
        signal = "REGRESI" if regression else "STABIL"
        baseline_detail = {"mean": round(mean, 4), "stdev": round(spread, 4),
                           "samples": len(baseline)}
    else:
        signal = "BELUM_CUKUP_DATA"
        baseline_detail = {"samples": len(baseline)}

    owners: dict[str, int] = {}
    for item in failing:
        kind = str(item.get("kind", "process"))
        area = {
            "http": "supervisor/http",
            "tcp": "network/port",
            "monitor": "network/port",
        }.get(kind, "process/runtime")
        owners[area] = owners.get(area, 0) + 1
    ranking = [
        {"area": area, "count": count,
         "confidence": round(count / len(failing), 3)}
        for area, count in sorted(owners.items(), key=lambda kv: -kv[1])
    ] if failing else []

    if fraction > 1:
        status = "WASPADA"
        recommendation = (
            "Error budget terlampaui. Evaluasi target SLO terhadap data nyata; "
            "jangan menaikkan target atau membuka layanan baru."
        )
    elif signal == "REGRESI":
        status = "WASPADA"
        recommendation = (
            "Terdeteksi penurunan availability di luar baseline. Periksa layanan "
            "yang gagal, lalu biarkan supervisor melakukan restart otomatis."
        )
    elif failing:
        status = "WASPADA"
        recommendation = (
            "Gagal terisolasi pada " + ", ".join(str(i.get("name")) for i in failing[:3])
            + ". Tindakan terkecil: verifikasi health endpoint, bukan ubah registry."
        )
    else:
        status = "SEHAT"
        recommendation = "Tidak ada tindakan; pertahankan konfigurasi yang ada."

    return {
        "checked_at": _now(),
        "source": "sre-watch",
        "skill": "sre-engineer (replika, MIT VoltAgent)",
        "skill_file": str(SKILL.relative_to(ROOT)),
        "target_availability": target,
        "availability": round(availability, 4),
        "error_budget": {
            "minutes_per_day": budget_minutes,
            "consumed_minutes": consumed,
            "fraction": fraction,
        },
        "signal": signal,
        "baseline": baseline_detail,
        "boundary": "system/services.json → service_watch.json → supervisor",
        "evidence": [str(item.get("name")) for item in failing],
        "informational": informational,
        "assumptions": [
            "health HTTP 200 dipakai sebagai proksi availability pengguna",
            "telemtri produksi nyata belum tersedia di workspace ini",
        ],
        "owner_ranking": ranking,
        "status": status,
        "recommendation": recommendation,
        "validation": {
            "normal_path": "semua layanan UP menurut service-watch" if not failing
                           else "tidak terpenuhi: " + ", ".join(str(i.get("name")) for i in failing[:3]),
            "failure_path": "satu layanan DOWN/DEGRADED terdeteksi" if failing
                            else "tidak diamati; butuh simulasi terarah",
            "recovery_path": "supervisor hot-reload + restart otomatis; rollback = service-remove",
        },
        "residual_risk": (
            "Tanpa telemetri produksi, korelasi belum dibuktikan sebagai kausalitas."
        ),
        "license": "Tom05ivier-commits-1.0",
    }


def run_once(
    watch_path: Path = WATCH_REPORT,
    report_path: Path = SRE_REPORT,
    history_path: Path = HISTORY,
    target: float = DEFAULT_TARGET,
    append: bool = True,
) -> dict[str, Any]:
    watch = _load_json(watch_path, {"total": 0, "up": 0, "results": []})
    history = read_history(history_path)
    report = assess(watch, history, target)
    if append:
        append_history(
            {"checked_at": report["checked_at"],
             "availability": report["availability"]},
            history_path,
        )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return report


def loop(interval: float = 60.0) -> None:
    while True:
        try:
            run_once()
        except Exception:
            pass
        time.sleep(max(5.0, interval))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sre_watch.py")
    parser.add_argument("command", choices=("once", "loop"), nargs="?", default="once")
    parser.add_argument("--target", type=float, default=DEFAULT_TARGET)
    parser.add_argument("--interval", type=float, default=60.0)
    args = parser.parse_args(argv)
    if args.command == "loop":
        loop(args.interval)
    else:
        print(json.dumps(run_once(target=args.target), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
