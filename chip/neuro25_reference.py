# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Model referensi dan verifikasi RTL untuk chip simulasi NEURO-25.

NEURO-25 memproses **vektor sintetis** yang merepresentasikan empat tahap
kognitif. Tidak ada data dari otak manusia sungguhan, tidak ada elektroda,
tidak ada stimulasi, dan tidak ada koneksi ke subjek hidup. Profil usia
~25 tahun hanya berupa konstanta gain simulasi, bukan ukuran biologis.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from chip.reference import _safe_eval, _vectors, parse_rtl  # noqa: E402

MODULE = "tom05_neuro25"
REPORT = ROOT / "reports" / "neuro25_verification.json"
INPUTS: tuple[tuple[str, int], ...] = (
    ("n0", 2), ("n1", 2), ("n2", 2), ("n3", 2),
    ("mem", 2), ("intent", 2), ("gate", 1),
)
OUTPUTS: tuple[str, ...] = ("decision", "stage", "act", "blocked", "irq", "ready")
PROFILE_AGE_REFERENCE_YEARS = 25
PROFILE_GAIN = 2


def neuro25(
    n0: int, n1: int, n2: int, n3: int,
    mem: int, intent: int, gate: int,
) -> dict[str, int]:
    """Model referensi empat tahap kognitif dengan consent gate."""
    sense = (n0 + (2 * n1) + (3 * n2) + (4 * n3)) & 31
    memory_w = (sense + (PROFILE_GAIN * mem)) & 31
    plan_w = (memory_w + (PROFILE_GAIN * intent)) & 31
    decision = plan_w & 31
    stage = intent & 3
    actionable = (intent >> 1) & 1
    stage_is_action = (stage & 1) & ((stage >> 1) & 1)
    high = (decision >> 3) & 1
    act = high & (gate & 1) & actionable
    blocked = high & ((gate ^ 1) & 1) & actionable
    irq = blocked & stage_is_action
    return {
        "decision": decision,
        "stage": stage,
        "act": act,
        "blocked": blocked,
        "irq": irq,
        "ready": 1,
    }


def verify() -> dict[str, Any]:
    """Bandingkan RTL dengan model untuk seluruh 8192 vektor."""
    rtl = parse_rtl(MODULE)
    widths = {item["name"]: item["width"] for item in rtl["ports"]}
    widths.update(rtl.get("wires", {}))
    vectors = _vectors(INPUTS)
    mismatches: list[dict[str, Any]] = []
    for vector in vectors:
        ctx = dict(vector)
        for target, expression in rtl["assigns"]:
            if target not in widths:
                raise ValueError(f"Sinyal {target} tidak dideklarasikan di {MODULE}")
            mask = (1 << min(widths[target], 31)) - 1
            ctx[target] = _safe_eval(expression, ctx) & mask
        expected = neuro25(*(vector[name] for name, _ in INPUTS))
        for output in OUTPUTS:
            if ctx.get(output) != expected[output]:
                mismatches.append({
                    "vector": vector,
                    "output": output,
                    "rtl": ctx.get(output),
                    "expected": expected[output],
                })
    report: dict[str, Any] = {
        "module": MODULE,
        "status": "PASS" if not mismatches else "FAIL",
        "vectors": len(vectors),
        "mismatches": len(mismatches),
        "details": mismatches[:5],
        "outputs": list(OUTPUTS),
        "profile": {
            "age_reference_years": PROFILE_AGE_REFERENCE_YEARS,
            "gain": PROFILE_GAIN,
            "kind": "synthetic-adult-reference",
        },
        "subject_data": False,
        "license": "Tom05ivier-commits-1.0",
        "owner": "Tomi vier",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, ensure_ascii=False))
