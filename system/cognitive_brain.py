# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pemetaan fungsi kognitif otak manusia ke dalam supervisor IT Agenty.

Empat lapisan yang dipetakan (analogi, bukan klaim biologis):

    indra        -> persepsi & sensor perangkat
    memori       -> basis pengetahuan & jejak pengalaman
    perencanaan  -> korteks prefrontal: aturan + rencana tugas
    aksi         -> korteks motorik: eksekutor, respon teks, aktuator

Modul ini adalah *lapisan pengikat* yang bersifat read-only dan deskriptif:
ia membaca bukti keberadaan komponen, menyusun peta, dan menyediakan satu
siklus simulasi ``indra -> memori -> rencana -> aksi -> refleksi``. Ia TIDAK
menjalankan responder, tidak mengubah layanan, tidak membuka koneksi keluar,
dan tidak pernah membaca kredensial. Ini bukan model neural dan bukan klaim
kesadaran: sistem yang dipetakan adalah komponen perangkat lunak nyata.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:  # Samarkan data sensitif bila teks tujuan memuatnya.
    from security.privacy import redact  # noqa: E402
except Exception:  # pragma: no cover - fallback bila modul privasi tidak ada
    def redact(text: str) -> str:  # type: ignore[misc]
        return text

LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"
SCHEMA = "tom05-cognitive-brain-map/1"
REPORT = ROOT / "system" / "reports" / "cognitive_brain.json"

HEARTBEAT = ROOT / "system" / "reports" / "heartbeat.json"
REGISTRY = ROOT / "system" / "services.json"
CONNECTIONS = ROOT / "config" / "tom05-connections.json"
TASTE_CONFIG = ROOT / "config" / "taste_knowledge.json"
RIGHTS_CONFIG = ROOT / "config" / "rights_balance.json"
DISPATCH_REGISTRY = ROOT / "config" / "chat_dispatch.json"
DISPATCH_BASE = ROOT / "system" / "reports" / "chat_dispatch"
KNOWLEDGE_PATH = ROOT / "advanced" / "memory.jsonl"
DATASET_PATH = ROOT / "dataset" / "data" / "tom05_dataset.jsonl"
AGENT_STATE = ROOT / "agent" / "state.json"

# Tugas yang hanya membaca status; sisanya adalah aksi operasional/ofensif
# yang tidak boleh dijalankan otomatis oleh lapisan pemetaan ini.
READ_ONLY_TASKS = frozenset({
    "status", "verify", "capability", "integrity", "dashboard", "knowledge", "parity",
})
RESTRICTED_TASKS = frozenset({"drill", "campaign", "protect", "perfect"})

LAYERS: tuple[dict[str, Any], ...] = (
    {
        "id": "indra",
        "otak": "Sistem sensorik: mata, telinga, kulit, lidah (rasa), propriosepsi",
        "fungsi": (
            "Menerima informasi dari lingkungan dan kondisi tubuh sendiri, "
            "termasuk pengetahuan rasa sebagai kosakata simbolik"
        ),
        "komputer": "Persepsi, sensor perangkat, & pengetahuan rasa",
        "komponen": (
            {"nama": "AdvancedComputer.perceive", "path": "advanced/engine.py",
             "peran": "mengumpulkan keadaan sistem + indeks pengetahuan"},
            {"nama": "Hardware CLI", "path": "system/hardware_agent.py",
             "peran": "info perangkat, baterai, storage lewat skill android-device"},
            {"nama": "Service Watch", "path": "system/service_watch.py",
             "peran": "probe HTTP/TCP/process sebagai indra kesehatan layanan"},
            {"nama": "Supervisor heartbeat", "path": "system/supervisor.py",
             "peran": "propriosepsi: PID, heartbeat, dan restart layanan"},
            {"nama": "Peta koneksi", "path": "config/tom05-connections.json",
             "peran": "status koneksi OpenCode, provider, dan bridge"},
            {"nama": "Pengetahuan Rasa", "path": "system/taste_knowledge.py",
             "peran": "kosakata simbolik manis/asin/asam/pahit/umami, bukan sensor kimia"},
            {"nama": "Config Rasa", "path": "config/taste_knowledge.json",
             "peran": "definisi kategori rasa tanpa data biometrik atau pribadi"},
        ),
        "analogi": (
            "Cahaya/suara menjadi sinyal saraf; snapshot sistem menjadi data persepsi, "
            "sedangkan rasa menjadi pengetahuan simbolik di indra."
        ),
        "batasan": (
            "Bridge perangkat tidak mengekspos kamera, mikrofon, lidah, GPU, atau Vulkan. "
            "Rasa tidak diukur dari subjek; hanya lima kategori simbolik yang dipakai."
        ),
    },
    {
        "id": "memori",
        "otak": "Hippocampus & korteks asosiasi: pengalaman dan pengetahuan",
        "fungsi": "Menyimpan pengetahuan masa lalu dan mengingatnya saat dibutuhkan",
        "komputer": "Basis pengetahuan & jejak pengalaman",
        "komponen": (
            {"nama": "KnowledgeBase", "path": "advanced/knowledge.py",
             "peran": "indeks dokumen workspace dengan checksum"},
            {"nama": "Tom05 retrieval", "path": "system/tom05_knowledge.py",
             "peran": "pencarian TF-IDF ringan atas dokumen IT Agenty"},
            {"nama": "Dataset berlabel", "path": "dataset/data/tom05_dataset.jsonl",
             "peran": "rekord instruksi->jawaban dengan sumber dan lisensi"},
            {"nama": "Memori episodik", "path": "advanced/memory.jsonl",
             "peran": "catatan append-only hasil siklus persepsi->aksi->refleksi"},
            {"nama": "Jejak keputusan", "path": "agent/state.json",
             "peran": "riwayat rencana dan hasil eksekusi agen"},
            {"nama": "Arsip laporan", "path": "system/reports",
             "peran": "laporan status, skor, dan kepatuhan sebagai memori sistem"},
        ),
        "analogi": "Hippocampus mengkonsolidasikan pengalaman; berkas JSON menyimpan jejak.",
        "batasan": (
            "Ini retrieval dan berkas, bukan model neural: tidak ada bobt training, "
            "tidak ada pelatihan, dan kredensial tidak pernah diindeks."
        ),
    },
    {
        "id": "perencanaan",
        "otak": "Korteks prefrontal: pengambilan keputusan dan pengendalian impuls",
        "fungsi": (
            "Memilih tindakan berikutnya dengan menyeimbangkan kepentingan "
            "operasional dan hak di latar kebijakan"
        ),
        "komputer": "Perencana aturan, guardrail, & latar keseimbangan hak",
        "komponen": (
            {"nama": "AgentBrain.plan", "path": "agent/brain.py",
             "peran": "menerjemahkan tujuan menjadi langkah tugas yang aman"},
            {"nama": "Idea Engine", "path": "system/idea_engine.py",
             "peran": "sepuluh ide supervisor yang dikerjakan secara idempoten"},
            {"nama": "Registry layanan", "path": "system/services.json",
             "peran": "keputusan komponen mana yang dijalankan supervisor"},
            {"nama": "Guardrail izin", "path": "security/permission_automation.py",
             "peran": "membatasi izin otomatis: TTL <= 300 detik, kategori dilarang"},
            {"nama": "Gate akhir", "path": "system/final_status.py",
             "peran": "mengagregasi gate sebelum sistem dinyatakan selesai"},
            {"nama": "Keseimbangan Kepentingan-Hak", "path": "system/rights_balance.py",
             "peran": "latar kebijakan: hak mengikat kepentingan, izin terbatas & diaudit"},
            {"nama": "Config Keseimbangan", "path": "config/rights_balance.json",
             "peran": "daftar kepentingan, hak, TTL maks 300 detik, dan prioritas"},
        ),
        "analogi": (
            "Prefrontal memilih respons dan menekan impuls; latar hak menimbang "
            "kepentingan sebelum perencana memfilter aksi."
        ),
        "batasan": (
            "Perencana deterministik berbasis aturan, bukan penalaran sadar atau "
            "nasihat hukum. Bila bertentangan, hak didahulukan; aksi terbatas tetap "
            "memerlukan izin tertulis dan batas waktu."
        ),
    },
    {
        "id": "aksi",
        "otak": "Korteks motorik & otot: menjalankan keputusan menjadi gerakan",
        "fungsi": "Melaksanakan keputusan lewat tindakan nyata atau respon teks",
        "komputer": "Eksekutor, responder teks, dan aktuator",
        "komponen": (
            {"nama": "AgentRuntime", "path": "agent/runtime.py",
             "peran": "menjalankan satu langkah dan mencatat jejak audit"},
            {"nama": "Relai chat", "path": "system/chat_dispatch.py",
             "peran": "meneruskan pesan ke responder lokal sebagai respon teks"},
            {"nama": "Registri responder", "path": "config/chat_dispatch.json",
             "peran": "daftar aktuator tepercaya dengan argv, tanpa shell"},
            {"nama": "CLI sistem", "path": "system/cli.py",
             "peran": "menerbitkan perintah status, dashboard, dan service-add"},
            {"nama": "Kebijakan firewall", "path": "security/firewall",
             "peran": "aktuator jaringan userspace, bukan enforcement kernel"},
            {"nama": "Panduan perangkat", "path": "docs/HARDWARE-AGENT.md",
             "peran": "notifikasi, toast, clipboard, dan open-url lewat skill"},
        ),
        "analogi": "Saraf motorik menggerakkan otot; runtime menggerakkan proses dan teks.",
        "batasan": (
            "Mode pemetaan ini deskriptif: tidak mengeksekusi responder. Perintah "
            "responder memakai argv dari registri, diaudit, dan tanpa shell."
        ),
    },
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _count_lines(path: Path) -> int:
    try:
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    except OSError:
        return 0


def _exists(relative: str) -> bool:
    return (ROOT / relative).exists()


def _rights_balance():
    """Impor malas agar pemetaan tetap berfungsi tanpa modul kebijakan."""
    try:
        from system import rights_balance

        return rights_balance
    except Exception:  # pragma: no cover - fallback bila modul tidak ada
        class _Fallback:
            @staticmethod
            def evaluate(goal: str, authorize: bool = False) -> dict[str, Any]:
                return {"keputusan": "tidak-tersedia", "alasan": "modul kebijakan absen"}

            @staticmethod
            def describe() -> dict[str, Any]:
                return {"status": "TIDAK_SEIMBANG", "sumber": "tidak ada"}

        return _Fallback


def _task_kind(task: str) -> str:
    if task in RESTRICTED_TASKS:
        return "terbatas"
    if task in READ_ONLY_TASKS:
        return "read-only"
    return "lainnya"


def perceive() -> dict[str, Any]:
    """Kumpulkan sinyal indra secara read-only tanpa probe jaringan baru."""
    heartbeat = _read_json(HEARTBEAT)
    services = _read_json(REGISTRY).get("services", [])
    services = services if isinstance(services, list) else []
    heartbeat_services = heartbeat.get("services", {})
    alive = sum(
        1 for info in heartbeat_services.values()
        if isinstance(info, dict) and info.get("alive")
    ) if isinstance(heartbeat_services, dict) else 0
    inbox = DISPATCH_BASE / "inbox"
    outbox = DISPATCH_BASE / "outbox"
    return {
        "waktu": _now(),
        "mode": "read-only",
        "propriosepsi": {
            "heartbeat_ada": bool(heartbeat),
            "layanan_terdaftar": len(services),
            "layanan_hidup_tercatat": alive,
        },
        "sensor_perangkat": {
            "agen": "hardware",
            "laporan_skor": _exists("system/reports/device_score.json"),
            "gpu": "TIDAK_TEREKSPOS",
        },
        "antrean_chat": {
            "masuk": len(list(inbox.glob("*.json"))) if inbox.is_dir() else 0,
            "keluar": len(list(outbox.glob("*.json"))) if outbox.is_dir() else 0,
        },
        "peta_koneksi": {"path": "config/tom05-connections.json", "ada": _exists(
            "config/tom05-connections.json")},
        "rasa": {
            "sumber": "config/taste_knowledge.json",
            "sensor": False,
            "kategori": ["manis", "asin", "asam", "pahit", "umami"],
            "catatan": (
                "Pengetahuan rasa simbolik; tidak ada sensor lidah atau data "
                "biometrik yang dibaca."
            ),
        },
        "catatan": (
            "Tidak ada kamera, mikrofon, lidah, atau GPU yang diakses; sinyal "
            "berasal dari berkas status, skill perangkat, dan pengetahuan simbolik."
        ),
    }


def remember() -> dict[str, Any]:
    """Ringkas memori sistem tanpa menampilkan isi dokumen atau kredensial."""
    try:
        from advanced.knowledge import KnowledgeBase

        documents = KnowledgeBase().stats().get("documents", 0)
    except Exception:  # pragma: no cover - fallback bila modul tidak ada
        documents = 0
    state = _read_json(AGENT_STATE)
    runs = state.get("runs", [])
    report_files = 0
    for folder in (ROOT / "system" / "reports", ROOT / "security" / "reports"):
        if folder.is_dir():
            report_files += sum(1 for path in folder.glob("*.json") if path.is_file())
    return {
        "pengetahuan": {"dokumen_terindeks": documents, "sumber": "advanced/knowledge.py"},
        "dataset": {"rekord": _count_lines(DATASET_PATH), "trained": False},
        "memori_episodik": {"rekord": _count_lines(KNOWLEDGE_PATH)},
        "jejak_keputusan": {"runs": len(runs) if isinstance(runs, list) else 0},
        "arsip_laporan": {"berkas_json": report_files},
        "batasan": (
            "Retrieval berbasis berkas, bukan bobot neural; tidak ada training "
            "dan nilai sensitif tidak dimasukkan ke dalam laporan ini."
        ),
    }


def plan(goal: str = "status sistem", authorize: bool = False) -> dict[str, Any]:
    """Susun rencana dengan AgentBrain tanpa menjalankan tugas apa pun."""
    from agent.brain import AgentBrain

    steps = AgentBrain().plan(redact(str(goal))[:4000], authorize=authorize)
    return {
        "tujuan": redact(str(goal))[:4000],
        "izin": "dengan-otorisasi" if authorize else "tanpa-otorisasi",
        "langkah": [
            {
                "tugas": step.task,
                "jenis": _task_kind(step.task),
                "parameter": {
                    key: ("ya" if value is True else "tidak" if value is False else value)
                    for key, value in step.params.items()
                },
            }
            for step in steps
        ],
        "keseimbangan": _rights_balance().evaluate(goal, authorize=authorize),
        "catatan": (
            "Perencana berbasis aturan; langkah bertanda 'terbatas' tidak dijalankan "
            "otomatis. Latar hak didahulukan bila kepentingan bertentangan."
        ),
    }


def act() -> dict[str, Any]:
    """Petakan aktuator yang tersedia; jangan mengeksekusi apa pun."""
    registry = _read_json(DISPATCH_REGISTRY)
    responders = registry.get("responders", [])
    responders = responders if isinstance(responders, list) else []
    return {
        "mode": "deskriptif",
        "eksekutor": {"path": "agent/runtime.py", "ada": _exists("agent/runtime.py")},
        "respon_teks": {
            "jumlah_responder": len(responders),
            "nama": [str(item.get("name", "")) for item in responders
                     if isinstance(item, dict)],
        },
        "aktuator_perangkat": ["notify", "toast", "clipboard", "open-url"],
        "aktuator_kebijakan": "security/firewall (policy userspace)",
        "pengaman": {
            "shell": False,
            "argv_dari_registri": True,
            "audit": True,
            "aksi_ofensif_otomatis": False,
        },
        "catatan": (
            "Otot digital adalah proses dan teks: runtime menjalankan tugas, "
            "relai chat mengirim jawaban, skill perangkat memberi notifikasi."
        ),
    }


def reflect(layers: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Nilai kelengkapan pemetaan dari bukti komponen yang ada."""
    sources = layers if layers is not None else [
        {key: value for key, value in layer.items() if key != "bukti"} for layer in LAYERS
    ]
    results: list[dict[str, Any]] = []
    for layer in sources:
        components = layer.get("komponen", ())
        evidence = [
            {"nama": item["nama"], "path": item["path"], "ada": _exists(item["path"])}
            for item in components
        ]
        present = sum(1 for item in evidence if item["ada"])
        results.append({
            "lapisan": layer.get("id", "?"),
            "komponen": len(evidence),
            "hadir": present,
            "status": "LENGKAP" if present else "KOSONG",
            "bukti": evidence,
        })
    ok = bool(results) and all(item["status"] == "LENGKAP" for item in results)
    return {
        "status": "TERPETAKAN" if ok else "SEBAGIAN",
        "lapisan": results,
        "catatan": (
            "Status teknis mengenai keberadaan komponen; tidak menyatakan lisensi, "
            "otorisasi, atau kemampuan biologis."
        ),
    }


def cycle(goal: str = "status sistem", authorize: bool = False) -> dict[str, Any]:
    """Satu siklus kognitif simulasi: indra -> memori -> rencana -> aksi -> refleksi."""
    return {
        "tujuan": redact(str(goal))[:4000],
        "indra": perceive(),
        "memori": remember(),
        "perencanaan": plan(goal, authorize=authorize),
        "aksi": act(),
        "refleksi": {
            "status": "SIMULASI",
            "catatan": "Rencana tidak dijalankan; lihat agent/runtime.py untuk eksekusi nyata.",
        },
    }


def map_cognitive(goal: str = "status sistem") -> dict[str, Any]:
    """Bangun peta lengkap empat lapisan kognitif beserta buktinya."""
    layers: list[dict[str, Any]] = []
    for layer in LAYERS:
        entry = {key: value for key, value in layer.items() if key != "komponen"}
        entry["komponen"] = [
            {"nama": item["nama"], "path": item["path"], "peran": item["peran"],
             "ada": _exists(item["path"])}
            for item in layer["komponen"]
        ]
        layers.append(entry)
    reflection = reflect(layers)
    return {
        "schema": SCHEMA,
        "generated_at": _now(),
        "status": reflection["status"],
        "analogi": "Indra -> Memori -> Perencanaan -> Aksi",
        "lapisan": layers,
        "persepsi": perceive(),
        "memori": remember(),
        "latar": {
            "keseimbangan": _rights_balance().describe(),
            "catatan": (
                "Kepentingan operasional tunduk pada hak; ini kebijakan "
                "perangkat lunak, bukan nasihat hukum atau otoritas baru."
            ),
        },
        "contoh_siklus": cycle(goal),
        "refleksi": reflection,
        "catatan": (
            "Pemetaan fungsi kognitif ke komponen supervisor. Bukan model neural, "
            "bukan kesadaran, dan tidak membaca kredensial."
        ),
        "license": LICENSE,
        "owner": OWNER,
    }


def write_report(data: dict[str, Any], path: Path | None = None) -> Path:
    """Tulis laporan secara atomik."""
    target = path or REPORT
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(f".{target.name}.{uuid.uuid4().hex[:8]}.tmp")
    temp.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    os.replace(temp, target)
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Peta kognitif supervisor IT Agenty")
    parser.add_argument("--verify", action="store_true", help="kode 1 bila belum terpetakan")
    parser.add_argument("--no-write", action="store_true", help="jangan tulis laporan")
    parser.add_argument("--cycle", metavar="TUJUAN", help="cetak satu siklus simulasi saja")
    args = parser.parse_args(argv)

    if args.cycle is not None:
        result: dict[str, Any] = cycle(args.cycle)
    else:
        result = map_cognitive()
        if not args.no_write:
            write_report(result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.verify and args.cycle is None:
        return 0 if result["status"] == "TERPETAKAN" else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
