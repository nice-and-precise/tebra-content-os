"""
Migration: Draft schema 1.0 → 1.1

Breaking change: ClaimCited.claim_type promoted from Optional[ClaimType] to ClaimType (required).

All production drafts at time of migration already had claim_type set on every ClaimCited entry,
so this migration is a no-op for the v1 data set. The stub exists to satisfy the §3.3 policy
(every breaking schema change ships with a migration script) and to serve as the starting point
if any pre-1.1 draft is encountered during an import.

Usage:
    python3 -m scripts.migrations.draft_1_0_to_1_1 <draft.md>

The script reads the draft frontmatter, checks for ClaimCited entries with missing claim_type,
and raises ValueError listing all offending block_ids. No automatic default is applied because
claim_type is domain-specific and cannot be inferred safely without operator input.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml


def migrate(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{path}: no YAML frontmatter found")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path}: malformed frontmatter (no closing ---)")
    fm = yaml.safe_load(parts[1]) or {}

    missing: list[str] = []
    for src in fm.get("sources", []):
        for cc in src.get("claims_cited", []):
            if cc.get("claim_type") is None:
                missing.append(cc.get("block_id", "<unknown>"))

    if missing:
        raise ValueError(
            f"{path}: the following ClaimCited entries are missing claim_type "
            f"(must be set by operator before upgrading to schema 1.1): {missing}"
        )

    print(f"{path}: OK — all ClaimCited entries have claim_type set. No changes needed.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 -m scripts.migrations.draft_1_0_to_1_1 <draft.md>")
        sys.exit(1)
    for arg in sys.argv[1:]:
        migrate(Path(arg))
