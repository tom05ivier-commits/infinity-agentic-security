# /root is a persistent Android bind; seed optional tools after it is mounted.
if command -v python3 >/dev/null 2>&1; then
    python3 /usr/local/bin/opencode-install-layer-mcp
fi
