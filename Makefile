# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Ringkasan perintah Docker & pengujian.

COMPOSE := docker compose
DEV := docker compose -f docker-compose.dev.yml
EXEC := $(COMPOSE) exec infinity

.PHONY: help docker-check build up dev down logs status verify protect drill live-drill shell test clean chip chip-verify chip-score score dashboard iverilog security-score score-bootstrap secret-scan credential-audit apikey-check apikey-guard billing-guide billing-reminder share-check

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
	@echo "  shell       - masuk ke kontainer"
	@echo "  chip        - pasang/buka Sandbox Chip Merah Putih"
	@echo "  iverilog    - lint + kompilasi + simulasi testbench RTL"
	@echo "  chip-verify - model + iverilog + preset browser + scorecard"
	@echo "  chip-score  - hitung ulang skor kualitas chip (target 100/100)"
	@echo "  security-score - skor keamanan 12 kontrol (target 100/100)"
	@echo "  score-bootstrap - bangkitkan ulang laporan untuk skor pada clone kosong"
	@echo "  score       - chip + keamanan sekaligus (keduanya target 100/100)"
	@echo "  dashboard   - regenerasi dashboard.html dari laporan terbaru"
	@echo "  secret-scan - pindai nilai rahasia (tanpa menampilkan nilai)"
	@echo "  credential-audit - audit nama penanda kredensial"
	@echo "  apikey-check - uji tanda tangan API key dengan nilai buatan"
	@echo "  apikey-guard - audit mode 0600, .gitignore & kebocoran nilai
	@echo "  billing-guide - panduan tagihan Copilot CLI (tanpa kredensial)"
	@echo "  billing-reminder - cek hari jatuh tempo tagihan secara lokal""
	@echo "  share-check  - verifikasi OpenCode ↔ OpenCode AI & data bersama"
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

score-bootstrap:
	bash tools/bootstrap_scores.sh

dashboard:
	python3 system/cli.py dashboard

score: chip-score security-score
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

test:
	python3 -m unittest discover -s chip/tests -v
	python3 -m unittest discover -s system/tests -v
	python3 -m unittest discover -s security/tests -v
	python3 chip/chip_cli.py score
	python3 security/score.py
	$(MAKE) apikey-guard

clean:
	$(COMPOSE) down -v
	$(DEV) down -v
