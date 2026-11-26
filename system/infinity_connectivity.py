# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.1 — lihat file LICENSE di root proyek.
"""Peta konektivitas supervisor <-> seluruh komponen workspace IT Agenty Infinity.

Supervisor adalah pusat orkestrasi dari `system/services.json`. Modul ini
memetakan semua layanan yang dijalankan supervisor dan semua subsistem
workspace (chip, security, agent, dataset, platform, container, device, dan
sebagainya) ke dalam satu graph: simpul = komponen, sisi = koneksi lewat
registry, sumber data bersama `/root/workspace`, atau relai chat.

Bersifat read-only: hanya membaca registry, heartbeat, PID, dan laporan JSON.
Tidak ada kredensial yang dibaca/dicetak; satu-satunya tulisan adalah laporan
`system/reports/infinity_connectivity.json`.
"""

from __future__ import annotations

import json
import os
import sys
from collections import deque
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REGISTRY = ROOT / "system" / "services.json"
HEARTBEAT = ROOT / "system" / "reports" / "heartbeat.json"
PID_DIR = ROOT / "system" / "reports" / "supervisor-pids"
REPORT = ROOT / "system" / "reports" / "infinity_connectivity.json"

from system.supervisor import http_alive, pid_alive, port_open  # noqa: E402

# Setiap komponen punya sumber (path) yang harus ada di workspace. `service`
# menghubungkannya ke entri registry (artinya dijaga supervisor). `links`
# adalah sisi antarkomponen selain lewat sumber data bersama.
COMPONENTS: tuple[dict[str, Any], ...] = (
    {"name": "supervisor", "path": "system/supervisor.py", "kind": "core",
     "service": None, "role": "pusat orkestrasi registry"},
    {"name": "workspace", "path": ".", "kind": "data", "service": None,
     "role": "sumber kebenaran tunggal semua data bersama"},
    {"name": "server", "path": "system/cli.py", "kind": "server",
     "service": "server", "role": "server OpenCode + dashboard", "links": ["workspace"]},
    {"name": "protection", "path": "system/protection.py", "kind": "process",
     "service": "protection", "role": "perlindungan berkelanjutan", "links": ["security"]},
    {"name": "bridge", "path": "copilot-bridge/bridge.py", "kind": "server",
     "service": "bridge", "role": "bridge Copilot CLI ke model", "links": ["tom05-provider", "tom05-cli"]},
    {"name": "files", "path": "system/fileserver.py", "kind": "server",
     "service": "files", "role": "layanan berkas lokal", "links": ["workspace"]},
    {"name": "public", "path": "system/public_server.py", "kind": "server",
     "service": "public", "role": "server publik dengan Basic Auth", "links": ["server"]},
    {"name": "tunnel", "path": "system/tunnel.sh", "kind": "process",
     "service": "tunnel", "role": "tunnel opsional", "links": ["public"]},
    {"name": "workflow", "path": "security/workflow-daemon.sh", "kind": "process",
     "service": "workflow", "role": "daemon workflow keamanan", "links": ["security"]},
    {"name": "sites", "path": "site/server.py", "kind": "server",
     "service": "sites", "role": "hub situs statis & simulator chip", "links": ["chip", "mirror"]},
    {"name": "mirror", "path": "site/mirror_server.py", "kind": "server",
     "service": "mirror", "role": "cermin aplikasi tersanitasi", "links": ["publish"]},
    {"name": "community", "path": "site/community/server.py", "kind": "server",
     "service": "community", "role": "portal komunitas IT Agenty", "links": ["symphony"]},
    {"name": "symphony", "path": "scripts/symphony-deploy.sh", "kind": "process",
     "service": "symphony", "role": "orkestrasi symphony", "links": ["community"]},
    {"name": "tom05-provider", "path": "system/tom05_provider.py", "kind": "server",
     "service": "tom05-provider", "role": "provider OpenAI-compatible tom05",
     "links": ["tom05-selfhost", "bridge", "model"]},
    {"name": "port-14713", "path": "config/tom05-connections.json", "kind": "monitor",
     "service": "port-14713", "role": "kandidat koneksi yang hanya dipantau"},
    {"name": "chat-dispatch", "path": "system/chat_dispatch.py", "kind": "process",
     "service": "chat-dispatch", "role": "relai chat ke responder lokal",
     "links": ["agent", "advanced", "chip", "security", "dataset", "platform", "system"]},
    {"name": "tom05-selfhost", "path": "system/tom05_selfhost.py", "kind": "server",
     "service": "tom05-selfhost", "role": "model self-host + retrieval", "links": ["knowledge"]},
    {"name": "service-watch", "path": "system/service_watch.py", "kind": "server",
     "service": "service-watch", "role": "watchdog layanan", "links": ["sre-watch"]},
    {"name": "sre-watch", "path": "system/sre_watch.py", "kind": "process",
     "service": "sre-watch", "role": "SLO/error budget & triage", "links": ["service-watch"]},
    {"name": "ai-chip", "path": "system/ai_chip_service.py", "kind": "server",
     "service": "ai-chip", "role": "status chip AI TAI-1 read-only",
     "links": ["chip", "sites"]},
    {"name": "ai-chip-watch", "path": "chip/chip_watch.py", "kind": "process",
     "service": "ai-chip-watch", "role": "watchdog verifikasi chip AI TAI-1",
     "links": ["chip", "service-watch"]},
    {"name": "domain", "path": "system/domain_service.py", "kind": "server",
     "service": "domain", "role": "generator domain gratis & subdomain lokal",
     "links": ["sites", "workspace"]},
    {"name": "permission-watch", "path": "security/permission_watch.py", "kind": "process",
     "service": "permission-watch", "role": "pemeriksa kedaluwarsa izin tertulis",
     "links": ["security", "workspace"]},
    {"name": "cloud-code", "path": "system/cloud_code_service.py", "kind": "server",
     "service": "cloud-code", "role": "status alat Cloud Code read-only",
     "links": ["workspace", "system"]},
    {"name": "opencode", "path": "system/opencode_service.md", "kind": "server",
     "service": "opencode", "role": "server API OpenCode read-only di supervisor",
     "links": ["workspace", "system"]},
    {"name": "opencode-42337", "path": "scripts/opencode_serve.sh", "kind": "server",
     "service": "opencode-42337", "role": "instansi OpenCode tambahan yang diawasi supervisor",
     "links": ["workspace", "system"]},
    {"name": "opencode-watch", "path": "system/opencode_watch.py", "kind": "cli",
     "service": "opencode-watch", "role": "watchdog server OpenCode ephemeral di luar registry",
     "links": ["workspace", "system"]},
    {"name": "cognitive-brain", "path": "system/cognitive_brain.py", "kind": "core",
     "service": None, "role": "pemetaan indra->memori->rencana->aksi di supervisor",
     "links": ["supervisor", "advanced", "agent", "knowledge", "chat-dispatch",
               "dataset", "device"]},
    {"name": "neuro25-chip", "path": "chip/rtl/tom05_neuro25.v", "kind": "data",
     "service": None, "role": "chip simulasi NEURO-25 (bukan alat medis)",
     "links": ["cognitive-brain", "advanced", "chip"]},
    {"name": "taste-knowledge", "path": "system/taste_knowledge.py", "kind": "data",
     "service": None, "role": "pengetahuan rasa simbolik pada indra (bukan sensor)",
     "links": ["cognitive-brain", "workspace"]},
    {"name": "rights-balance", "path": "system/rights_balance.py", "kind": "core",
     "service": None, "role": "latar keseimbangan kepentingan dan hak",
     "links": ["cognitive-brain", "security", "workspace"]},
    {"name": "system", "path": "system", "kind": "cli", "service": None,
     "role": "CLI komputer sistem", "links": ["workspace", "dashboard"]},
    {"name": "dashboard", "path": "dashboard.html", "kind": "data", "service": None,
     "role": "tampilan status & skor", "links": ["server"]},
    {"name": "security", "path": "security", "kind": "cli", "service": None,
     "role": "antivirus, firewall, DLP, SOC, red-team", "links": ["workspace", "chip"]},
    {"name": "chip", "path": "chip", "kind": "cli", "service": None,
     "role": "RTL, verifikasi, dan scorecard chip", "links": ["sites", "security"]},
    {"name": "agent", "path": "agent", "kind": "cli", "service": None,
     "role": "agen otonom", "links": ["chat-dispatch"]},
    {"name": "advanced", "path": "advanced", "kind": "cli", "service": None,
     "role": "advanced computer", "links": ["chat-dispatch"]},
    {"name": "dataset", "path": "dataset", "kind": "data", "service": None,
     "role": "dataset instruksi→jawaban terverifikasi", "links": ["chat-dispatch", "security"]},
    {"name": "platform", "path": "platform_clis", "kind": "cli", "service": None,
     "role": "scorecard CLI platform engineering", "links": ["chat-dispatch"]},
    {"name": "container", "path": "Dockerfile.tom05", "kind": "data", "service": None,
     "role": "container hardened & SoC", "links": ["chat-dispatch", "tom05-provider"]},
    {"name": "device", "path": "docs/HARDWARE-AGENT.md", "kind": "data", "service": None,
     "role": "integrasi perangkat Android", "links": ["system"]},
    {"name": "knowledge", "path": "system/tom05_knowledge.py", "kind": "data",
     "service": None, "role": "retrieval pengetahuan workspace", "links": ["workspace"]},
    {"name": "model", "path": "config/tom05-models.json", "kind": "data", "service": None,
     "role": "katalog & alias model (proxied)", "links": ["tom05-provider", "bridge"]},
    {"name": "tom05-cli", "path": "tom05", "kind": "cli", "service": None,
     "role": "CLI kanonik tom05", "links": ["bridge", "chat-dispatch"]},
    {"name": "publish", "path": "publish", "kind": "data", "service": None,
     "role": "cermin rilis tersanitasi", "links": ["mirror", "workspace"]},
    {"name": "mcp", "path": "config/tom05-connections.json", "kind": "mcp",
     "service": None, "role": "server MCP dengan scope workspace", "links": ["workspace"]},
)

DISABLE_FLAGS = {
    "public": "AGENTY_DISABLE_PUBLIC",
    "tunnel": "AGENTY_DISABLE_TUNNEL",
}
REPORT_SOURCES = (
    ("model_connectivity", ROOT / "system" / "reports" / "model_connectivity.json"),
    ("service_watch", ROOT / "system" / "reports" / "service_watch.json"),
    ("sre_watch", ROOT / "system" / "reports" / "sre_watch.json"),
    ("security_score", ROOT / "security" / "reports" / "security_score.json"),
    ("chip_score", ROOT / "chip" / "reports" / "chip_score.json"),
    ("tom05_score", ROOT / "system" / "reports" / "tom05_score.json"),
    ("device_score", ROOT / "system" / "reports" / "device_score.json"),
    ("container_score", ROOT / "system" / "reports" / "container_score.json"),
)


def _read(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def registry() -> list[dict[str, Any]]:
    return _read(REGISTRY).get("services", [])


def _pid_for(name: str, heartbeat: dict[str, Any]) -> int | None:
    path = PID_DIR / f"{name}.pid"
    data = _read(path)
    pid = data.get("pid")
    if not isinstance(pid, int) or not pid_alive(pid):
        info = heartbeat.get("services", {}).get(name, {})
        pid = info.get("pid") if isinstance(info, dict) else None
    return pid if isinstance(pid, int) and pid_alive(pid) else None


def _probe_http(port: int, path: str, heartbeat_alive: bool) -> bool:
    """Beberapa percobaan + heartbeat agar beban sesaat tidak jadi alarm palsu."""
    for attempt in range(3):
        if http_alive(port, path):
            return True
        if attempt < 2:
            import time

            time.sleep(0.2)
    return heartbeat_alive


def service_status(item: dict[str, Any], heartbeat: dict[str, Any]) -> dict[str, Any]:
    """Probe satu layanan tanpa mengubahnya."""
    name = str(item.get("name", ""))
    kind = str(item.get("kind", "process"))
    flag = DISABLE_FLAGS.get(name)
    disabled = bool(flag and os.environ.get(flag) == "1")
    port = item.get("port")
    info = heartbeat.get("services", {}).get(name, {})
    recorded = bool(info.get("alive")) if isinstance(info, dict) else False
    if kind in ("monitor", "tcp"):
        alive = port_open(int(port or 0))
        mode = "dipantau"
    elif disabled:
        alive = False
        mode = "dinonaktifkan"
    elif kind == "http":
        alive = _probe_http(int(port or 0), str(item.get("health", "/")), recorded)
        mode = "dijalankan"
    else:
        pid = _pid_for(name, heartbeat)
        alive = pid is not None
        mode = "dijalankan"
    return {
        "nama": name, "kind": kind, "port": port, "mode": mode,
        "hidup": alive, "pid": _pid_for(name, heartbeat) if kind == "process" else None,
        "dihitung": kind not in ("monitor", "tcp") and not disabled,
    }


def build_graph() -> dict[str, Any]:
    """Susun simpul & sisi graph konektivitas (undirected)."""
    edges: set[tuple[str, str]] = set()
    names = {item["name"] for item in COMPONENTS}

    def edge(a: str, b: str) -> None:
        if a in names and b in names and a != b:
            edges.add(tuple(sorted((a, b))))

    for item in COMPONENTS:
        if item["name"] != "workspace":
            edge(item["name"], "workspace")
        for target in item.get("links", []):
            edge(item["name"], target)

    registered = {item.get("name") for item in registry()}
    for item in COMPONENTS:
        service = item.get("service")
        if service and service in registered:
            edge("supervisor", item["name"])

    adjacency: dict[str, set[str]] = {name: set() for name in names}
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)

    seen = {"supervisor"}
    queue = deque(["supervisor"])
    while queue:
        for neighbour in adjacency[queue.popleft()]:
            if neighbour not in seen:
                seen.add(neighbour)
                queue.append(neighbour)

    return {
        "simpul": sorted(names),
        "sisi": [list(pair) for pair in sorted(edges)],
        "terjangkau": sorted(seen),
        "terputus": sorted(names - seen),
        "jumlah_sisi": len(edges),
    }


def check() -> dict[str, Any]:
    """Bangun laporan konektivitas lengkap tanpa mengubah layanan."""
    heartbeat = _read(HEARTBEAT)
    definitions = registry()
    services = [service_status(item, heartbeat) for item in definitions]
    graph = build_graph()

    components: list[dict[str, Any]] = []
    for item in COMPONENTS:
        path = (ROOT / str(item["path"])).resolve()
        components.append({
            "nama": item["name"],
            "jenis": item["kind"],
            "peran": item["role"],
            "path": str(item["path"]),
            "ada": path.exists(),
            "layanan": item.get("service"),
        })

    missing = [item["nama"] for item in components if not item["ada"]]
    unmanaged = [
        item["nama"] for item in components
        if item["jenis"] in ("server", "process", "monitor") and not item["layanan"]
    ]
    registered_names = {item.get("name") for item in definitions}
    unregistered_sources = [
        name for name in registered_names
        if name not in {item["nama"] for item in components}
    ]
    gate = [s for s in services if s["dihitung"]]
    down = [s["nama"] for s in gate if not s["hidup"]]
    issues = heartbeat.get("issues", [])
    supervisor_ok = not issues and bool(heartbeat)

    laporan = {}
    for key, path in REPORT_SOURCES:
        data = _read(path)
        laporan[key] = data.get("status", data.get("supervisor-status", "tidak ada"))

    connected = (
        supervisor_ok
        and not missing
        and not unmanaged
        and not unregistered_sources
        and not down
        and not graph["terputus"]
        and (ROOT / ".").exists()
    )
    return {
        "status": "TERHUBUNG" if connected else "SEBAGIAN",
        "sumber_data": str(ROOT),
        "supervisor": {
            "status": heartbeat.get("timestamp", "tidak ada"),
            "masalah": issues,
            "layanan": len(services),
            "hidup": sum(1 for s in services if s["hidup"]),
            "mati": down,
        },
        "layanan": services,
        "komponen": components,
        "graf": graph,
        "masalah": {
            "path_hilang": missing,
            "tanpa_layanan": unmanaged,
            "di_registry_tanpa_komponen": unregistered_sources,
            "mati": down,
        },
        "laporan": laporan,
        "catatan": (
            "Supervisor menjaga layanan dari registry; komponen CLI terhubung lewat "
            "sumber data bersama dan relai chat. Port monitor tidak dijalankan. "
            "Tidak ada kredensial yang dibaca atau dicetak."
        ),
        "license": "Tom05ivier-commits-1.0",
        "owner": "Tomi vier",
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
