"""Tests for scripts/validate_sources.py."""

import json
from pathlib import Path

from scripts.validate_sources import validate

REGISTRY_PATH = Path(__file__).parent.parent / "sources" / "registry.json"

VALID_SOURCE = {
    "schema_version": "1.1",
    "id": "test-source-1",
    "type": "internal_doc",
    "title": "Test Source",
    "authority_tier": 1,
    "cite_as": "Test Source 2026",
    "path": None,
    "url": "https://example.com/test",
    "added_at": "2026-01-01T00:00:00Z",
    "added_by": "test@example.com",
    "approved_for_claims": ["product_feature"],
    "not_approved_for_claims": [],
    "expires_at": "2099-01-01T00:00:00Z",
    "citation_api_ready": True,
}


def write_registry(tmp_path: Path, registry: dict) -> Path:
    reg_file = tmp_path / "registry.json"
    reg_file.write_text(json.dumps(registry), encoding="utf-8")
    return reg_file


def test_validate_passes_on_real_registry():
    assert validate(REGISTRY_PATH) == 0


def test_validate_fails_missing_registry(tmp_path: Path):
    assert validate(tmp_path / "nonexistent.json") == 1


def test_validate_fails_empty_registry(tmp_path: Path):
    reg = write_registry(tmp_path, {})
    assert validate(reg) == 1


def test_validate_fails_invalid_json(tmp_path: Path):
    reg = tmp_path / "registry.json"
    reg.write_text("not json", encoding="utf-8")
    assert validate(reg) == 1


def test_validate_fails_schema_error(tmp_path: Path):
    bad = {**VALID_SOURCE, "approved_for_claims": []}
    reg = write_registry(tmp_path, {"test-source-1": bad})
    assert validate(reg) == 1


def test_validate_fails_id_key_mismatch(tmp_path: Path):
    source = {**VALID_SOURCE, "id": "wrong-id"}
    reg = write_registry(tmp_path, {"test-source-1": source})
    assert validate(reg) == 1


def test_validate_fails_missing_path_file(tmp_path: Path):
    source = {**VALID_SOURCE, "path": "sources/internal/nonexistent.pdf", "url": None}
    reg = write_registry(tmp_path, {"test-source-1": source})
    assert validate(reg) == 1


def test_validate_fails_expired_source(tmp_path: Path):
    source = {**VALID_SOURCE, "expires_at": "2020-01-01T00:00:00Z"}
    reg = write_registry(tmp_path, {"test-source-1": source})
    assert validate(reg) == 1


def test_validate_url_only_source_passes(tmp_path: Path):
    source = {**VALID_SOURCE, "path": None, "url": "https://example.com/test"}
    reg = write_registry(tmp_path, {"test-source-1": source})
    assert validate(reg) == 0


def test_validate_passes_with_on_disk_path(tmp_path: Path):
    stub = tmp_path / "my-doc.pdf"
    stub.write_text("stub", encoding="utf-8")
    source = {**VALID_SOURCE, "path": str(stub), "url": None}
    reg = write_registry(tmp_path, {"test-source-1": source})
    assert validate(reg) == 0
