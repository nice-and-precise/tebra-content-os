from datetime import datetime
from enum import Enum, StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

# ---- Enums ----


class AssetType(StrEnum):
    comparison = "comparison"
    roi_calculator = "roi_calculator"
    case_study = "case_study"
    implementation_guide = "implementation_guide"
    refresh = "refresh"
    quick_answer = "quick_answer"


class BuyerStage(StrEnum):
    TOFU = "TOFU"
    MOFU = "MOFU"
    BOFU = "BOFU"


class SourceType(StrEnum):
    internal_doc = "internal_doc"
    customer_interview = "customer_interview"
    third_party_research = "third_party_research"
    regulatory_document = "regulatory_document"
    peer_reviewed = "peer_reviewed"


class AuthorityTier(int, Enum):
    tier_1 = 1
    tier_2 = 2
    tier_3 = 3
    tier_4 = 4


class ClaimType(StrEnum):
    product_feature = "product_feature"
    pricing = "pricing"
    integration_capability = "integration_capability"
    clinical_outcome = "clinical_outcome"
    regulatory_compliance = "regulatory_compliance"
    customer_testimonial = "customer_testimonial"
    market_statistic = "market_statistic"
    implementation_procedure = "implementation_procedure"


class DraftStatus(StrEnum):
    draft = "draft"
    pmm_review = "pmm_review"
    approved = "approved"
    published = "published"
    archived = "archived"


class AuthorType(StrEnum):
    subagent = "subagent"
    freelancer = "freelancer"
    internal = "internal"


class EventType(StrEnum):
    compliance_decision = "compliance_decision"
    publish_success = "publish_success"
    publish_failure = "publish_failure"
    citation_score = "citation_score"
    refresh_triggered = "refresh_triggered"
    brief_created = "brief_created"
    draft_created = "draft_created"
    source_added = "source_added"
    source_expired = "source_expired"


class SubagentStatus(StrEnum):
    success = "success"
    partial_success = "partial_success"
    failure = "failure"
    blocked_by_hook = "blocked_by_hook"


# ---- Shared nested models ----


class TargetIntent(BaseModel):
    primary_query: str
    query_cluster: list[str]
    buyer_stage: BuyerStage
    persona: str


class ProofPoint(BaseModel):
    claim: str
    source_id: str
    source_type: SourceType
    required: bool


class BofuCta(BaseModel):
    primary: str
    secondary: str | None = None


class CompetitorCoverage(BaseModel):
    required: list[str] = Field(default_factory=list)
    optional: list[str] = Field(default_factory=list)


class BriefSourceRef(BaseModel):
    id: str
    type: SourceType
    path: str | None = None
    url: str | None = None
    cite_as: str


# ---- Brief (/briefs/<slug>.json) ----


class Brief(BaseModel):
    schema_version: Literal["1.0"]
    slug: str
    asset_type: AssetType
    target_intent: TargetIntent
    proof_points: list[ProofPoint]
    required_internal_links: list[str] = Field(default_factory=list)
    bofu_cta: BofuCta | None = None
    schema_hints: list[str] = Field(default_factory=list)
    competitor_coverage: CompetitorCoverage = Field(default_factory=CompetitorCoverage)
    sources: list[BriefSourceRef]
    asana_task_id: str | None = None
    created_at: datetime
    created_by: str
    created_by_version: str

    @model_validator(mode="after")
    def _validate_proof_point_source_ids(self) -> "Brief":
        source_ids = {s.id for s in self.sources}
        for pp in self.proof_points:
            if pp.source_id not in source_ids:
                raise ValueError(
                    f"proof_points source_id '{pp.source_id}' not found in sources"
                )
        return self

    @model_validator(mode="after")
    def _validate_asset_type_constraints(self) -> "Brief":
        if self.asset_type == AssetType.comparison and not self.competitor_coverage.required:
            raise ValueError(
                "asset_type 'comparison' requires competitor_coverage.required to be non-empty"
            )
        if self.asset_type == AssetType.case_study:
            if not any(s.type == SourceType.customer_interview for s in self.sources):
                raise ValueError(
                    "asset_type 'case_study' requires at least one customer_interview source"
                )
        if self.asset_type == AssetType.implementation_guide:
            if not any(s.type == SourceType.internal_doc for s in self.sources):
                raise ValueError(
                    "asset_type 'implementation_guide' requires at least one internal_doc source"
                )
        return self


# ---- Citation record (inline in draft frontmatter) ----


class CitationSource(BaseModel):
    type: Literal["base64", "url", "text", "content"]
    media_type: str | None = None
    data: str | None = None
    url: str | None = None


class CitationRecord(BaseModel):
    type: Literal["document"]
    source: CitationSource
    citations: bool
    title: str
    context: str | None = None


# ---- Draft (/drafts/<slug>.md frontmatter) ----


class DraftAuthor(BaseModel):
    type: AuthorType
    identifier: str
    version: str


class ExtractabilityScore(BaseModel):
    total: float
    schema_present: float
    semantic_hierarchy: float
    qa_patterns: float
    proof_attribution: float
    answer_first_structure: float
    scored_at: datetime
    scored_by: str


class ClaimCited(BaseModel):
    block_id: str
    claim: str
    claim_type: ClaimType | None = None
    citation_api_format: CitationRecord


class DraftSource(BaseModel):
    id: str
    claims_cited: list[ClaimCited]


class ComplianceHookLog(BaseModel):
    last_run: datetime
    decision: str
    claims_checked: int
    claims_sourced: int
    claims_flagged: int


class PublishInfo(BaseModel):
    webflow_collection_id: str | None = None
    webflow_item_id: str | None = None
    published_url: str | None = None
    published_at: datetime | None = None


class RefreshInfo(BaseModel):
    last_refreshed_at: datetime
    next_refresh_due: datetime
    refresh_cadence_days: int
    recommended_changes: list[str] = Field(default_factory=list)


# Statuses that represent advancement past draft — archived is excluded because
# drafts can be archived without ever passing compliance review.
_PAST_DRAFT_STATUSES = {DraftStatus.pmm_review, DraftStatus.approved, DraftStatus.published}


class Draft(BaseModel):
    schema_version: Literal["1.0"]
    slug: str
    asset_type: AssetType
    status: DraftStatus
    brief_path: str
    author: DraftAuthor
    extractability_score: ExtractabilityScore
    sources: list[DraftSource]
    compliance_hook_log: ComplianceHookLog
    publish: PublishInfo = Field(default_factory=PublishInfo)
    refresh: RefreshInfo

    @model_validator(mode="after")
    def _validate_advancement_past_draft(self) -> "Draft":
        if self.status in _PAST_DRAFT_STATUSES:
            if self.extractability_score.total < 3.5:
                raise ValueError(
                    f"extractability_score.total must be >= 3.5 to advance past draft "
                    f"(got {self.extractability_score.total})"
                )
            if self.compliance_hook_log.decision != "allow":
                raise ValueError(
                    f"compliance_hook_log.decision must be 'allow' to advance past draft "
                    f"(got '{self.compliance_hook_log.decision}')"
                )
        return self

    @model_validator(mode="after")
    def _validate_published_fields(self) -> "Draft":
        if self.status == DraftStatus.published:
            if not self.publish.published_url or not self.publish.published_at:
                raise ValueError(
                    "status 'published' requires publish.published_url and publish.published_at"
                )
        return self


# ---- Source registry (/sources/<subdir>/<slug>.json) ----


class Source(BaseModel):
    schema_version: Literal["1.0"]
    id: str
    type: SourceType
    title: str
    authority_tier: AuthorityTier
    cite_as: str
    path: str | None = None
    url: str | None = None
    added_at: datetime
    added_by: str
    approved_for_claims: list[ClaimType]
    not_approved_for_claims: list[ClaimType] = Field(default_factory=list)
    expires_at: datetime
    citation_api_ready: bool

    @field_validator("approved_for_claims")
    @classmethod
    def _approved_for_claims_not_empty(cls, v: list[ClaimType]) -> list[ClaimType]:
        if not v:
            raise ValueError("approved_for_claims must contain at least one claim type")
        return v


# ---- Audit event (/audit/*.jsonl) ----


class AuditActor(BaseModel):
    type: str
    identifier: str
    version: str | None = None


class AuditEvent(BaseModel):
    schema_version: Literal["1.0"]
    timestamp: datetime
    event_type: EventType
    slug: str
    actor: AuditActor
    decision: str | None = None
    reason: str | None = None
    metadata: dict[str, Any] | None = None

    @model_validator(mode="after")
    def _validate_compliance_decision_metadata(self) -> "AuditEvent":
        if self.event_type == EventType.compliance_decision:
            if self.metadata is None:
                raise ValueError("compliance_decision events require metadata")
            required = {"claims_checked", "claims_sourced", "claims_flagged"}
            missing = required - set(self.metadata.keys())
            if missing:
                raise ValueError(f"compliance_decision metadata missing required keys: {missing}")
        return self

    @model_validator(mode="after")
    def _validate_publish_success_metadata(self) -> "AuditEvent":
        if self.event_type == EventType.publish_success:
            if self.metadata is None:
                raise ValueError("publish_success events require metadata")
            required = {"published_url", "webflow_item_id"}
            missing = required - set(self.metadata.keys())
            if missing:
                raise ValueError(f"publish_success metadata missing required keys: {missing}")
        return self


# ---- Subagent output contract ----


class SubagentArtifact(BaseModel):
    type: str
    path: str


class ExternalAction(BaseModel):
    type: str
    id: str | None = None
    url: str | None = None


class SubagentResponse(BaseModel):
    schema_version: Literal["1.0"]
    subagent: str
    status: SubagentStatus
    artifacts: list[SubagentArtifact] = Field(default_factory=list)
    external_actions: list[ExternalAction] = Field(default_factory=list)
    summary_for_user: str
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_failure_has_errors(self) -> "SubagentResponse":
        if self.status == SubagentStatus.failure and not self.errors:
            raise ValueError("failure status requires at least one error in errors[]")
        return self
