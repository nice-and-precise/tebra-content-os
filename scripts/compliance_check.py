"""
Compliance check: detect unsourced medical claims in draft content.

CLI usage (called by the PreToolUse hook):
    echo "<content>" | python scripts/compliance_check.py <slug> <registry_path> [<audit_path>]

Import usage (tests, compliance-qa subagent):
    from scripts.compliance_check import check_draft_content, CheckResult
"""

import contextlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from scripts.schemas import AuditActor, AuditEvent, EventType

# Medical claim patterns — language that requires source attribution
MEDICAL_PATTERNS = [
    re.compile(r'(?:reduces?|improves?|increases?|decreases?|lowers?|cuts?)\s+(?:\w+\s+){0,3}by\s+\d+\s*%', re.I),  # noqa: E501
    re.compile(r'\d+\s*%\s+(?:reduction|improvement|increase|decrease|accuracy|efficacy|success|survival|rate)\b', re.I),  # noqa: E501
    re.compile(r'\b(?:mortality|morbidity|adverse\s+event|clinical\s+outcome)\b', re.I),
    re.compile(r'(?:clinically\s+proven|FDA[-\s]approved|CE[-\s]marked|HIPAA[-\s]compliant)\b', re.I),  # noqa: E501
    re.compile(r'\b\d+\s*(?:mg|mcg|mL|IU)\b', re.I),
    re.compile(r'(?:diagnos(?:es?|ing)|treats?|cures?|prevents?)\s+(?:cancer|diabetes|disease|disorder|condition)\b', re.I),  # noqa: E501
    re.compile(r'\d+\s*[xX×]\s+(?:more|faster|better|safer|accurate)\b', re.I),
]


@dataclass
class CheckResult:
    decision: str  # "allow", "ask", or "deny"
    reason: str
    claims_checked: int
    claims_sourced: int
    claims_flagged: int


def detect_claims(text: str) -> list[str]:
    """Return matched claim strings from text using medical claim patterns."""
    return [m.group(0) for pattern in MEDICAL_PATTERNS for m in pattern.finditer(text)]


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Split YAML frontmatter from body. Returns ({}, full_content) if no frontmatter."""
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        meta = {}
    return meta, parts[2]


def load_registry(registry_path: Path) -> dict[str, Any]:
    """Load source registry JSON. Returns {} if file not found."""
    if not registry_path.exists():
        return {}
    with registry_path.open() as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"registry JSON is malformed: {e}") from e
    if not isinstance(data, dict):
        raise RuntimeError(f"registry JSON must be an object, got {type(data).__name__}")
    return data


def _get_cited_claims(meta: dict[str, Any]) -> dict[str, tuple[str, str | None]]:
    """Return {cited_claim_text_lower: (source_id, claim_type)} from draft frontmatter sources."""
    cited: dict[str, tuple[str, str | None]] = {}
    for src in meta.get("sources", []):
        source_id = src.get("id", "")
        for cc in src.get("claims_cited", []):
            claim_text = cc.get("claim", "").lower()
            if claim_text:
                cited[claim_text] = (source_id, cc.get("claim_type"))
    return cited


def _normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', text.lower()).strip().strip('.,;:')


def _find_citation(
    matched_text: str, cited: dict[str, tuple[str, str | None]]
) -> tuple[str, str | None] | None:
    """Find (source_id, claim_type) where cited claim text matches the detected claim."""
    normalized_match = _normalize(matched_text)
    for claim_text, (source_id, claim_type) in cited.items():
        if _normalize(claim_text) == normalized_match:
            return source_id, claim_type
    return None


def _validate_source(
    source_id: str, claim_type: str | None, registry: dict[str, Any]
) -> tuple[bool, str]:
    """Check: source exists, not expired, not tier 4, approved for claim_type."""
    entry = registry.get(source_id)
    if entry is None:
        return False, f"source '{source_id}' not in registry"
    expires_at_str = entry.get("expires_at")
    if expires_at_str:
        try:
            expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
            if expires_at < datetime.now(UTC):
                return False, f"source '{source_id}' expired at {expires_at_str}"
        except ValueError:
            return False, f"source '{source_id}' has unparseable expires_at: {expires_at_str!r}"
    if entry.get("authority_tier") == 4:
        return False, f"source '{source_id}' is tier 4 (not citable)"
    if claim_type is not None:
        approved = entry.get("approved_for_claims", [])
        if claim_type not in approved:
            return False, (
                f"source '{source_id}' not approved for claim_type '{claim_type}' "
                f"(approved: {approved})"
            )
    return True, "ok"


def check_draft_content(content: str, registry_path: Path) -> CheckResult:
    """Run compliance check on draft content string. Core importable entry point."""
    meta, body = parse_frontmatter(content)
    registry = load_registry(registry_path)
    cited = _get_cited_claims(meta)
    detected = detect_claims(body)

    claims_checked = len(detected)
    claims_sourced = 0
    claims_flagged = 0
    flagged_reasons: list[str] = []

    for matched_text in detected:
        citation = _find_citation(matched_text, cited)
        if citation is None:
            claims_flagged += 1
            flagged_reasons.append(f"unsourced: '{matched_text[:60]}'")
        else:
            source_id, claim_type = citation
            valid, reason = _validate_source(source_id, claim_type, registry)
            if valid:
                claims_sourced += 1
            else:
                claims_flagged += 1
                flagged_reasons.append(reason)

    if claims_flagged > 0:
        return CheckResult(
            decision="deny",
            reason="; ".join(flagged_reasons[:3]),
            claims_checked=claims_checked,
            claims_sourced=claims_sourced,
            claims_flagged=claims_flagged,
        )
    return CheckResult(
        decision="allow",
        reason="all claims sourced" if claims_checked > 0 else "no medical claims detected",
        claims_checked=claims_checked,
        claims_sourced=claims_sourced,
        claims_flagged=claims_flagged,
    )


def _write_audit_event(slug: str, result: CheckResult, audit_path: Path) -> None:
    event = AuditEvent(
        schema_version="1.1",
        timestamp=datetime.now(UTC),
        event_type=EventType.compliance_decision,
        slug=slug,
        actor=AuditActor(
            type="hook",
            identifier="pre-tool-use-compliance.sh",
            version="0.1.0",
        ),
        decision=result.decision,
        reason=result.reason,
        metadata={
            "claims_checked": result.claims_checked,
            "claims_sourced": result.claims_sourced,
            "claims_flagged": result.claims_flagged,
        },
    )
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    with audit_path.open("a") as f:
        f.write(event.model_dump_json() + "\n")


def main() -> None:
    """CLI entry point. Reads content from stdin; writes JSON result to stdout."""
    content = sys.stdin.read()
    slug = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    registry_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("sources/registry.json")
    audit_path = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("audit/compliance.jsonl")

    result = check_draft_content(content, registry_path)
    print(json.dumps({"decision": result.decision, "reason": result.reason}))
    # Audit write failure must never swallow the decision — MEDIUM-2 fix.
    with contextlib.suppress(OSError):
        _write_audit_event(slug, result, audit_path)

    if result.decision in ("deny", "ask"):
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
