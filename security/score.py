# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Skor keamanan terpadu (0–100) berdasarkan kontrol yang dapat dibuktikan.

Skor mengukur **kontrol yang aktif & terverifikasi**, bukan menghilangkan
jejak serangan. `risiko_simulasi` dari kampanye red-team sengaja dilaporkan
terpisah: serangan yang terdeteksi adalah bukti pertahanan bekerja, bukan
penalti. Dengan demikian 100/100 berarti semua kontrol lolos, bukan berarti
tidak pernah ada simulasi serangan.

Tidak ada nilai kredensial yang pernah dimasukkan ke laporan.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

_WORKSPACE = Path(__file__).resolve().parents[1]
if str(_WORKSPACE) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE))

from security.auto_approval import AutoApproval  # noqa: E402
from security.blue.integrity import BASELINE_PATH, IntegrityMonitor  # noqa: E402
from security.clone_actions import CloneActions  # noqa: E402
from security.common.config import WORKSPACE  # noqa: E402
from security.privacy import release_ready  # noqa: E402

REPORT = WORKSPACE / "security" / "reports" / "security_score.json"
PUBLISH = (WORKSPACE / "publish" / "infinity-agentic-security", WORKSPACE / "publish" / "hy4-agent-model")

Control = Callable[[], tuple[bool, str]]


def _load_json(path: Path) -> dict[str, Any]:
    """Baca laporan JSON; tahan penulisan atomik yang sedang berlangsung."""
    for _ in range(3):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            time.sleep(0.2)
    return {}


def _load(name: str) -> dict[str, Any]:
    return _load_json(WORKSPACE / "security" / "reports" / name)


def control_verification() -> tuple[bool, str]:
    data = _load("verification.json")
    checks = data.get("checks", [])
    passed = sum(1 for c in checks if isinstance(c, dict) and c.get("status") == "PASS")
    failed = sum(1 for c in checks if isinstance(c, dict) and c.get("status") == "FAIL")
    summary = data.get("summary", {})
    # Ringkasan harus konsisten dengan butir bukti; tidak cukup mempercayai
    # satu field status yang bisa basi atau diubah.
    consistent = summary.get("pass") == passed and summary.get("fail") == failed
    ok = consistent and data.get("status") == "COMPLIANT" and failed == 0 and passed >= 11
    return ok, f"verify={data.get('status')}, pass={passed}/{len(checks)}, fail={failed}, konsisten={consistent}"


def control_efficacy() -> tuple[bool, str]:
    data = _load("efficacy.json")
    cycles = data.get("cycles", [])
    reported = float(data.get("skor_rata_rata", 0))
    computed = (
        round(sum(float(c.get("score", 0)) for c in cycles) / len(cycles), 1)
        if cycles
        else 0.0
    )
    consistent = bool(cycles) and abs(computed - reported) < 0.05
    complete = len(cycles) == data.get("expected_cycles", 3)
    ok = (
        consistent
        and complete
        and data.get("status") == "EFEKTIF"
        and reported >= 80
        and all(c.get("passed") == c.get("total") for c in cycles)
    )
    return ok, f"efikasi={data.get('status')}, rata-rata={reported}, dihitung={computed}, konsisten={consistent}"


def control_firewall() -> tuple[bool, str]:
    data = _load("firewall_drill.json")
    ok = data.get("status") == "BERHASIL" and not data.get("failed")
    return ok, f"drill={data.get('status')}, attempt={data.get('attempts')}"


def control_av_dlp() -> tuple[bool, str]:
    checks = _load("verification.json").get("checks", [])
    passed = {
        item.get("check")
        for item in checks
        if isinstance(item, dict) and item.get("status") == "PASS"
    }
    needed = {"deteksi antivirus", "pencegahan kebocoran data"}
    ok = needed.issubset(passed)
    return ok, ", ".join(sorted(needed & passed))


def control_privacy() -> tuple[bool, str]:
    statuses: list[str] = []
    ok = True
    for repo in PUBLISH:
        result = release_ready(repo) if repo.is_dir() else {"status": "PERLU TINDAKAN"}
        statuses.append(f"{repo.name}={result['status']}")
        ok = ok and result["status"] == "SIAP"
    return ok, "; ".join(statuses)


def control_api_key() -> tuple[bool, str]:
    from system.api_keygen import guard

    result = guard()
    detail = f"status={result['status']}, mode={result.get('mode')}, bocor={len(result.get('lokasi_bocor', []))}"
    return result.get("status") == "AMAN", detail


def control_auth_public() -> tuple[bool, str]:
    from system.hy4_auth import local_status, scan_public

    local, public = local_status(), scan_public()
    local_ok = bool(local["opencode_auth"] or local["env_api_key"])
    ok = local_ok and public["status"] == "AMAN"
    return ok, f"lokal={local_ok}, publik={public['status']} ({public['scanned_files']} file)"


def control_integrity() -> tuple[bool, str]:
    result = IntegrityMonitor().check()
    ok = BASELINE_PATH.exists() and result.get("total", 0) > 0
    return ok, f"baseline={BASELINE_PATH.exists()}, berkas={result.get('total')}"


def control_authorization() -> tuple[bool, str]:
    meta = AutoApproval().valid_meta
    clone = CloneActions().letter_valid
    return meta and clone, f"meta_izin={meta}, klon={clone}"


def control_chip() -> tuple[bool, str]:
    verification = _load_json(WORKSPACE / "chip" / "reports" / "chip_verification.json")
    synthesis = _load_json(WORKSPACE / "chip" / "reports" / "chip_synthesis.json")
    if not verification or not synthesis:
        return False, "laporan chip tidak dapat dibaca"
    ok = verification.get("status") == "PASS" and synthesis.get("status") == "PASS"
    return ok, f"verifikasi={verification.get('status')} ({verification.get('modules')} modul), sintesis={synthesis.get('status')}"


def control_secret_scan() -> tuple[bool, str]:
    script = WORKSPACE / "tools" / "secret_scan.py"
    if not script.exists():
        return False, "secret_scan.py tidak ada"
    try:
        result = subprocess.run(
            [sys.executable, str(script), str(WORKSPACE)],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.SubprocessError):
        return False, "pemindai gagal dijalankan"
    high = next((line for line in result.stdout.splitlines() if line.startswith("High:")), "High: ?")
    return result.returncode == 0, f"secret_scan rc={result.returncode}, {high}"


def control_incident() -> tuple[bool, str]:
    campaign = _load("campaign.json")
    ok = campaign.get("status") == "SELESAI" and bool(campaign.get("response"))
    return ok, f"campaign={campaign.get('status')}, respons={bool(campaign.get('response'))}"


CONTROLS: tuple[tuple[str, Control], ...] = (
    ("verifikasi kepatuhan", control_verification),
    ("efikasi pertahanan", control_efficacy),
    ("firewall & drill", control_firewall),
    ("antivirus & DLP", control_av_dlp),
    ("privasi rilis publik", control_privacy),
    ("kunci API aman", control_api_key),
    ("kerahasiaan kredensial", control_auth_public),
    ("integritas berkas", control_integrity),
    ("izin terbatas & diaudit", control_authorization),
    ("chip terverifikasi", control_chip),
    ("pemindaian rahasia", control_secret_scan),
    ("respons insiden", control_incident),
)


def summarize(controls: list[dict[str, Any]]) -> dict[str, Any]:
    """Hitung skor dari hasil kontrol. Fungsi murni untuk pengujian."""
    total = len(controls)
    passed = sum(1 for item in controls if item.get("status") == "LULUS")
    score = round(100 * passed / total, 1) if total else 0.0
    return {
        "skor": score,
        "passed": passed,
        "total": total,
        "status": "SEMPURNA" if passed == total else "PERLU PERBAIKAN",
    }


def evaluate() -> dict[str, Any]:
    """Jalankan seluruh kontrol dan tulis laporan skor keamanan."""
    results: list[dict[str, Any]] = []
    for name, check in CONTROLS:
        try:
            ok, evidence = check()
        except Exception as exc:  # noqa: BLE001 — kontrol gagal bukan pengecualian fatal
            ok, evidence = False, f"kesalahan kontrol: {type(exc).__name__}"
        results.append(
            {
                "kontrol": name,
                "status": "LULUS" if ok else "GAGAL",
                "bukti": evidence,
            }
        )

    summary = summarize(results)
    efficacy = _load("efficacy.json")
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "owner": "Tomi vier",
        "license": "Tom05ivier-commits-1.0",
        "skor_keamanan": f"{summary['skor']:.0f}/100",
        "risiko_simulasi": efficacy.get("risk_score", 0),
        "catatan_risiko": "Risiko dari serangan simulasi yang berhasil terdeteksi; bukan penalti kontrol.",
        "summary": summary,
        "controls": results,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    report["report"] = str(REPORT)
    return report


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Skor keamanan terpadu 0–100")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    data = evaluate()
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"Skor keamanan: {data['skor_keamanan']} — {data['summary']['status']}")
        for item in data["controls"]:
            print(f"  [{item['status']}] {item['kontrol']}: {item['bukti']}")
        print(f"Risiko simulasi: {data['risiko_simulasi']} (informasional)")
    # Berfungsi sebagai gate: kode 1 bila skor turun dari 100/100.
    return 0 if data["summary"]["status"] == "SEMPURNA" else 1


if __name__ == "__main__":
    sys.exit(main())
