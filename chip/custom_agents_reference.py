# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyeg.
"""Model referensi verifikasi chip khusus per agent (jalur terpisah).

Terpisah dari 9 modul utama (`chip/reference.py`, 2612 vektor). Per chip:
`ok = req & (tag == ACC); match = (tag == ACC)`. Semua vektor exhaustif.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REG = ROOT / "chip" / "custom_agents.json"
RTL = ROOT / "chip" / "rtl"
LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"

_ALLOWED_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Name, ast.Load, ast.Constant,
    ast.BitAnd, ast.BitOr, ast.BitXor, ast.Invert, ast.USub, ast.UAdd,
    ast.Compare, ast.Eq,
)


def chip_name(agent: str) -> str:
    return "cd_" + re.sub(r"[^a-z0-9_]", "", agent.lower())


def reg_agents() -> list[dict[str, Any]]:
    import json
    return json.loads(REG.read_text(encoding="utf-8"))["agents"]


def parse_rtl(path: Path) -> tuple[str, list[tuple[str, str]]]:
    text = re.sub(r"//[^\n]*", "", path.read_text(encoding="utf-8"))
    m = re.search(r"module\s+(\w+)\s*\(([\s\S]*?)\)\s*;([\s\S]*?)endmodule", text, re.I)
    if not m:
        raise ValueError(f"modul tidak ditemukan: {path}")
    assigns = [(t, e.strip()) for t, e in
               re.findall(r"assign\s+(\w+)\s*=\s*([^;]+);", m.group(3))]
    return m.group(1), assigns


def _normalize_expr(expr: str) -> str:
    """Ubah literal Verilog `8'd100`/`8'b101`/`8'h1F` menjadi angka desimal."""
    def conv(m: "re.Match[str]") -> str:
        mode, digits = m.group(1), m.group(2)
        base = {"b": 2, "d": 10, "h": 16}.get(mode.strip(), 10)
        return str(int(digits, base))
    return re.sub(r"\d+'([d bh])([0-9a-fA-F]+)", conv, expr)


def eval_assign(expr: str, ctx: dict[str, int]) -> int:
    tree = ast.parse(_normalize_expr(expr), mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError(f"operator tidak diizinkan: {type(node).__name__}")
        if isinstance(node, ast.Name) and node.id not in ctx:
            raise ValueError(f"sinyal tidak dikenal: {node.id}")
    return int(eval(compile(tree, "<cd>", "eval"), {"__builtins__": {}}, ctx))


def verify_agent(agent: str) -> dict[str, Any]:
    entry = next((a for a in reg_agents() if a["agent"] == agent), None)
    if not entry:
        return {"agent": agent, "status": "MISSING"}
    chip = entry["chip"]
    acc = entry["acc"]
    _, assigns = parse_rtl(RTL / f"{chip}.v")
    mismatches: list[dict[str, Any]] = []
    vectors = 0
    for req in range(256):
        for tag in range(256):
            ctx = {"req": req & 1, "tag": tag}
            for target, expr in assigns:
                ctx[target] = eval_assign(expr, ctx)  # jangan mask ACC (8'd...)
            vectors += 1
            exp_ok = (req & 1) if tag == acc else 0
            exp_match = 1 if tag == acc else 0
            rtl_ok, rtl_match = ctx.get("ok", 0) & 1, ctx.get("match", 0) & 1
            if rtl_ok != exp_ok or rtl_match != exp_match:
                mismatches.append({"req": req & 1, "tag": tag,
                                   "rtl": (rtl_ok, rtl_match),
                                   "expected": (exp_ok, exp_match)})
    return {
        "agent": agent, "chip": chip, "acc": acc,
        "vectors": vectors, "mismatches": len(mismatches),
        "status": "PASS" if not mismatches else "FAIL",
        "details": mismatches[:3],
        "license": LICENSE, "owner": OWNER,
    }


def registry_fingerprint(entries: list[dict[str, Any]] | None = None) -> str:
    """Sidik registry agar cache otomatis basi bila entri agen ditambah/diubah."""
    rows = entries if entries is not None else reg_agents()
    payload = [(a["agent"], a["chip"], a["acc"]) for a in rows]
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]


def _verify_all_slow() -> dict[str, Any]:
    entries = reg_agents()
    results = [verify_agent(a["agent"]) for a in entries]
    ok = all(r["status"] == "PASS" for r in results)
    return {
        "status": "PASS" if ok else "FAIL",
        "agents": len(results), "vectors": sum(r["vectors"] for r in results),
        "results": results, "fabrication": "NOT_READY",
        "fingerprint": registry_fingerprint(entries),
        "license": LICENSE, "owner": OWNER,
        "cached": False,
    }


def verify_all(force: bool = False) -> dict[str, Any]:
    """Verifikasi semua chip khusus. Cache: bila berkas valid & 'PASS', kembalikan.

    Gunakan `force=True` / `--force` untuk re-verifikasi dari awal (4 menit).
    """
    if not force:
        cache = ROOT / "chip" / "reports" / "custom_agents_verify.json"
        try:
            data = json.loads(cache.read_text(encoding="utf-8"))
            if (data.get("status") == "PASS" and data.get("agents")
                    and data.get("fingerprint") == registry_fingerprint()):
                data["cached"] = True
                return data
        except (OSError, json.JSONDecodeError):
            pass
    out = _verify_all_slow()
    out["cached"] = False
    cache = ROOT / "chip" / "reports" / "custom_agents_verify.json"
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    print(json.dumps(verify_all(force=a.force), indent=2, ensure_ascii=False))
