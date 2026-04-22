"""Validate .mcp.json: check env vars are set, flag SSE transports."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

MCP_JSON = Path(__file__).parent.parent / ".mcp.json"
_ENV_VAR_RE = re.compile(r"\$\{(\w+)\}")


def _collect_env_refs(value: object) -> list[str]:
    if isinstance(value, str):
        return _ENV_VAR_RE.findall(value)
    if isinstance(value, dict):
        return [ref for v in value.values() for ref in _collect_env_refs(v)]
    if isinstance(value, list):
        return [ref for item in value for ref in _collect_env_refs(item)]
    return []


def validate(mcp_path: Path = MCP_JSON) -> int:
    if not mcp_path.exists():
        print(f"ERROR: {mcp_path} not found", file=sys.stderr)
        return 1

    with mcp_path.open() as f:
        config = json.load(f)

    servers = config.get("mcpServers", {})
    missing: list[str] = []
    sse_servers: list[str] = []
    exit_code = 0

    for name, server in servers.items():
        transport = server.get("type", "stdio")
        if transport == "sse":
            sse_servers.append(name)

        for var in _collect_env_refs(server):
            if not os.environ.get(var):
                missing.append(f"{name}: ${var}")

    if sse_servers:
        names = ", ".join(sse_servers)
        count = len(sse_servers)
        print(f"WARN: {count} server(s) use SSE transport (migrate to HTTP by 2026-06-30): {names}")

    if missing:
        print("WARN: the following env vars are not set:")
        for m in missing:
            print(f"  {m}")

    if not missing and not sse_servers:
        print(f"OK: {len(servers)} server(s) validated, all env vars present.")

    return exit_code


if __name__ == "__main__":
    sys.exit(validate())
