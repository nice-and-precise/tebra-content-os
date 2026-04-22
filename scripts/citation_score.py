"""
Extractability rubric scorer for tebra-content-os.

Scores a page against five dimensions (0–5 each); total is the arithmetic mean.
The five dimensions match ExtractabilityScore fields in schemas.py.

CLI usage (called by citation-auditor subagent):
    echo '<signals_json>' | python scripts/citation_score.py

Import usage (tests):
    from scripts.citation_score import score_page, PageSignals
"""

import json
import sys
from dataclasses import dataclass


@dataclass
class PageSignals:
    url: str
    schema_types: list[str]      # JSON-LD @type values found on page
    h1_count: int
    h2_count: int
    h3_count: int
    qa_pair_count: int           # Q&A patterns detected (questions + answers)
    citation_count: int          # <cite> elements + footnote/reference links
    word_count: int
    answer_in_first_paragraph: bool  # direct answer before first section heading


@dataclass
class RubricScore:
    schema_present: float
    semantic_hierarchy: float
    qa_patterns: float
    proof_attribution: float
    answer_first_structure: float
    total: float


_AI_EXTRACTABLE = {"FAQPage", "QAPage", "HowTo"}
_MEDICAL_PRODUCT = {"MedicalWebPage", "Product", "Service", "SoftwareApplication"}
_ARTICLE = {"Article", "BlogPosting", "WebPage", "NewsArticle"}


def _score_schema_present(schema_types: list[str]) -> float:
    if not schema_types:
        return 0.0
    found = set(schema_types)
    if found & _AI_EXTRACTABLE and found & (_MEDICAL_PRODUCT | _ARTICLE):
        return 5.0
    if found & _AI_EXTRACTABLE:
        return 4.0
    if found & _MEDICAL_PRODUCT:
        return 3.0
    if found & _ARTICLE:
        return 2.0
    return 1.0  # schema present but only generic types (Organization, WebSite)


def _score_semantic_hierarchy(h1: int, h2: int, h3: int) -> float:
    if h1 == 0:
        return 0.0
    if h2 == 0:
        return 1.0
    if h3 == 0:
        return 2.0 if h1 == 1 else 1.0
    if h1 == 1 and h2 >= 3 and h3 >= 2:
        return 5.0
    if h1 == 1 and h2 >= 2 and h3 >= 1:
        return 4.0
    if h1 == 1 and (h2 >= 1 or h3 >= 1):
        return 3.0
    return 2.0


def _score_qa_patterns(qa_count: int, has_faq_schema: bool) -> float:
    if qa_count == 0:
        return 0.0
    if qa_count == 1:
        return 1.0
    if qa_count <= 3:
        return 2.0
    if qa_count <= 6:
        return 4.0 if has_faq_schema else 3.0
    if qa_count <= 10:
        return 4.0
    return 5.0


def _score_proof_attribution(citation_count: int) -> float:
    if citation_count == 0:
        return 0.0
    if citation_count <= 2:
        return 1.0
    if citation_count <= 5:
        return 2.0
    if citation_count <= 10:
        return 3.0
    if citation_count <= 15:
        return 4.0
    return 5.0


def _score_answer_first(answer_in_first_paragraph: bool) -> float:
    return 5.0 if answer_in_first_paragraph else 0.0


def score_page(signals: PageSignals) -> RubricScore:
    """Score a page against the extractability rubric. Pure function — no I/O."""
    has_faq_schema = bool(set(signals.schema_types) & _AI_EXTRACTABLE)
    dims = [
        _score_schema_present(signals.schema_types),
        _score_semantic_hierarchy(signals.h1_count, signals.h2_count, signals.h3_count),
        _score_qa_patterns(signals.qa_pair_count, has_faq_schema),
        _score_proof_attribution(signals.citation_count),
        _score_answer_first(signals.answer_in_first_paragraph),
    ]
    total = round(sum(dims) / len(dims), 2)
    return RubricScore(
        schema_present=dims[0],
        semantic_hierarchy=dims[1],
        qa_patterns=dims[2],
        proof_attribution=dims[3],
        answer_first_structure=dims[4],
        total=total,
    )


def main() -> None:
    """CLI entry point. Reads PageSignals JSON from stdin; writes RubricScore JSON to stdout."""
    raw = json.loads(sys.stdin.read())
    signals = PageSignals(
        url=raw["url"],
        schema_types=raw.get("schema_types", []),
        h1_count=raw.get("h1_count", 0),
        h2_count=raw.get("h2_count", 0),
        h3_count=raw.get("h3_count", 0),
        qa_pair_count=raw.get("qa_pair_count", 0),
        citation_count=raw.get("citation_count", 0),
        word_count=raw.get("word_count", 0),
        answer_in_first_paragraph=raw.get("answer_in_first_paragraph", False),
    )
    result = score_page(signals)
    print(json.dumps({
        "schema_present": result.schema_present,
        "semantic_hierarchy": result.semantic_hierarchy,
        "qa_patterns": result.qa_patterns,
        "proof_attribution": result.proof_attribution,
        "answer_first_structure": result.answer_first_structure,
        "total": result.total,
    }))


if __name__ == "__main__":
    main()
