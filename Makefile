# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Ringkasan perintah Docker & pengujian.

COMPOSE := docker compose
DEV := docker compose -f docker-compose.dev.yml
EXEC := $(COMPOSE) exec infinity

.PHONY: help docker-check build up dev down logs status verify protect drill live-drill shell test clean chip chip-verify chip-score score dashboard iverilog security-score score-bootstrap secret-scan credential-audit apikey-check apikey-guard billing-guide billing-reminder share-check license-status connection-status model-connectivity infinity-connectivity infinity-connectivity-test chat-dispatch-status chat-dispatch-run chat-dispatch-test tom05-container tom05-container-verify tom05-score device-score container-score tom05-cli-install dataset-agent dataset-doctor dataset-build dataset-verify dataset-test firewall-chip cognitive-map cognitive-map-test neuro25 neuro25-test custom-agents custom-agents-force fleet github-mcp-audit bigquery-token-status bigquery-token-refresh bigquery-mcp-probe bigquery-mcp-guard

help:
	@echo "Target tersedia:"
	@echo "  docker-check - cek CLI, plugin, daemon & compose"
	@echo "  build       - bangun image"
	@echo "  up          - jalankan produksi (NET_ADMIN, host network)"
	@echo "  dev         - jalankan mode dev (tanpa NET_ADMIN)"
	@echo "  down        - hentikan kontainer"
	@echo "  logs        - ikuti log"
	@echo "  status      - status sistem"
	@echo "  verify      - verifikasi kepatuhan"
	@echo "  protect     - jalankan proteksi 10 detik"
	@echo "  drill       - latihan lengkap"
	@echo "  live-drill  - serangan saat proteksi aktif"
	@echo "  firewall-chip - verifikasi otomatis chip firewall (drill + Icarus)"
	@echo "  shell       - masuk ke kontainer"
	@echo "  chip        - pasang/buka Sandbox Chip Merah Putih"
	@echo "  iverilog    - lint + kompilasi + simulasi testbench RTL"
	@echo "  chip-verify - model + iverilog + preset browser + scorecard"
	@echo "  chip-score  - hitung ulang skor kualitas chip (target 100/100)"
	@echo "  security-score - skor keamanan 12 kontrol (target 100/100)"
	@echo "  score-bootstrap - bangkitkan ulang laporan untuk skor pada clone kosong"
	@echo "  tom05-score - skor kualitas Tom05 (target 100/100)"
	@echo "  device-score - skor integrasi perangkat (target 100/100)"
	@echo "  final-status - agregat seluruh gate (read-only)"
	@echo "  container-score - skor kualitas container (target 100/100; total 500/500)"
	@echo "  tom05-cli-install - pasang ulang CLI tom05 dari sumber workspace"
	@echo "  score       - chip + keamanan + tom05 + perangkat + container (total 500/500)"
	@echo "  dashboard   - regenerasi dashboard.html dari laporan terbaru"
	@echo "  secret-scan - pindai nilai rahasia (tanpa menampilkan nilai)"
	@echo "  credential-audit - audit nama penanda kredensial"
	@echo "  apikey-check - uji tanda tangan API key dengan nilai buatan"
	@echo "  apikey-guard - audit mode 0600, .gitignore & kebocoran nilai"
	@echo "  billing-guide - panduan tagihan Copilot CLI (tanpa kredensial)"
	@echo "  billing-reminder - cek hari jatuh tempo tagihan secara lokal"
	@echo "  dataset-agent  - profil agen CLI dataset (JSON, read-only)"
	@echo "  dataset-doctor - laporan jujur prasyarat training (read-only)"
	@echo "  dataset-build  - bangun dataset berlabel dari dokumen workspace"
	@echo "  dataset-verify - validasi + privasi dataset tanpa menampilkan nilai"
	@echo "  dataset-test   - uji agen CLI dataset (21 kasus)"
	@echo "  share-check  - verifikasi OpenCode ↔ OpenCode AI & data bersama"
	@echo "  license-status - status peresmian lisensi (read-only)"
	@echo "  connection-status - status koneksi OpenCode/tom05 (read-only)"
	@echo "  model-connectivity - peta supervisor <-> semua model (read-only)"
	@echo "  infinity-connectivity - peta supervisor <-> semua komponen workspace (read-only)"
	@echo "  infinity-connectivity-test - uji peta konektivitas infinity"
	@echo "  cognitive-map - peta fungsi kognitif otak -> komponen supervisor"
	@echo "  cognitive-map-test - uji pemetaan kognitif (18 kasus)"
	@echo "  neuro25 - verifikasi chip simulasi NEURO-25 (bukan alat medis)"
	@echo "  neuro25-test - uji model & RTL chip NEURO-25"
	@echo "  custom-agents - verifikasi 23 chip kustom per agen (cache)"
	@echo "  custom-agents-force - paksa verifikasi ulang chip kustom"
	@echo "  fleet - status gabungan 23 chip agen + NEURO-25 (read-only)"
	@echo "  github-mcp-audit - audit konfigurasi GitHub MCP (tanpa token)"
	@echo "  bigquery-token-status - status token BigQuery MCP (tanpa nilai)"
	@echo "  bigquery-token-refresh - perbarui token + aktifkan MCP (--authorize)"
	@echo "  bigquery-mcp-probe - cek alat metadata BigQuery via tools/list"
	@echo "  bigquery-mcp-guard - cek mode token & invariant privasi (offline)"
	@echo "  chat-dispatch-status - status antrean & responder relai chat (read-only)"
	@echo "  chat-dispatch-run - proses antrean relai chat sekali jalan"
	@echo "  chat-dispatch-test - uji alur relai chat (termasuk regresi race)"
	@echo "  tom05-container-verify - verifikasi statis container tom05 (tanpa daemon)"
	@echo "  tom05-container - jalankan container tom05 hardened"
	@echo "  test        - jalankan seluruh tes"
	@echo "  clean       - hentikan & hapus volume"

docker-check:
	bash docker-cli-check.sh

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d --build

dev:
	$(DEV) up -d --build

down:
	$(COMPOSE) down
	$(DEV) down

logs:
	$(COMPOSE) logs -f infinity

status:
	$(EXEC) status

verify:
	$(EXEC) verify

protect:
	$(EXEC) protect --seconds 10

drill:
	$(EXEC) drill

live-drill:
	$(EXEC) live-drill

firewall-chip:
	bash ./run_firewall_chip.sh

shell:
	$(EXEC) shell

chip:
	@CHIP_NO_OPEN=$${CHIP_NO_OPEN:-0} ./run_chip.sh

iverilog:
	python3 chip/chip_cli.py iverilog

chip-verify:
	python3 chip/chip_cli.py verify
	python3 chip/chip_cli.py iverilog
	./site/chip/test_presets.sh
	python3 chip/chip_cli.py score

chip-score:
	python3 chip/chip_cli.py score

security-score:
	python3 security/score.py

tom05-cli-install:
	install -m 0755 tom05 /usr/local/bin/tom05
	# hy4 sengaja tidak dipasang di /usr/local/bin (lihat AGENTS.md dan tes CLI).

final-status:
	python3 system/final_status.py

device-score:
	python3 system/device_score.py

container-score:
	python3 system/container_score.py

tom05-score:
	python3 system/tom05_score.py

score-bootstrap:
	bash tools/bootstrap_scores.sh

dashboard:
	python3 system/cli.py dashboard

score: chip-score security-score tom05-score device-score container-score
	$(MAKE) dashboard

secret-scan:
	python3 tools/secret_scan.py .

credential-audit:
	python3 tools/credential_audit.py .

apikey-check:
	python3 tools/apikey_demo.py selftest

apikey-guard:
	./api-key.sh guard

billing-guide:
	python3 security/copilot_billing.py guide

billing-reminder:
	python3 tools/copilot_billing_reminder.py

share-check:
	python3 system/shared_data.py

license-status:
	python3 system/license_formalization.py

connection-status:
	python3 system/connection_status.py

model-connectivity:
	python3 system/model_connectivity.py

infinity-connectivity:
	python3 system/infinity_connectivity.py

infinity-connectivity-test:
	python3 -m unittest system.tests.test_infinity_connectivity -v

cognitive-map:
	python3 system/cognitive_brain.py

cognitive-map-test:
	python3 -m unittest system.tests.test_cognitive_brain -v

neuro25:
	python3 chip/chip_cli.py neuro25

neuro25-test:
	python3 -m unittest chip.tests.test_neuro25 -v

custom-agents:
	python3 chip/chip_cli.py custom-agents

custom-agents-force:
	python3 chip/chip_cli.py custom-agents --force

fleet:
	python3 chip/chip_cli.py fleet

github-mcp-audit:
	python3 tools/github_mcp_audit.py

bigquery-token-status:
	python3 tools/bigquery_token_refresh.py status

bigquery-token-refresh:
	python3 tools/bigquery_token_refresh.py refresh --authorize

bigquery-mcp-probe:
	python3 tools/bigquery_token_refresh.py probe

bigquery-mcp-guard:
	python3 tools/bigquery_token_refresh.py guard

chat-dispatch-status:
	python3 system/chat_dispatch.py status

chat-dispatch-run:
	python3 system/chat_dispatch.py run

chat-dispatch-test:
	python3 -m unittest system.tests.test_chat_dispatch -v

service-watch:
	python3 system/service_watch.py once

service-watch-test:
	python3 -m unittest system.tests.test_service_watch -v

supervisor-status:
	python3 system/cli.py supervisor-status

sre-watch:
	python3 system/sre_watch.py once

sre-watch-test:
	python3 -m unittest system.tests.test_sre_watch -v

watch-status:
	python3 system/service_watch.py once
	python3 system/sre_watch.py once

dataset-agent:
	./dataset-cli agent

dataset-doctor:
	./dataset-cli doctor

dataset-build:
	./dataset-cli build

dataset-verify:
	./dataset-cli validate dataset/data/tom05_dataset.jsonl
	./dataset-cli privacy dataset/data/tom05_dataset.jsonl

dataset-test:
	python3 -m unittest discover -s dataset/tests -v

test:
	python3 -m unittest discover -s dataset/tests -v
	python3 -m unittest discover -s chip/tests -v
	python3 -m unittest discover -s system/tests -v
	python3 -m unittest discover -s security/tests -v
	python3 chip/chip_cli.py score
	python3 security/score.py
	python3 system/tom05_score.py
	python3 system/device_score.py
	python3 system/container_score.py
	$(MAKE) apikey-guard

tom05-container-verify:
	bash scripts/tom05_container_verify.sh

tom05-container:
	docker compose -f docker-compose.tom05.yml up -d --build

clean:
	$(COMPOSE) down -v
	$(DEV) down -v
