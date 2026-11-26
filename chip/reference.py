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


def index_match4(q: int, k: int) -> dict[str, int]:
    """Model referensi irisan masker 4-bit untuk indeks data aman.

    ``score`` adalah popcount dari ``q & k`` — padanan hardware dari
    ``len(terms & haystack)`` pada ``tools/safe_data_index.py::search``.
    """
    overlap = (q & k) & 0xF
    return {"score": sum((overlap >> bit) & 1 for bit in range(4)) & 0x7}


def tom05_soc(
    cam0: int, cam1: int, cam2: int, cam3: int, mode: int, irq_clear: int
) -> dict[str, int]:
    """Model referensi SoC tom05 untuk smartphone Android.

    Empat jalur sensor 2-bit difusikan dengan bobot hy4, ditambah bias
    konteks `mode`, lalu dikuantisasi. Interrupt aktif bila level tinggi
    dan belum di-clear; `ready` selalu 1 (jalur kombinasional).
    """
    score = (cam0 + 2 * cam1 + 3 * cam2 + 4 * cam3 + mode) & 0xF
    level = (score >> 2) & 0x3
    irq = (((level >> 1) & 1) & (irq_clear ^ 1)) & 1
    return {"score": score, "level": level, "irq": irq, "ready": 1}


def tom05_ai_accel(
    a0: int, a1: int, a2: int, a3: int, mode: int, irq_clear: int
) -> dict[str, int]:
    """Model referensi akselerator AI tom05 (TAI-1).

    Empat jalur aktivasi 2-bit diproses memakai empat profil arsitektur yang
    dipilih `mode` (tanpa bit-select agar tetap cocok dengan subset simulator
    browser): TENSOR (GPU/TPU-like), LPU (stream deterministik), NEARMEM
    (komputasi dekat SRAM), dan MESH (reduksi wafer-scale).

    `hit` menandakan residensi data di memori lokal (bit tinggi aktivasi),
    `score` 5-bit menampung keluaran dot product maksimal 30, `level` adalah
    kuantisasi 2-bit, dan `irq` aktif pada level tinggi yang belum di-clear.
    """
    m0 = mode & 1
    m1 = (mode >> 1) & 1
    hit = (
        ((a0 >> 1) & 1) | ((a1 >> 1) & 1)
        | ((a2 >> 1) & 1) | ((a3 >> 1) & 1)
    ) & 1
    d_tensor = (a0 + 2 * a1 + 3 * a2 + 4 * a3) & 0x1F
    d_lpu = (4 * a0 + 3 * a1 + 2 * a2 + a3) & 0x1F
    d_near_hit = (2 * a0 + 2 * a1 + a2 + a3) & 0x1F
    d_near_miss = (a0 + a1 + 2 * a2 + 2 * a3) & 0x1F
    d_near = (((1 - hit) * d_near_miss) + (hit * d_near_hit)) & 0x1F
    d_mesh = (2 * (a0 + a1 + a2 + a3)) & 0x1F
    score = (
        ((1 - m0) & (1 - m1)) * d_tensor
        + (m0 & (1 - m1)) * d_lpu
        + ((1 - m0) & m1) * d_near
        + (m0 & m1) * d_mesh
    ) & 0x1F
    level = (score >> 3) & 0x3
    irq = (((level >> 1) & 1) & (irq_clear ^ 1)) & 1
    return {"score": score, "level": level, "hit": hit, "irq": irq, "ready": 1}


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
    "index_match4": {
        "inputs": (("q", 4), ("k", 4)),
        "outputs": ("score",),
        "model": index_match4,
    },
    "tom05_soc": {
        "inputs": (
            ("cam0", 2), ("cam1", 2), ("cam2", 2), ("cam3", 2),
            ("mode", 1), ("irq_clear", 1),
        ),
        "outputs": ("score", "level", "irq", "ready"),
        "model": tom05_soc,
    },
    "tom05_ai_accel": {
        "inputs": (
            ("a0", 2), ("a1", 2), ("a2", 2), ("a3", 2),
            ("mode", 2), ("irq_clear", 1),
        ),
        "outputs": ("score", "level", "hit", "irq", "ready"),
        "model": tom05_ai_accel,
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
    wires: dict[str, int] = {}
    for width_text, names in re.findall(
        r"\bwire\s+(?:\[\s*(\d+)\s*:\s*0\s*\]\s+)?([A-Za-z_][\w\s,]*)\s*;",
        match.group(3),
        re.I,
    ):
        width = int(width_text) + 1 if width_text else 1
        for raw_name in names.split(","):
            signal = raw_name.strip()
            if signal:
                wires[signal] = width

    assigns: list[tuple[str, str]] = []
    for target, expression in re.findall(
        r"assign\s+([A-Za-z_]\w*)\s*=\s*([^;]+);", match.group(3), re.I
    ):
        # ekspresi boleh wrap ke beberapa baris; ratakan agar ast.parse
        # tidak melihat indentasi sebagai blok Python.
        assigns.append((target, " ".join(expression.split())))
    return {
        "name": match.group(1),
        "ports": ports,
        "wires": wires,
        "assigns": assigns,
    }


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
    widths = {p["name"]: p["width"] for p in rtl["ports"]}
    widths.update(rtl.get("wires", {}))
    vector_list = _vectors(spec["inputs"])
    mismatches: list[dict[str, Any]] = []
    for vec in vector_list:
        ctx = dict(vec)
        for target, expression in rtl["assigns"]:
            if target not in widths:
                raise ValueError(f"Sinyal {target} tidak dideklarasikan di {name}")
            width = widths[target]
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
