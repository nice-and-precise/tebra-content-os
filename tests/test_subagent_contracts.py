import pytest
from pydantic import ValidationError

from scripts.schemas import Brief, Draft, SubagentResponse


def _success(
    subagent: str,
    artifacts: list[dict],
    external_actions: list[dict] | None = None,
    summary: str = "OK",
) -> dict:
    return {
        "schema_version": "1.1",
        "subagent": subagent,
        "status": "success",
        "artifacts": artifacts,
        "external_actions": external_actions or [],
        "summary_for_user": summary,
        "warnings": [],
        "errors": [],
    }


def _failure(subagent: str, error: str) -> dict:
    return {
        "schema_version": "1.1",
        "subagent": subagent,
        "status": "failure",
        "artifacts": [],
        "external_actions": [],
        "summary_for_user": f"{subagent} failed.",
        "warnings": [],
        "errors": [error],
    }


# ---- brief-author ----

def test_brief_author_success_validates():
    data = _success(
        subagent="brief-author",
        artifacts=[{"type": "brief_json", "path": "briefs/tebra-vs-athenahealth.json"}],
        external_actions=[{"type": "asana_task", "id": "1234567890"}],
        summary="## Brief Created\nReady for /draft.",
    )
    result = SubagentResponse.model_validate(data)
    assert result.status.value == "success"
    assert result.subagent == "brief-author"
    assert len(result.artifacts) == 1


def test_brief_author_failure_requires_errors():
    """status=failure without errors[] must raise ValidationError."""
    data = _failure("brief-author", "Search Console MCP returned 403")
    result = SubagentResponse.model_validate(data)
    assert result.status.value == "failure"
    assert result.errors[0] == "Search Console MCP returned 403"


def test_brief_author_failure_empty_errors_invalid():
    data = {**_failure("brief-author", "x"), "errors": []}
    with pytest.raises(ValidationError):
        SubagentResponse.model_validate(data)


# ---- draft-writer ----

def test_draft_writer_success_validates():
    data = _success(
        subagent="draft-writer",
        artifacts=[{"type": "draft_md", "path": "drafts/tebra-vs-athenahealth.md"}],
        summary="## Draft Written\nCompliance: passed.",
    )
    result = SubagentResponse.model_validate(data)
    assert result.status.value == "success"
    assert result.artifacts[0].type == "draft_md"


def test_draft_writer_failure_validates():
    data = _failure(
        "draft-writer",
        "Compliance hook denied after 3 attempts: unsourced: 'mortality'",
    )
    result = SubagentResponse.model_validate(data)
    assert result.status.value == "failure"
    assert "mortality" in result.errors[0]


# ---- refresh-auditor ----

def test_refresh_auditor_success_validates():
    data = _success(
        subagent="refresh-auditor",
        artifacts=[
            {"type": "draft_md", "path": "drafts/tebra-features.md"},
            {"type": "audit_log_entry", "path": "audit/compliance.jsonl"},
        ],
        summary="## Refresh Audit\n3 changes identified.",
    )
    result = SubagentResponse.model_validate(data)
    assert result.status.value == "success"
    assert len(result.artifacts) == 2


def test_refresh_auditor_failure_validates():
    data = _failure("refresh-auditor", "No draft found for https://www.tebra.com/unknown")
    result = SubagentResponse.model_validate(data)
    assert result.status.value == "failure"
    assert "No draft found" in result.errors[0]


# ---- schema fixtures (Brief + Draft) ----


def test_brief_fixture_validates():
    """A Brief JSON shaped like brief-author output must pass Brief.model_validate()."""
    data = {
        "schema_version": "1.1",
        "slug": "tebra-vs-athenahealth",
        "asset_type": "comparison",
        "target_intent": {
            "primary_query": "tebra vs athenahealth",
            "query_cluster": ["tebra vs athenahealth", "athenahealth alternative"],
            "buyer_stage": "BOFU",
            "persona": "independent practice operator",
        },
        "proof_points": [
            {
                "claim": "Tebra reduces billing errors by 40%.",
                "source_id": "src-tebra-internal-2024",
                "source_type": "internal_doc",
                "required": True,
            }
        ],
        "competitor_coverage": {"required": ["athenahealth"], "optional": []},
        "sources": [
            {
                "id": "src-tebra-internal-2024",
                "type": "internal_doc",
                "url": "https://www.tebra.com/internal/billing-study",
                "cite_as": "Tebra Internal Billing Study 2024",
            }
        ],
        "asana_task_id": "1234567890",
        "created_at": "2026-04-21T12:00:00Z",
        "created_by": "brief-author",
        "created_by_version": "0.1.0",
    }
    result = Brief.model_validate(data)
    assert result.slug == "tebra-vs-athenahealth"
    assert result.asset_type.value == "comparison"


def test_draft_fixture_validates():
    """A Draft frontmatter shaped like draft-writer output must pass Draft.model_validate()."""
    data = {
        "schema_version": "1.1",
        "slug": "tebra-vs-athenahealth",
        "asset_type": "comparison",
        "status": "draft",
        "brief_path": "briefs/tebra-vs-athenahealth.json",
        "author": {"type": "subagent", "identifier": "draft-writer", "version": "0.1.0"},
        "extractability_score": {
            "schema_present": 0.0,
            "semantic_hierarchy": 0.0,
            "qa_patterns": 0.0,
            "proof_attribution": 0.0,
            "answer_first_structure": 0.0,
            "total": 0.0,
            "scored_at": "2026-04-21T12:00:00Z",
            "scored_by": "citation-auditor",
        },
        "sources": [
            {
                "id": "src-tebra-internal-2024",
                "claims_cited": [
                    {
                        "block_id": "proof-1",
                        "claim": "Tebra reduces billing errors by 40%.",
                        "claim_type": "market_statistic",
                        "citation_api_format": {
                            "type": "document",
                            "source": {
                                "type": "url",
                                "url": "https://www.tebra.com/internal/billing-study",
                            },
                            "citations": True,
                            "title": "Tebra Internal Billing Study 2024",
                        },
                    }
                ],
            }
        ],
        "compliance_hook_log": {
            "last_run": "2026-04-21T12:00:00Z",
            "decision": "pending",
            "claims_checked": 0,
            "claims_sourced": 0,
            "claims_flagged": 0,
        },
        "refresh": {
            "last_refreshed_at": "2026-04-21T12:00:00Z",
            "next_refresh_due": "2026-07-20T12:00:00Z",
            "refresh_cadence_days": 90,
            "recommended_changes": [],
        },
    }
    result = Draft.model_validate(data)
    assert result.slug == "tebra-vs-athenahealth"
    assert result.extractability_score.scored_by == "citation-auditor"
