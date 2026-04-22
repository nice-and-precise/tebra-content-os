"""Shell-level integration tests for pre-tool-use-compliance.sh.

These tests invoke the hook directly via subprocess with realistic Claude Code
PreToolUse JSON payloads using absolute file_path values (CRITICAL-1 regression).
"""

import json
import subprocess
from pathlib import Path

HOOK = Path(__file__).parent.parent / ".claude/hooks/pre-tool-use-compliance.sh"
REPO_ROOT = Path(__file__).parent.parent


def _run_hook(file_path: str, content: str) -> subprocess.CompletedProcess:
    payload = json.dumps({
        "tool_name": "Write",
        "tool_input": {"file_path": file_path, "content": content},
    })
    return subprocess.run(
        ["bash", str(HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )


def test_hook_allows_clean_draft_absolute_path():
    """Absolute path to drafts/ with no medical claims → exit 0 (allow)."""
    result = _run_hook(
        file_path=str(REPO_ROOT / "drafts/clean.md"),
        content="---\ntitle: Clean Post\n---\nThis is a clean post with no claims.",
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"


def test_hook_denies_unsourced_medical_claim_absolute_path():
    """Absolute path to drafts/ with unsourced mortality claim → exit 2 (deny)."""
    result = _run_hook(
        file_path=str(REPO_ROOT / "drafts/risky.md"),
        content="---\ntitle: Risky\n---\nThis treatment reduces mortality by 50%.",
    )
    assert result.returncode == 2, f"stderr: {result.stderr}"
    stderr_data = json.loads(result.stderr)
    assert stderr_data["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_hook_ignores_absolute_path_outside_drafts():
    """Absolute path to docs/ (not drafts/) → exit 0 (hook doesn't fire)."""
    result = _run_hook(
        file_path=str(REPO_ROOT / "docs/mortality.md"),
        content="mortality by 50%",
    )
    assert result.returncode == 0, f"hook should not fire for docs/, stderr: {result.stderr}"


def test_hook_ignores_relative_path_outside_drafts():
    """Relative path not under drafts/ → exit 0."""
    result = _run_hook(
        file_path="scripts/foo.py",
        content="mortality by 50%",
    )
    assert result.returncode == 0
