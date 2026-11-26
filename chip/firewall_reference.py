# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Model referensi & verifikasi mandiri untuk RTL chip firewall.

Terpisah dari ``chip/reference.py`` agar 9 modul utama (2612 vektor,
5704 check, skor 100/100) tidak berubah. Parser di sini menerima teks RTL
sehingga mutation testing bisa berjalan tanpa menulis file sementara.
"""

from __future__ import annotations

import ast
import itertools
import re
from pathlib import Path
from typing import Any, Callable

RTL_DIR = Path(__file__).resolve().parent / "rtl"
LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"

_ALLOWED_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Name, ast.Load, ast.Constant,
    ast.BitAnd, ast.BitOr, ast.BitXor, ast.Invert, ast.Add, ast.Sub,
    ast.Mult, ast.LShift, ast.RShift, ast.USub, ast.UAdd,
)


def firewall_match(
    p0: int, p1: int, p2: int, p3: int,
    r0: int, r1: int, r2: int, r3: int, enable: int,
) -> dict[str, int]:
    hit = (
        (p0 == r0) & (p1 == r1) & (p2 == r2) & (p3 == r3) & bool(enable)
    )
    return {"hit": int(hit)}


def firewall_decide(
    p0: int, p1: int, p2: int, p3: int,
    d0: int, d1: int, d2: int, d3: int, deny_en: int,
    a0: int, a1: int, a2: int, a3: int, allow_en: int,
) -> dict[str, int]:
    deny = firewall_match(p0, p1, p2, p3, d0, d1, d2, d3, deny_en)["hit"]
    allow = firewall_match(p0, p1, p2, p3, a0, a1, a2, a3, allow_en)["hit"]
    return {"decision": int(allow and not deny)}


SPECS: dict[str, dict[str, Any]] = {
    "firewall_match": {
        "inputs": tuple((f"p{i}", 1) for i in range(4))
                  + tuple((f"r{i}", 1) for i in range(4))
                  + (("enable", 1),),
        "outputs": ("hit",),
        "model": firewall_match,
    },
    "firewall_decide": {
        "inputs": tuple((f"p{i}", 1) for i in range(4))
                  + tuple((f"d{i}", 1) for i in range(4))
                  + (("deny_en", 1),)
                  + tuple((f"a{i}", 1) for i in range(4))
                  + (("allow_en", 1),),
        "outputs": ("decision",),
        "model": firewall_decide,
    },
}


def _safe_eval(expression: str, ctx: dict[str, int]) -> int:
    tree = ast.parse(expression, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError(f"Operator tidak diizinkan: {type(node).__name__}")
        if isinstance(node, ast.Name) and node.id not in ctx:
            raise ValueError(f"Sinyal belum dikenal: {node.id}")
    return int(eval(compile(tree, "<firewall-rtl>", "eval"), {"__builtins__": {}}, ctx))


def parse_text(text: str) -> dict[str, Any]:
    clean = re.sub(r"//[^\n]*", "", text)
    match = re.search(
        r"module\s+([A-Za-z_]\w*)\s*\(([\s\S]*?)\)\s*;([\s\S]*?)endmodule",
        clean, re.I,
    )
    if not match:
        raise ValueError("Modul RTL tidak ditemukan")
    ports: list[dict[str, Any]] = []
    parts = re.split(r";|\s+(?=(?:input|output|inout)\b)", match.group(2), flags=re.I)
    for part in parts:
        part = part.strip().rstrip(",").strip()
        if not part:
            continue
        port = re.match(
            r"^(input|output|inout)\s*(?:\[\s*(\d+)\s*:\s*0\s*\])?\s*([\s\S]*)$",
            part, re.I,
        )
        if not port:
            raise ValueError(f"Deklarasi port tidak dikenali: {part}")
        width = int(port.group(2)) + 1 if port.group(2) else 1
        for raw in port.group(3).split(","):
            signal = re.sub(r"\[[^\]]*\]", "", raw).strip()
            if signal:
                ports.append({"name": signal, "dir": port.group(1).lower(), "width": width})
    assigns = [
        (target, expression.strip())
        for target, expression in re.findall(
            r"assign\s+([A-Za-z_]\w*)\s*=\s*([^;]+);", match.group(3), re.I
        )
    ]
    return {"name": match.group(1), "ports": ports, "assigns": assigns}


def load_rtl(name: str) -> str:
    return (RTL_DIR / f"{name}.v").read_text(encoding="utf-8")


def verify(name: str, rtl_text: str | None = None) -> dict[str, Any]:
    spec = SPECS[name]
    parsed = parse_text(rtl_text if rtl_text is not None else load_rtl(name))
    ranges = [range(1 << width) for _, width in spec["inputs"]]
    vectors = [
        {key: vals[i] for i, (key, _) in enumerate(spec["inputs"])}
        for vals in itertools.product(*ranges)
    ]
    mismatches: list[dict[str, Any]] = []
    for vec in vectors:
        ctx = dict(vec)
        for target, expression in parsed["assigns"]:
            # Target bisa berupa wire internal (bukan port) → default 1-bit.
            width = next(
                (p["width"] for p in parsed["ports"] if p["name"] == target), 1
            )
            mask = (1 << min(width, 31)) - 1
            ctx[target] = _safe_eval(expression, ctx) & mask
        expected = spec["model"](*(vec[key] for key, _ in spec["inputs"]))
        for output in spec["outputs"]:
            if ctx.get(output) != expected[output]:
                mismatches.append({"vector": vec, "output": output,
                                   "rtl": ctx.get(output), "expected": expected[output]})
                break
    return {
        "module": name,
        "vectors": len(vectors),
        "mismatches": len(mismatches),
        "status": "PASS" if not mismatches else "FAIL",
        "details": mismatches[:3],
        "license": LICENSE,
        "owner": OWNER,
    }
