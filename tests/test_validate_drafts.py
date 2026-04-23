"""Tests for scripts/validate_drafts.py."""

from pathlib import Path

from scripts.validate_drafts import _extract_frontmatter, validate

VALID_FRONTMATTER = """\
schema_version: "1.1"
slug: tebra-vs-athenahealth
asset_type: comparison
status: draft
brief_path: briefs/tebra-vs-athenahealth.json
author:
  type: subagent
  identifier: draft-writer
  version: "1.0"
extractability_score:
  total: 4.0
  schema_present: 1.0
  semantic_hierarchy: 1.0
  qa_patterns: 0.5
  proof_attribution: 1.0
  answer_first_structure: 0.5
  scored_at: "2026-01-15T10:00:00Z"
  scored_by: citation-auditor
sources:
  - id: src-001
    claims_cited: []
compliance_hook_log:
  last_run: "2026-01-15T10:00:00Z"
  decision: allow
  claims_checked: 0
  claims_sourced: 0
  claims_flagged: 0
refresh:
  last_refreshed_at: "2026-01-15T10:00:00Z"
  next_refresh_due: "2026-04-15T10:00:00Z"
  refresh_cadence_days: 90
  recommended_changes: []
"""

VALID_DRAFT = f"---\n{VALID_FRONTMATTER}---\n\n# Tebra vs athenahealth\n\nBody content.\n"


def write_draft(drafts_dir: Path, slug: str, content: str) -> Path:
    drafts_dir.mkdir(parents=True, exist_ok=True)
    f = drafts_dir / f"{slug}.md"
    f.write_text(content, encoding="utf-8")
    return f


def test_extract_frontmatter_valid():
    result = _extract_frontmatter("---\nfoo: bar\n---\n\nbody")
    assert result == {"foo": "bar"}


def test_extract_frontmatter_missing():
    assert _extract_frontmatter("no frontmatter here") is None


def test_extract_frontmatter_unclosed():
    assert _extract_frontmatter("---\nfoo: bar\n") is None


def test_validate_passes_on_empty_directory(tmp_path: Path):
    (tmp_path / "drafts").mkdir()
    assert validate(tmp_path / "drafts") == 0


def test_validate_fails_missing_directory(tmp_path: Path):
    assert validate(tmp_path / "no-such-dir") == 1


def test_validate_passes_valid_draft(tmp_path: Path):
    (tmp_path / "briefs").mkdir()
    (tmp_path / "briefs" / "tebra-vs-athenahealth.json").write_text("{}", encoding="utf-8")
    content = VALID_DRAFT.replace(
        "brief_path: briefs/tebra-vs-athenahealth.json",
        f"brief_path: {tmp_path / 'briefs' / 'tebra-vs-athenahealth.json'}",
    )
    write_draft(tmp_path, "tebra-vs-athenahealth", content)
    assert validate(tmp_path) == 0


def test_validate_fails_missing_frontmatter(tmp_path: Path):
    write_draft(tmp_path, "tebra-vs-athenahealth", "# No frontmatter\n\nJust body.")
    assert validate(tmp_path) == 1


def test_validate_fails_schema_error(tmp_path: Path):
    bad = VALID_DRAFT.replace('status: draft', 'status: invalid_status')
    write_draft(tmp_path, "tebra-vs-athenahealth", bad)
    assert validate(tmp_path) == 1


def test_validate_fails_slug_mismatch(tmp_path: Path):
    bad = VALID_DRAFT.replace("slug: tebra-vs-athenahealth", "slug: wrong-slug")
    write_draft(tmp_path, "tebra-vs-athenahealth", bad)
    assert validate(tmp_path) == 1


def test_validate_fails_missing_brief_path(tmp_path: Path):
    bad = VALID_DRAFT.replace(
        "brief_path: briefs/tebra-vs-athenahealth.json",
        "brief_path: briefs/nonexistent.json",
    )
    write_draft(tmp_path, "tebra-vs-athenahealth", bad)
    assert validate(tmp_path) == 1


def test_validate_passes_when_brief_exists_on_disk(tmp_path: Path):
    brief_dir = tmp_path / "briefs"
    brief_dir.mkdir()
    (brief_dir / "tebra-vs-athenahealth.json").write_text("{}", encoding="utf-8")
    content = VALID_DRAFT.replace(
        "brief_path: briefs/tebra-vs-athenahealth.json",
        f"brief_path: {brief_dir / 'tebra-vs-athenahealth.json'}",
    )
    write_draft(tmp_path, "tebra-vs-athenahealth", content)
    assert validate(tmp_path) == 0
