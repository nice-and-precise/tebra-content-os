"""Validate .mcp.json schema and validate_mcp_config.py logic."""

import json
import os
from pathlib import Path

from scripts.validate_mcp_config import validate

MCP_JSON = Path(__file__).parent.parent / ".mcp.json"


# ---- .mcp.json structural tests ----


def test_mcp_json_exists():
    assert MCP_JSON.exists(), ".mcp.json missing at repo root"


def test_mcp_json_parses():
    with MCP_JSON.open() as f:
        config = json.load(f)
    assert isinstance(config, dict)


def test_mcp_json_has_mcp_servers_key():
    with MCP_JSON.open() as f:
        config = json.load(f)
    assert "mcpServers" in config


def test_mcp_servers_non_empty():
    with MCP_JSON.open() as f:
        config = json.load(f)
    assert config["mcpServers"], "mcpServers must not be empty"


def test_each_server_has_command_or_type():
    with MCP_JSON.open() as f:
        config = json.load(f)
    for name, server in config["mcpServers"].items():
        has_command = "command" in server
        has_type = "type" in server
        assert has_command or has_type, (
            f"server '{name}' must have 'command' (stdio) or 'type' (http)"
        )


def test_no_inline_secrets():
    """Env vars must be referenced as ${VAR}, not hardcoded."""
    raw = MCP_JSON.read_text()
    for keyword in ("sk-", "api_key=", "Bearer eyJ"):
        assert keyword.lower() not in raw.lower(), f"Possible secret found: {keyword!r}"


# ---- validate() function tests ----


def test_validate_returns_0_on_valid_config(tmp_path: Path):
    cfg = {
        "mcpServers": {
            "myserver": {
                "command": "npx",
                "args": ["-y", "my-mcp"],
                "env": {"MY_KEY": "${MY_KEY}"},
            }
        }
    }
    cfg_path = tmp_path / ".mcp.json"
    cfg_path.write_text(json.dumps(cfg))
    env = os.environ.copy()
    env["MY_KEY"] = "test-value"
    # Patch env temporarily
    old = os.environ.get("MY_KEY")
    os.environ["MY_KEY"] = "test-value"
    try:
        result = validate(cfg_path)
    finally:
        if old is None:
            os.environ.pop("MY_KEY", None)
        else:
            os.environ["MY_KEY"] = old
    assert result == 0


def test_validate_warns_on_missing_env(tmp_path: Path, capsys):
    cfg = {
        "mcpServers": {
            "myserver": {
                "type": "http",
                "url": "${MISSING_VAR_XYZ}",
            }
        }
    }
    cfg_path = tmp_path / ".mcp.json"
    cfg_path.write_text(json.dumps(cfg))
    os.environ.pop("MISSING_VAR_XYZ", None)
    validate(cfg_path)
    captured = capsys.readouterr()
    assert "MISSING_VAR_XYZ" in captured.out


def test_validate_warns_on_sse_transport(tmp_path: Path, capsys):
    cfg = {
        "mcpServers": {
            "legacy": {
                "type": "sse",
                "url": "https://example.com/sse",
            }
        }
    }
    cfg_path = tmp_path / ".mcp.json"
    cfg_path.write_text(json.dumps(cfg))
    validate(cfg_path)
    captured = capsys.readouterr()
    assert "SSE" in captured.out


def test_validate_missing_file(tmp_path: Path):
    result = validate(tmp_path / "nonexistent.json")
    assert result == 1


# ---- firecrawl + exa tool-name regression ----


def test_firecrawl_key_in_mcp_json():
    with MCP_JSON.open() as f:
        config = json.load(f)
    assert "firecrawl" in config["mcpServers"], "firecrawl must be a registered server key"


def test_exa_key_in_mcp_json():
    with MCP_JSON.open() as f:
        config = json.load(f)
    assert "exa" in config["mcpServers"], "exa must be a registered server key"
