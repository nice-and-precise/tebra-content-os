import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from scripts.compliance_check import (
    check_draft_content,
    detect_claims,
    load_registry,
    parse_frontmatter,
)

# ---- Helpers ----


def future_iso() -> str:
    return (datetime.now(UTC) + timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")


def past_iso() -> str:
    return (datetime.now(UTC) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")


def make_source(
    id_: str = "src_test",
    authority_tier: int = 1,
    expires_at: str | None = None,
) -> dict:
    return {
        "schema_version": "1.0",
        "id": id_,
        "type": "internal_doc",
        "title": "Test Source",
        "authority_tier": authority_tier,
        "cite_as": "Test Source 2026",
        "path": None,
        "url": None,
        "added_at": "2026-01-01T00:00:00Z",
        "added_by": "test",
        "approved_for_claims": ["product_feature"],
        "not_approved_for_claims": [],
        "expires_at": expires_at or future_iso(),
        "citation_api_ready": True,
    }


def write_registry(tmp_path: Path, sources: list[dict]) -> Path:
    path = tmp_path / "registry.json"
    path.write_text(json.dumps({s["id"]: s for s in sources}))
    return path


def draft_content(slug: str, cited_claims: list[dict], body: str) -> str:
    """Build a minimal draft markdown with YAML frontmatter containing citation data."""
    sources_yaml = ""
    if cited_claims:
        sources_yaml = "sources:\n"
        for cc in cited_claims:
            sources_yaml += (
                f"  - id: {cc['source_id']}\n"
                f"    claims_cited:\n"
                f"      - block_id: proof-1\n"
                f"        claim: \"{cc['claim']}\"\n"
                f"        citation_api_format:\n"
                f"          type: document\n"
                f"          source:\n"
                f"            type: base64\n"
                f"            media_type: application/pdf\n"
                f"            data: abc123\n"
                f"          citations: true\n"
                f"          title: Test Source\n"
            )
    fm = f'---\nschema_version: "1.0"\nslug: "{slug}"\n{sources_yaml}---\n'
    return fm + body


# ---- detect_claims ----


def test_detect_claims_percentage_outcome():
    text = "This treatment reduces mortality by 50%."
    assert detect_claims(text) != []


def test_detect_claims_mortality_keyword():
    text = "The drug targets mortality in elderly patients."
    assert detect_claims(text) != []


def test_detect_claims_fda_approved():
    text = "Our FDA-approved device meets all standards."
    assert detect_claims(text) != []


def test_detect_claims_plain_text_no_match():
    text = "Our software helps practices streamline billing and scheduling."
    assert detect_claims(text) == []


def test_detect_claims_dosage():
    text = "Patients receive 500 mg daily."
    assert detect_claims(text) != []


# ---- parse_frontmatter ----


def test_parse_frontmatter_splits_correctly():
    content = '---\nslug: "test"\n---\nBody text here.'
    meta, body = parse_frontmatter(content)
    assert meta == {"slug": "test"}
    assert "Body text here." in body


def test_parse_frontmatter_no_frontmatter():
    content = "Just plain text."
    meta, body = parse_frontmatter(content)
    assert meta == {}
    assert body == "Just plain text."


def test_parse_frontmatter_malformed_yaml_returns_empty_meta():
    content = "---\n: bad: yaml: [\n---\nBody."
    meta, body = parse_frontmatter(content)
    assert meta == {}


# ---- load_registry ----


def test_load_registry_missing_file_returns_empty(tmp_path: Path):
    result = load_registry(tmp_path / "nonexistent.json")
    assert result == {}


def test_load_registry_valid_file(tmp_path: Path):
    reg = write_registry(tmp_path, [make_source()])
    result = load_registry(reg)
    assert "src_test" in result


# ---- check_draft_content: allow cases ----


def test_check_allow_no_medical_claims(tmp_path: Path):
    reg = write_registry(tmp_path, [])
    content = "Tebra streamlines billing and scheduling for independent practices."
    result = check_draft_content(content, reg)
    assert result.decision == "allow"
    assert result.claims_checked == 0


def test_check_allow_sourced_claim_valid_source(tmp_path: Path):
    src = make_source()
    reg = write_registry(tmp_path, [src])
    # "reduces pain by 50%" triggers only the percentage pattern (not the mortality keyword)
    content = draft_content(
        slug="test",
        cited_claims=[{"source_id": "src_test", "claim": "reduces pain by 50%"}],
        body="This treatment reduces pain by 50%.",
    )
    result = check_draft_content(content, reg)
    assert result.decision == "allow"
    assert result.claims_sourced == result.claims_checked


# ---- check_draft_content: deny cases ----


def test_check_deny_medical_claim_no_citations(tmp_path: Path):
    reg = write_registry(tmp_path, [])
    content = "This drug reduces mortality by 50%."
    result = check_draft_content(content, reg)
    assert result.decision == "deny"
    assert result.claims_flagged > 0


def test_check_deny_claim_source_not_in_registry(tmp_path: Path):
    reg = write_registry(tmp_path, [])  # empty registry
    content = draft_content(
        slug="test",
        cited_claims=[{"source_id": "src_missing", "claim": "reduces mortality by 50%"}],
        body="This treatment reduces mortality by 50%.",
    )
    result = check_draft_content(content, reg)
    assert result.decision == "deny"
    assert "not in registry" in result.reason


def test_check_deny_expired_source(tmp_path: Path):
    src = make_source(expires_at=past_iso())
    reg = write_registry(tmp_path, [src])
    content = draft_content(
        slug="test",
        cited_claims=[{"source_id": "src_test", "claim": "reduces mortality by 50%"}],
        body="This treatment reduces mortality by 50%.",
    )
    result = check_draft_content(content, reg)
    assert result.decision == "deny"
    assert "expired" in result.reason


def test_check_deny_tier4_source(tmp_path: Path):
    src = make_source(authority_tier=4)
    reg = write_registry(tmp_path, [src])
    content = draft_content(
        slug="test",
        cited_claims=[{"source_id": "src_test", "claim": "reduces mortality by 50%"}],
        body="This treatment reduces mortality by 50%.",
    )
    result = check_draft_content(content, reg)
    assert result.decision == "deny"
    assert "tier 4" in result.reason


# ---- CheckResult structure ----


def test_check_result_counts_sourced_and_flagged(tmp_path: Path):
    src = make_source()
    reg = write_registry(tmp_path, [src])
    # One sourced claim + one unsourced claim
    content = draft_content(
        slug="test",
        cited_claims=[{"source_id": "src_test", "claim": "reduces mortality by 50%"}],
        body="This treatment reduces mortality by 50%. It is also FDA-approved for general use.",
    )
    result = check_draft_content(content, reg)
    assert result.claims_checked >= 2
    assert result.claims_sourced >= 1
    assert result.claims_flagged >= 1
    assert result.decision == "deny"


# ---- Bug regression tests ----


def test_short_detection_not_authorized_by_long_citation(tmp_path: Path):
    """CRITICAL-2: bare 'mortality' detection must not match a longer cited claim."""
    src = make_source()
    reg = write_registry(tmp_path, [src])
    content = draft_content(
        slug="test",
        cited_claims=[
            {"source_id": "src_test", "claim": "reduces mortality by 50% in clinical outcomes"}
        ],
        body="Separately, mortality remains a key concern.",
    )
    result = check_draft_content(content, reg)
    assert result.decision == "deny"


def test_validate_source_unparseable_expiry_denies(tmp_path: Path):
    """HIGH-1: unparseable expires_at must not be silently treated as non-expired."""
    src = make_source()
    src["expires_at"] = "not-a-date"
    reg = write_registry(tmp_path, [src])
    content = draft_content(
        slug="test",
        cited_claims=[{"source_id": "src_test", "claim": "reduces mortality by 50%"}],
        body="This treatment reduces mortality by 50%.",
    )
    result = check_draft_content(content, reg)
    assert result.decision == "deny"
    assert "unparseable" in result.reason


def test_load_registry_malformed_json_raises(tmp_path: Path):
    """MEDIUM-1: malformed registry JSON must raise RuntimeError, not JSONDecodeError."""
    path = tmp_path / "registry.json"
    path.write_text("{not valid json}")
    with pytest.raises(RuntimeError, match="registry"):
        load_registry(path)
