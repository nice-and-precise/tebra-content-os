import pytest
from pydantic import ValidationError

from scripts.schemas import (
    AuditEvent,
    Brief,
    CitationRecord,
    Draft,
    Source,
    SubagentResponse,
)

# ---- Valid fixture data ----

VALID_BRIEF_DATA: dict = {
    "schema_version": "1.1",
    "slug": "tebra-vs-athenahealth",
    "asset_type": "comparison",
    "target_intent": {
        "primary_query": "tebra vs athenahealth for independent practices",
        "query_cluster": ["tebra vs athenahealth pricing"],
        "buyer_stage": "BOFU",
        "persona": "independent_practice_owner",
    },
    "proof_points": [
        {
            "claim": "Tebra all-in-one EHR reduces vendor sprawl",
            "source_id": "src_tebra_overview",
            "source_type": "internal_doc",
            "required": True,
        }
    ],
    "competitor_coverage": {"required": ["athenahealth"], "optional": []},
    "sources": [
        {
            "id": "src_tebra_overview",
            "type": "internal_doc",
            "path": "sources/internal/tebra-overview.pdf",
            "cite_as": "Tebra Product Overview 2026",
        }
    ],
    "created_at": "2026-04-21T14:30:00Z",
    "created_by": "brief-author-subagent",
    "created_by_version": "0.1.0",
}

VALID_DRAFT_DATA: dict = {
    "schema_version": "1.1",
    "slug": "tebra-vs-athenahealth",
    "asset_type": "comparison",
    "status": "draft",
    "brief_path": "briefs/tebra-vs-athenahealth.json",
    "author": {
        "type": "subagent",
        "identifier": "draft-writer",
        "version": "0.1.0",
    },
    "extractability_score": {
        "total": 4.2,
        "schema_present": 5.0,
        "semantic_hierarchy": 4.0,
        "qa_patterns": 4.0,
        "proof_attribution": 5.0,
        "answer_first_structure": 3.0,
        "scored_at": "2026-04-21T15:45:00Z",
        "scored_by": "citation-auditor-subagent",
    },
    "sources": [
        {
            "id": "src_tebra_overview",
            "claims_cited": [
                {
                    "block_id": "proof-1",
                    "claim": "Tebra all-in-one EHR reduces vendor sprawl",
                    "claim_type": "product_feature",
                    "citation_api_format": {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": "abc123",
                        },
                        "citations": True,
                        "title": "Tebra Product Overview 2026",
                    },
                }
            ],
        }
    ],
    "compliance_hook_log": {
        "last_run": "2026-04-21T15:47:12Z",
        "decision": "allow",
        "claims_checked": 1,
        "claims_sourced": 1,
        "claims_flagged": 0,
    },
    "refresh": {
        "last_refreshed_at": "2026-04-21T15:45:00Z",
        "next_refresh_due": "2026-07-21T00:00:00Z",
        "refresh_cadence_days": 91,
        "recommended_changes": [],
    },
}

VALID_SOURCE_DATA: dict = {
    "schema_version": "1.1",
    "id": "src_tebra_overview",
    "type": "internal_doc",
    "title": "Tebra Product Overview 2026",
    "authority_tier": 1,
    "cite_as": "Tebra Product Overview 2026",
    "path": "sources/internal/tebra-overview.pdf",
    "added_at": "2026-04-15T00:00:00Z",
    "added_by": "jordan@boreready.com",
    "approved_for_claims": ["product_feature", "pricing"],
    "expires_at": "2027-04-15T00:00:00Z",
    "citation_api_ready": True,
}

VALID_CITATION_RECORD_DATA: dict = {
    "type": "document",
    "source": {
        "type": "base64",
        "media_type": "application/pdf",
        "data": "abc123",
    },
    "citations": True,
    "title": "Tebra Product Overview 2026",
}

VALID_AUDIT_EVENT_DATA: dict = {
    "schema_version": "1.1",
    "timestamp": "2026-04-21T15:47:12.342Z",
    "event_type": "compliance_decision",
    "slug": "tebra-vs-athenahealth",
    "actor": {
        "type": "hook",
        "identifier": "pre-tool-use-compliance.sh",
        "version": "0.1.0",
    },
    "decision": "allow",
    "reason": "all claims have approved sources",
    "metadata": {
        "claims_checked": 2,
        "claims_sourced": 2,
        "claims_flagged": 0,
    },
}

VALID_SUBAGENT_RESPONSE_DATA: dict = {
    "schema_version": "1.1",
    "subagent": "brief-author",
    "status": "success",
    "artifacts": [{"type": "brief", "path": "briefs/tebra-vs-athenahealth.json"}],
    "summary_for_user": "Brief ready at briefs/tebra-vs-athenahealth.json.",
    "warnings": [],
    "errors": [],
}


# ---- Valid fixture tests ----


def test_brief_valid():
    brief = Brief.model_validate(VALID_BRIEF_DATA)
    assert brief.slug == "tebra-vs-athenahealth"


def test_draft_valid():
    draft = Draft.model_validate(VALID_DRAFT_DATA)
    assert draft.slug == "tebra-vs-athenahealth"


def test_source_valid():
    source = Source.model_validate(VALID_SOURCE_DATA)
    assert source.id == "src_tebra_overview"


def test_citation_record_valid():
    record = CitationRecord.model_validate(VALID_CITATION_RECORD_DATA)
    assert record.type == "document"


def test_audit_event_valid():
    event = AuditEvent.model_validate(VALID_AUDIT_EVENT_DATA)
    assert event.event_type.value == "compliance_decision"


def test_subagent_response_valid():
    response = SubagentResponse.model_validate(VALID_SUBAGENT_RESPONSE_DATA)
    assert response.status.value == "success"


def test_brief_model_json_schema_smoke():
    schema = Brief.model_json_schema()
    assert isinstance(schema, dict)
    assert "properties" in schema
    assert "slug" in schema["properties"]


# ---- Brief validation rule tests ----


def test_brief_invalid_source_id_not_in_sources():
    data = {
        **VALID_BRIEF_DATA,
        "proof_points": [
            {
                "claim": "some claim",
                "source_id": "nonexistent_source",
                "source_type": "internal_doc",
                "required": True,
            }
        ],
    }
    with pytest.raises(ValidationError, match="not found in sources"):
        Brief.model_validate(data)


def test_brief_invalid_comparison_empty_competitor_coverage():
    data = {**VALID_BRIEF_DATA, "competitor_coverage": {"required": [], "optional": []}}
    with pytest.raises(ValidationError, match="non-empty"):
        Brief.model_validate(data)


def test_brief_invalid_case_study_no_customer_interview():
    data = {
        **VALID_BRIEF_DATA,
        "asset_type": "case_study",
        "competitor_coverage": {"required": [], "optional": []},
        "sources": [
            {
                "id": "src_tebra_overview",
                "type": "internal_doc",
                "path": "sources/internal/tebra-overview.pdf",
                "cite_as": "Tebra Product Overview 2026",
            }
        ],
    }
    with pytest.raises(ValidationError, match="customer_interview"):
        Brief.model_validate(data)


def test_brief_invalid_implementation_guide_no_internal_doc():
    data = {
        **VALID_BRIEF_DATA,
        "asset_type": "implementation_guide",
        "competitor_coverage": {"required": [], "optional": []},
        "sources": [
            {
                "id": "src_tebra_overview",
                "type": "customer_interview",
                "path": "sources/interviews/interview.md",
                "cite_as": "Customer Interview 2026",
            }
        ],
    }
    with pytest.raises(ValidationError, match="internal_doc"):
        Brief.model_validate(data)


# ---- Draft validation rule tests ----


def test_draft_invalid_low_extractability_score():
    data = {
        **VALID_DRAFT_DATA,
        "status": "pmm_review",
        "extractability_score": {
            **VALID_DRAFT_DATA["extractability_score"],
            "total": 2.0,
        },
    }
    with pytest.raises(ValidationError, match="3.5"):
        Draft.model_validate(data)


def test_draft_invalid_compliance_not_allow():
    data = {
        **VALID_DRAFT_DATA,
        "status": "pmm_review",
        "compliance_hook_log": {
            **VALID_DRAFT_DATA["compliance_hook_log"],
            "decision": "deny",
        },
    }
    with pytest.raises(ValidationError, match="allow"):
        Draft.model_validate(data)


def test_draft_invalid_published_missing_url():
    data = {
        **VALID_DRAFT_DATA,
        "status": "published",
        "publish": {
            "webflow_collection_id": None,
            "webflow_item_id": None,
            "published_url": None,
            "published_at": None,
        },
    }
    with pytest.raises(ValidationError, match="published_url"):
        Draft.model_validate(data)


# ---- Source validation rule tests ----


def test_source_invalid_empty_approved_for_claims():
    data = {**VALID_SOURCE_DATA, "approved_for_claims": []}
    with pytest.raises(ValidationError, match="approved_for_claims"):
        Source.model_validate(data)


# ---- AuditEvent validation rule tests ----


def test_audit_event_invalid_compliance_decision_missing_metadata():
    data = {
        **VALID_AUDIT_EVENT_DATA,
        "metadata": {"claims_checked": 2},
    }
    with pytest.raises(ValidationError, match="claims_sourced|claims_flagged"):
        AuditEvent.model_validate(data)


def test_audit_event_invalid_publish_success_missing_metadata():
    data = {
        **VALID_AUDIT_EVENT_DATA,
        "event_type": "publish_success",
        "metadata": {},
    }
    with pytest.raises(ValidationError, match="published_url|webflow_item_id"):
        AuditEvent.model_validate(data)


# ---- SubagentResponse validation rule tests ----


def test_subagent_response_invalid_failure_no_errors():
    data = {**VALID_SUBAGENT_RESPONSE_DATA, "status": "failure", "errors": []}
    with pytest.raises(ValidationError, match="errors"):
        SubagentResponse.model_validate(data)
