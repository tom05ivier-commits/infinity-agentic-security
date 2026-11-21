# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Image untuk Infinity Computer System + Infinity Security Suite.
# CAP_NET_ADMIN diberikan saat runtime (lihat docker-compose.yml).

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    AGENTY_WORKSPACE=/workspace \
    AGENTY_DISABLE_TUNNEL=1 \
    AGENTY_DISABLE_PUBLIC=1 \
    BIND_HOST=127.0.0.1 \
    BIND_PORT=8765 \
    LANG=id_ID.UTF-8 \
    LANGUAGE=id_ID:id \
    LC_ALL=id_ID.UTF-8

# iptables + iproute2 untuk enforcement kernel; locales untuk locale Indonesia.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      iptables iproute2 ca-certificates procps locales \
 && sed -i 's/^# *id_ID.UTF-8/id_ID.UTF-8/' /etc/locale.gen \
 && locale-gen \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY . /workspace

RUN chmod +x \
      docker-entrypoint.sh \
      run_system.sh \
      run_security_drill.sh \
      run_always.sh \
      run_agent.sh \
      run_advanced.sh \
      run_copilot.sh \
      connect_host_chrome.sh \
      hy4 \
      capability-setup.sh \
      docker-cli-check.sh \
      prepare_github.sh \
      push_github.sh \
      security/firewall/enable_kernel.sh \
      security/firewall/setup-capbnd.sh \
      security/firewall/install-net-admin.sh \
      security/firewall/capbnd.sh \
      security/workflow-daemon.sh

# 8765 dashboard/API · 8766 Copilot bridge · 8767 file server · 8768 publik (auth)
EXPOSE 8765 8766 8767 8768 8769 8770

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["serve"]
