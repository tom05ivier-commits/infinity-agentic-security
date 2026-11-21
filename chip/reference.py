# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
# Model referensi chip (Python murni, bukan salinan kode simulator JS).

from __future__ import annotations

import ast
import itertools
import re
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent
RTL_DIR = ROOT / "rtl"
REPORT_DIR = ROOT / "reports"


def full_adder(a: int, b: int, cin: int) -> dict[str, int]:
    a, b, cin = a & 1, b & 1, cin & 1
    return {
        "sum": (a ^ b ^ cin) & 1,
        "cout": ((a & b) | (a & cin) | (b & cin)) & 1,
    }


def mux2(a: int, b: int, sel: int) -> dict[str, int]:
    return {"y": ((a & ~sel) | (b & sel)) & 1}


def decoder2(a: int, b: int) -> dict[str, int]:
    a, b = a & 1, b & 1
    return {
        "y0": (~a & ~b) & 1,
        "y1": (a & ~b) & 1,
        "y2": (~a & b) & 1,
        "y3": (a & b) & 1,
    }


def parity4(a: int, b: int, c: int, d: int) -> dict[str, int]:
    return {"odd": (a ^ b ^ c ^ d) & 1}


def alu4(a: int, b: int, op0: int, op1: int) -> dict[str, int]:
    op = (op0 & 1) | ((op1 & 1) << 1)
    if op == 0:
        value = a + b
    elif op == 1:
        value = a & b
    elif op == 2:
        value = a | b
    else:
        value = a ^ b
    return {"y": value & 0xF}


def hy4_dot4(a0: int, a1: int, a2: int, a3: int) -> dict[str, int]:
    """Model referensi penjumlahan berbobot untuk hy4."""
    return {"y": (a0 + 2 * a1 + 3 * a2 + 4 * a3) & 0xF}


def hy4_quant(score: int) -> dict[str, int]:
    """Model referensi kuantisasi skor hy4 menjadi dua bit."""
    return {"level": (score >> 2) & 0x3}


def hy4_top(a0: int, a1: int, a2: int, a3: int) -> dict[str, int]:
    """Model referensi inti akselerator hy4."""
    dot = (a0 + 2 * a1 + 3 * a2 + 4 * a3) & 0xF
    return {"level": (dot >> 2) & 0x3}


MODULES: dict[str, dict[str, Any]] = {
    "full_adder": {
        "inputs": (("a", 1), ("b", 1), ("cin", 1)),
        "outputs": ("sum", "cout"),
        "model": full_adder,
    },
    "mux2": {
        "inputs": (("a", 1), ("b", 1), ("sel", 1)),
        "outputs": ("y",),
        "model": mux2,
    },
    "decoder2": {
        "inputs": (("a", 1), ("b", 1)),
        "outputs": ("y0", "y1", "y2", "y3"),
        "model": decoder2,
    },
    "parity4": {
        "inputs": (("a", 1), ("b", 1), ("c", 1), ("d", 1)),
        "outputs": ("odd",),
        "model": parity4,
    },
    "alu4": {
        "inputs": (("a", 4), ("b", 4), ("op0", 1), ("op1", 1)),
        "outputs": ("y",),
        "model": alu4,
    },
    "hy4_dot4": {
        "inputs": (("a0", 2), ("a1", 2), ("a2", 2), ("a3", 2)),
        "outputs": ("y",),
        "model": hy4_dot4,
    },
    "hy4_quant": {
        "inputs": (("score", 4),),
        "outputs": ("level",),
        "model": hy4_quant,
    },
    "hy4_top": {
        "inputs": (("a0", 2), ("a1", 2), ("a2", 2), ("a3", 2)),
        "outputs": ("level",),
        "model": hy4_top,
    },
}

_ALLOWED_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Name, ast.Load, ast.Constant,
    ast.BitAnd, ast.BitOr, ast.BitXor, ast.Invert, ast.Add, ast.Sub,
    ast.Mult, ast.LShift, ast.RShift, ast.USub, ast.UAdd,
)


def _safe_eval(expression: str, ctx: dict[str, int]) -> int:
    """Evaluasi ekspresi RTL dengan AST whitelist."""
    tree = ast.parse(expression, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError(f"Operator tidak diizinkan: {type(node).__name__}")
        if isinstance(node, ast.Name) and node.id not in ctx:
            raise ValueError(f"Sinyal belum dikenal: {node.id}")
    return int(eval(compile(tree, "<rtl>", "eval"), {"__builtins__": {}}, ctx))


def parse_rtl(name: str) -> dict[str, Any]:
    """Urai subset Verilog: module, port input/output, dan assign."""
    path = RTL_DIR / f"{name}.v"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"//[^\n]*", "", text)
    match = re.search(
        r"module\s+([A-Za-z_]\w*)\s*\(([\s\S]*?)\)\s*;([\s\S]*?)endmodule",
        text,
        re.I,
    )
    if not match:
        raise ValueError(f"Modul {name} tidak ditemukan")
    ports: list[dict[str, Any]] = []
    parts = re.split(r";|\s+(?=(?:input|output|inout)\b)", match.group(2), flags=re.I)
    for part in parts:
        part = part.strip().rstrip(",").strip()
        if not part:
            continue
        port = re.match(
            r"^(input|output|inout)\s*(?:\[\s*(\d+)\s*:\s*0\s*\])?\s*([\s\S]*)$",
            part,
            re.I,
        )
        if not port:
            raise ValueError(f"Deklarasi port tidak dikenali: {part}")
        width = int(port.group(2)) + 1 if port.group(2) else 1
        for raw in port.group(3).split(","):
            signal = re.sub(r"\[[^\]]*\]", "", raw).strip()
            if signal:
                ports.append(
                    {"name": signal, "dir": port.group(1).lower(), "width": width}
                )
    assigns: list[tuple[str, str]] = []
    for target, expression in re.findall(
        r"assign\s+([A-Za-z_]\w*)\s*=\s*([^;]+);", match.group(3), re.I
    ):
        assigns.append((target, expression.strip()))
    return {"name": match.group(1), "ports": ports, "assigns": assigns}


def _vectors(inputs: tuple[tuple[str, int], ...]) -> list[dict[str, int]]:
    ranges = [range(1 << width) for _, width in inputs]
    return [
        {name: values[i] for i, (name, _) in enumerate(inputs)}
        for values in itertools.product(*ranges)
    ]


def verify_module(name: str) -> dict[str, Any]:
    """Bandingkan hasil RTL dengan model referensi untuk semua vektor."""
    spec = MODULES[name]
    rtl = parse_rtl(name)
    vector_list = _vectors(spec["inputs"])
    mismatches: list[dict[str, Any]] = []
    for vec in vector_list:
        ctx = dict(vec)
        for target, expression in rtl["assigns"]:
            width = next(
                p["width"] for p in rtl["ports"]
                if p["name"] == target
            )
            mask = (1 << min(width, 31)) - 1
            ctx[target] = _safe_eval(expression, ctx) & mask
        expected = spec["model"](*(vec[signal] for signal, _ in spec["inputs"]))
        for output in spec["outputs"]:
            if ctx.get(output) != expected[output]:
                mismatches.append(
                    {
                        "vector": vec,
                        "output": output,
                        "rtl": ctx.get(output),
                        "expected": expected[output],
                    }
                )
    return {
        "module": name,
        "vectors": len(vector_list),
        "mismatches": len(mismatches),
        "status": "PASS" if not mismatches else "FAIL",
        "details": mismatches[:5],
    }


def verify_all() -> dict[str, Any]:
    results = [verify_module(name) for name in MODULES]
    report = {
        "status": "PASS" if all(r["status"] == "PASS" for r in results) else "FAIL",
        "modules": len(results),
        "vectors": sum(r["vectors"] for r in results),
        "results": results,
        "license": "Tom05ivier-commits-1.0",
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "chip_verification.json").write_text(
        __import__("json").dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return report
