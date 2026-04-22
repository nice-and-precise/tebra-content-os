"""Tests for refresh_append.py — YAML frontmatter refresh helper."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import yaml

from scripts.refresh_append import append_refresh


def _make_draft(tmp_path: Path, cadence_days: int = 90, changes: list[str] | None = None) -> Path:
    now = datetime.now(UTC)
    frontmatter = {
        "schema_version": "1.0",
        "slug": "test-slug",
        "refresh": {
            "last_refreshed_at": now.isoformat(),
            "next_refresh_due": (now + timedelta(days=cadence_days)).isoformat(),
            "refresh_cadence_days": cadence_days,
            "recommended_changes": changes or [],
        },
    }
    path = tmp_path / "test-slug.md"
    path.write_text(f"---\n{yaml.dump(frontmatter)}---\nBody content.")
    return path


def _load_refresh(path: Path) -> dict:
    content = path.read_text()
    _, fm_str, _ = content.split("---", 2)
    return yaml.safe_load(fm_str)["refresh"]


def test_append_refresh_updates_last_refreshed_at(tmp_path: Path):
    draft = _make_draft(tmp_path)
    before = datetime.now(UTC)
    append_refresh(draft, ["Update stats"])
    after = datetime.now(UTC)

    last_refreshed = datetime.fromisoformat(_load_refresh(draft)["last_refreshed_at"])
    assert before <= last_refreshed <= after


def test_append_refresh_sets_next_due_from_cadence(tmp_path: Path):
    draft = _make_draft(tmp_path, cadence_days=90)
    before = datetime.now(UTC)
    append_refresh(draft, ["Update stats"])

    next_due = datetime.fromisoformat(_load_refresh(draft)["next_refresh_due"])
    assert abs((next_due - (before + timedelta(days=90))).total_seconds()) < 2


def test_append_refresh_appends_new_changes(tmp_path: Path):
    draft = _make_draft(tmp_path, changes=["Existing change"])
    append_refresh(draft, ["New change 1", "New change 2"])

    changes = _load_refresh(draft)["recommended_changes"]
    assert "Existing change" in changes
    assert "New change 1" in changes
    assert "New change 2" in changes


def test_append_refresh_deduplicates_changes(tmp_path: Path):
    draft = _make_draft(tmp_path, changes=["Update stats"])
    append_refresh(draft, ["Update stats", "New change"])

    changes = _load_refresh(draft)["recommended_changes"]
    assert changes.count("Update stats") == 1
    assert "New change" in changes


def test_append_refresh_preserves_body(tmp_path: Path):
    draft = _make_draft(tmp_path)
    append_refresh(draft, ["Update stats"])
    assert "Body content." in draft.read_text()


def test_append_refresh_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        append_refresh(tmp_path / "nonexistent.md", ["change"])


def test_append_refresh_no_refresh_section_raises(tmp_path: Path):
    path = tmp_path / "no-refresh.md"
    path.write_text("---\nschema_version: '1.0'\n---\nBody.")
    with pytest.raises(ValueError, match="refresh"):
        append_refresh(path, ["change"])


def test_append_refresh_no_frontmatter_raises(tmp_path: Path):
    path = tmp_path / "no-fm.md"
    path.write_text("Just plain text, no frontmatter.")
    with pytest.raises(ValueError, match="frontmatter"):
        append_refresh(path, ["change"])
