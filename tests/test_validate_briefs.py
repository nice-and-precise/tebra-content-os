"""Tests for scripts/validate_briefs.py."""

import json
from pathlib import Path

from scripts.validate_briefs import validate

VALID_BRIEF = {
    "schema_version": "1.0",
    "slug": "tebra-vs-athenahealth",
    "asset_type": "comparison",
    "target_intent": {
        "primary_query": "tebra vs athenahealth",
        "query_cluster": ["tebra vs athenahealth for small practices"],
        "buyer_stage": "BOFU",
        "persona": "independent practice owner",
    },
    "proof_points": [
        {
            "claim": "Tebra onboards in 30 days",
            "source_id": "src-001",
            "source_type": "internal_doc",
            "required": True,
        }
    ],
    "required_internal_links": [],
    "bofu_cta": {"primary": "Start free trial"},
    "schema_hints": [],
    "competitor_coverage": {"required": ["athenahealth"], "optional": []},
    "sources": [
        {
            "id": "src-001",
            "type": "internal_doc",
            "path": None,
            "url": "https://tebra.com/docs/onboarding",
            "cite_as": "Tebra Onboarding Guide 2026",
        }
    ],
    "asana_task_id": None,
    "created_at": "2026-01-15T10:00:00Z",
    "created_by": "brief-author",
    "created_by_version": "1.0",
}


def write_brief(briefs_dir: Path, slug: str, data: dict) -> Path:
    briefs_dir.mkdir(parents=True, exist_ok=True)
    f = briefs_dir / f"{slug}.json"
    f.write_text(json.dumps(data), encoding="utf-8")
    return f


def test_validate_passes_on_empty_directory(tmp_path: Path):
    (tmp_path / "briefs").mkdir()
    assert validate(tmp_path / "briefs") == 0


def test_validate_fails_missing_directory(tmp_path: Path):
    assert validate(tmp_path / "no-such-dir") == 1


def test_validate_passes_valid_brief(tmp_path: Path):
    write_brief(tmp_path, "tebra-vs-athenahealth", VALID_BRIEF)
    assert validate(tmp_path) == 0


def test_validate_fails_invalid_json(tmp_path: Path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "bad.json").write_text("not json", encoding="utf-8")
    assert validate(tmp_path) == 1


def test_validate_fails_schema_error(tmp_path: Path):
    bad = {**VALID_BRIEF, "asset_type": "invalid_type"}
    write_brief(tmp_path, "tebra-vs-athenahealth", bad)
    assert validate(tmp_path) == 1


def test_validate_fails_slug_mismatch(tmp_path: Path):
    data = {**VALID_BRIEF, "slug": "wrong-slug"}
    write_brief(tmp_path, "tebra-vs-athenahealth", data)
    assert validate(tmp_path) == 1


def test_validate_fails_proof_point_missing_source(tmp_path: Path):
    data = {
        **VALID_BRIEF,
        "proof_points": [
            {
                "claim": "Some claim",
                "source_id": "nonexistent-src",
                "source_type": "internal_doc",
                "required": True,
            }
        ],
    }
    write_brief(tmp_path, "tebra-vs-athenahealth", data)
    assert validate(tmp_path) == 1


def test_validate_fails_comparison_without_competitor_coverage(tmp_path: Path):
    data = {**VALID_BRIEF, "competitor_coverage": {"required": [], "optional": []}}
    write_brief(tmp_path, "tebra-vs-athenahealth", data)
    assert validate(tmp_path) == 1
