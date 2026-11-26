# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Peta koneksi supervisor <-> model opencode/tom05.

Supervisor menjaga *layanan* yang menyajikan model, bukan model sebagai
proses: opencode_server (8765), copilot_bridge (8766), dan tom05_provider
(8772). Semua identifier yang dipetakan di sini adalah alias/proxy pihak
ketiga; tidak ada klaim model terlatih baru tom05. Read-only, tanpa
kredensial; satu-satunya tulisan adalah laporan JSON di system/reports/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REPORT = ROOT / "system" / "reports" / "model_connectivity.json"
CATALOG = ROOT / "config" / "tom05-models.json"
FREE_CATALOG = ROOT / "config" / "hy4-free-models.json"
PROVIDER_CATALOG = ROOT / "config" / "tom05-provider-models.json"
OPENCODE_CONFIG = Path("/root/.config/opencode/opencode.json")

# Model yang disebut pemilik. Tidak ada ID "glm-5.3-flash-free" di katalog;
# yang dimaksud adalah alias proxied opencode/glm-5.3-flash dengan biaya nol.
NAMED: dict[str, dict[str, Any]] = {
    "tom05/tom05-flash-free": {
        "nama": "Tom05 flash Free",
        "endpoint": ["tom05_provider", "copilot_bridge"],
    },
    "opencode/hy4-flash-free": {
        "nama": "Hy4 flash Free",
        "endpoint": ["copilot_bridge", "opencode_server"],
    },
    "opencode/deepseek-v4.1-flash-free": {
        "nama": "DeepSeek V4.1 Flash Free",
        "endpoint": ["tom05_provider", "opencode_server"],
    },
    "opencode/glm-5.3-flash": {
        "nama": "GLM 5.3 Flash (alias proxied, biaya nol)",
        "endpoint": ["tom05_provider", "opencode_server"],
    },
    "opencode/tidepool-alpha-free": {
        "nama": "Tidepool Alpha Free",
        "endpoint": ["tom05_provider", "opencode_server"],
    },
}

ENDPOINT_LABEL = {
    "tom05_provider": "tom05-provider (8772)",
    "opencode_server": "server OpenCode (8765)",
    "copilot_bridge": "copilot-bridge (8766)",
}


def _read(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def collect_models() -> dict[str, dict[str, Any]]:
    """Gabungkan semua identifier opencode/tom05 dari katalog lokal."""
    models: dict[str, dict[str, Any]] = {}

    def add(model_id: str, source: str, **extra: Any) -> None:
        if not model_id:
            return
        entry = models.setdefault(model_id, {"id": model_id, "sumber": []})
        if source not in entry["sumber"]:
            entry["sumber"].append(source)
        entry.update(extra)

    catalog = _read(CATALOG)
    for item in catalog.get("models", []):
        if isinstance(item, dict) and item.get("id"):
            add(item["id"], "tom05-models", variants=item.get("variants", []))
    for item in catalog.get("aliases", []):
        if isinstance(item, dict) and item.get("target"):
            add(item["target"], "tom05-alias", alias=item.get("id"))
    for item in _read(FREE_CATALOG).get("models", []):
        if isinstance(item, dict) and item.get("id"):
            add(item["id"], "hy4-free-models")
    for item in _read(PROVIDER_CATALOG).get("models", []):
        if isinstance(item, dict) and item.get("id"):
            add(item["id"], "tom05-provider-models", proxied=bool(item.get("proxied")))

    for model_id, info in NAMED.items():
        add(model_id, "pemilik", nama=info["nama"], endpoint=list(info["endpoint"]))

    cost: dict[str, bool] = {}
    for section in _read(OPENCODE_CONFIG).get("providers", {}).values():
        if not isinstance(section, dict):
            continue
        for mid, entry in section.get("models", {}).items():
            if not isinstance(entry, dict):
                continue
            first = (entry.get("cost") or [{}])[0] or {}
            cache = first.get("cache") or {}
            cost[mid] = (
                all(first.get(k, 0) == 0 for k in ("input", "output"))
                and all(cache.get(k, 0) == 0 for k in ("read", "write"))
            )
    for mid, entry in models.items():
        if mid in cost:
            entry["gratis"] = cost[mid]
    return models


def _supervisor() -> dict[str, Any]:
    from system.supervisor import Supervisor

    return Supervisor().status()


def check() -> dict[str, Any]:
    """Bangun laporan konektivitas tanpa mengubah layanan."""
    from system.connection_status import check as connection_check

    koneksi = connection_check()
    endpoint = koneksi.get("endpoint", {})
    supervisor = _supervisor()
    models = collect_models()

    def status_for(model_id: str) -> dict[str, Any]:
        info = models.get(model_id, {})
        required = info.get("endpoint") or (
            ["tom05_provider", "copilot_bridge"]
            if model_id.startswith("tom05/")
            else ["tom05_provider", "opencode_server"]
        )
        rincian = {
            name: bool(endpoint.get(name, {}).get("terhubung")) for name in required
        }
        return {
            "id": model_id,
            "nama": info.get("nama", model_id),
            "gratis": info.get("gratis"),
            "endpoint": required,
            "rincian": rincian,
            "status": "TERHUBUNG" if all(rincian.values()) else "SEBAGIAN",
        }

    named = [status_for(mid) for mid in NAMED]
    semua_terhubung = all(item["status"] == "TERHUBUNG" for item in named)
    supervisor_ok = supervisor.get("supervisor-status") == "OK"
    aktif = [k for k, v in endpoint.items() if v.get("terhubung")]
    status = (
        "TERHUBUNG"
        if semua_terhubung and supervisor_ok and len(aktif) >= 3
        else "SEBAGIAN"
    )
    return {
        "status": status,
        "model": {
            "total": len(models),
            "gratis": sum(1 for m in models.values() if m.get("gratis")),
            "proxied": sum(1 for m in models.values() if m.get("proxied")),
        },
        "dinamai": named,
        "endpoint": {
            key: {
                "label": ENDPOINT_LABEL.get(key, key),
                "terhubung": bool(value.get("terhubung")),
            }
            for key, value in endpoint.items()
        },
        "supervisor": {
            "status": supervisor.get("supervisor-status"),
            "layanan": supervisor.get("layanan"),
            "hidup": supervisor.get("hidup"),
            "mati": supervisor.get("mati", []),
        },
        "catatan": (
            "Supervisor menjaga layanan yang menyajikan model; model adalah "
            "alias/proxy pihak ketiga, bukan model terlatih baru tom05. "
            "Pemeriksaan tanpa kredensial."
        ),
        "license": "Tom05ivier-commits-1.0",
    }


def write_report(data: dict[str, Any]) -> Path:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    tmp = REPORT.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(REPORT)
    return REPORT


if __name__ == "__main__":
    result = check()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    write_report(result)
