#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Verifikasi statis container tom05 — tidak memerlukan Docker daemon.
# Pemakaian: bash scripts/tom05_container_verify.sh [--json]

set -euo pipefail
ROOT="${AGENTY_WORKSPACE:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

JSON=0
if [ "${1:-}" = "--json" ]; then JSON=1; fi

PASS=0
FAIL=0
RESULTS=""

add() {
  local name="$1" ok="$2" detail="$3" status
  if [ "$ok" = "1" ]; then
    PASS=$((PASS + 1)); status="PASS"
  else
    FAIL=$((FAIL + 1)); status="FAIL"
  fi
  if [ -n "$RESULTS" ]; then RESULTS="${RESULTS},"; fi
  RESULTS="${RESULTS}{\"name\":\"${name}\",\"status\":\"${status}\",\"detail\":\"${detail}\"}"
  if [ "$JSON" -eq 0 ]; then
    printf '[%s] %-16s %s\n' "$status" "$name" "$detail"
  fi
}

# 1. Dockerfile purpose-built.
DF="Dockerfile.tom05"
if [ -f "$DF" ] \
  && grep -q 'SPDX-License-Identifier: Tom05ivier-commits-1.0' "$DF" \
  && grep -q '^USER 10001:10001' "$DF" \
  && grep -q '^HEALTHCHECK' "$DF" \
  && grep -q 'AS runtime' "$DF" \
  && grep -q 'AS verify' "$DF"; then
  add dockerfile 1 "multi-stage, non-root, healthcheck, build-time verify"
else
  add dockerfile 0 "struktur Dockerfile.tom05 tidak lengkap"
fi

# 2. Compose hardening.
CF="docker-compose.tom05.yml"
if [ -f "$CF" ] \
  && grep -q 'SPDX-License-Identifier: Tom05ivier-commits-1.0' "$CF" \
  && grep -q 'read_only: true' "$CF" \
  && grep -q 'cap_drop:' "$CF" \
  && grep -q 'no-new-privileges:true' "$CF" \
  && grep -q 'AGENTY_TOM05_PORT' "$CF" \
  && grep -q 'tom05-inference' "$CF"; then
  add compose 1 "read-only rootfs, cap_drop ALL, no-new-privileges, AGENTY_TOM05_PORT"
else
  add compose 0 "hardening docker-compose.tom05.yml tidak lengkap"
fi

# 3. Entry point tidak memakai variabel `PORT` polos.
EF="scripts/tom05_container_entrypoint.sh"
if [ -f "$EF" ] \
  && grep -q 'SPDX-License-Identifier: Tom05ivier-commits-1.0' "$EF" \
  && grep -q 'AGENTY_TOM05_PORT' "$EF" \
  && ! grep -qE '^PORT=' "$EF"; then
  add entrypoint 1 "memakai AGENTY_TOM05_PORT, bukan PORT"
else
  add entrypoint 0 "entry point tidak memenuhi aturan port"
fi

# 4. Katalog tom05 konsisten.
if python3 -c "
import json, pathlib
d = json.loads(pathlib.Path('config/tom05-models.json').read_text())
assert d['default'] == 'tom05/tom05-flash-free'
assert d['aliases'][0]['target'] == d['default']
" 2>/dev/null; then
  add catalog 1 "alias default mengarah ke model nyata"
else
  add catalog 0 "katalog tom05 tidak konsisten"
fi

# 5. SoC tom05 terverifikasi.
if python3 chip/chip_cli.py soc >/dev/null 2>&1; then
  add soc 1 "tom05_soc 1024 vektor PASS"
else
  add soc 0 "verifikasi tom05_soc gagal"
fi

# 6. Sintaks compose (opsional: CLI ada, daemon tidak diperlukan).
if command -v docker >/dev/null 2>&1 \
  && docker compose version >/dev/null 2>&1; then
  if docker compose -f docker-compose.tom05.yml config -q >/dev/null 2>&1; then
    add compose-config 1 "docker compose config valid"
  else
    add compose-config 0 "docker compose config tidak valid"
  fi
else
  add compose-config 1 "SKIP: Docker CLI/Compose tidak tersedia"
fi

# 7. Profil tampilan: orientasi lanskap + backend GPU Panfrost/Mali terdeklarasi.
if python3 -c "
import json, pathlib
d = json.loads(pathlib.Path('config/tom05-models.json').read_text())
p = d['capabilities']['display']
assert p['orientation'] == 'lanskap'
assert p['gpu_acceleration']['backends'] == ['panfrost', 'mali']
assert p['gpu_acceleration']['bridge_exposed'] is False
" 2>/dev/null \
  && grep -q 'TOM05_DISPLAY_ORIENTATION' "$DF" \
  && grep -q 'TOM05_GPU_BACKENDS' "$CF" \
  && grep -q 'display)' "$EF"; then
  add display 1 "lanskap + panfrost/mali (deklarasi-manual, bukan akses GPU nyata)"
else
  add display 0 "profil tampilan tidak lengkap"
fi

# 8. Jaringan bersama + manager + pendaftaran supervisor.
if grep -q 'agenty-net' "$CF" \
  && grep -q 'agenty-net' docker-compose.dev.yml \
  && grep -q 'http://infinity:8766/v1/chat/completions' "$CF" \
  && grep -q 'infinity:host-gateway' "$CF" \
  && python3 -c "
import json, pathlib
d = json.loads(pathlib.Path('system/services.json').read_text())
s = next(x for x in d['services'] if x['name'] == 'tom05-provider')
assert s['container'] == 'tom05-inference'
assert s['container_network'] == 'agenty-net'
assert s['manager'] == 'infinity'
" 2>/dev/null; then
  add manager 1 "agenty-net + infinity:8766 + tom05-provider terdaftar"
else
  add manager 0 "jaringan bersama / manager belum terhubung"
fi

STATUS="PASS"
[ "$FAIL" -gt 0 ] && STATUS="FAIL"

if [ "$JSON" -eq 1 ]; then
  printf '{"status":"%s","pass":%d,"fail":%d,"checks":[%s]}\n' \
    "$STATUS" "$PASS" "$FAIL" "$RESULTS"
else
  echo "---"
  echo "tom05 container: $STATUS ($PASS lulus, $FAIL gagal)"
fi

[ "$FAIL" -eq 0 ]
