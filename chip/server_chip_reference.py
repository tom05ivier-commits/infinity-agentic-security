# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Model referensi & verifikasi untuk chip server localhost.

Terpisah dari `chip/reference.py` (9 modul utama, 2612 vektor) agar skor
100/100 tidak berubah. RTL dihasilkan oleh `chip/server_chip_gen.py`.
"""

from __future__ import annotations

import ast
import itertools
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
RTL = ROOT / "chip" / "rtl"
LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"
ALLOWED_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Name, ast.Load, ast.Constant,
    ast.BitAnd, ast.BitOr, ast.BitXor, ast.Invert,
)


def gate(alive: int, healthy: int, enabled: int) -> dict[str, int]:
    alive, healthy, enabled = alive & 1, healthy & 1, enabled & 1
    return {
        "ready": alive & healthy & enabled,
        "degraded": alive & enabled & (healthy ^ 1),
        "blocked": (alive ^ 1) | (enabled ^ 1),
    }


def _safe_eval(expr: str, ctx: dict[str, int]) -> int:
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED_NODES):
            raise ValueError(f"Operator tidak diizinkan: {type(node).__name__}")
        if isinstance(node, ast.Name) and node.id not in ctx:
            raise ValueError(f"Sinyal belum dikenal: {node.id}")
    return int(eval(compile(tree, "<srv-rtl>", "eval"), {"__builtins__": {}}, ctx))


def parse(path: Path) -> tuple[str, list[tuple[str, str]]]:
    text = re.sub(r"//[^\n]*", "", path.read_text(encoding="utf-8"))
    match = re.search(r"module\s+srv_(\w+)\s*\(([\s\S]*?)\)\s*;([\s\S]*?)endmodule", text, re.I)
    if not match:
        raise ValueError(f"Modul tidak ditemukan: {path}")
    assigns = [
        (t, e.strip()) for t, e in re.findall(r"assign\s+(\w+)\s*=\s*([^;]+);", match.group(3))
    ]
    return match.group(1), assigns


def specs() -> list[dict[str, Any]]:
    from chip.server_chip_gen import servers
    return servers()


def verify_all() -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    vectors = 0
    for s in specs():
        path = RTL / f"srv_{s['sig']}.v"
        name, assigns = parse(path)
        mismatches: list[dict[str, Any]] = []
        count = 0
        for alive, healthy, enabled in itertools.product((0, 1), repeat=3):
            ctx = {"alive": alive, "healthy": healthy, "enabled": enabled}
            for target, expr in assigns:
                ctx[target] = _safe_eval(expr, ctx) & 1
            expected = gate(alive, healthy, enabled)
            for out in ("ready", "degraded", "blocked"):
                if ctx.get(out) != expected[out]:
                    mismatches.append({"in": dict(ctx), "out": out,
                                       "rtl": ctx.get(out), "expected": expected[out]})
            count += 1
        vectors += count
        results.append({"server": s["name"], "module": f"srv_{name}",
                        "kind": s["kind"], "port": s["port"],
                        "vectors": count, "mismatches": len(mismatches),
                        "status": "PASS" if not mismatches else "FAIL",
                        "details": mismatches[:3]})
    return {
        "status": "PASS" if all(r["status"] == "PASS" for r in results) else "FAIL",
        "servers": len(results), "vectors": vectors, "results": results,
        "license": LICENSE, "owner": OWNER, "fabrication": "NOT_READY",
    }


if __name__ == "__main__":
    print(json.dumps(verify_all(), indent=2, ensure_ascii=False))
