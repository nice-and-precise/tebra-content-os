"""Validate drafts/*.md: YAML frontmatter schema, brief_path presence, approved_for_claims."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from pydantic import ValidationError

from scripts.schemas import Draft

REPO_ROOT = Path(__file__).parent.parent
DRAFTS_DIR = REPO_ROOT / "drafts"


def _load_registry(drafts_dir: Path) -> dict[str, list[str]]:
    """Return {source_id: approved_for_claims_list} from co-located registry, or empty dict."""
    registry_path = drafts_dir.parent / "sources" / "registry.json"
    if not registry_path.is_file():
        return {}
    try:
        raw = json.loads(registry_path.read_text(encoding="utf-8"))
        return {sid: entry.get("approved_for_claims", []) for sid, entry in raw.items()}
    except (json.JSONDecodeError, AttributeError):
        return {}


def _extract_frontmatter(text: str) -> dict | None:
    """Return parsed YAML frontmatter or None if absent/malformed."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end].strip()
    try:
        result = yaml.safe_load(block)
        return result if isinstance(result, dict) else None
    except yaml.YAMLError:
        return None


def validate(drafts_dir: Path = DRAFTS_DIR) -> int:
    if not drafts_dir.is_dir():
        print(f"ERROR: drafts directory not found: {drafts_dir}", file=sys.stderr)
        return 1

    draft_files = sorted(drafts_dir.glob("*.md"))
    if not draft_files:
        print("OK: 0 draft(s) validated.")
        return 0

    registry = _load_registry(drafts_dir)
    errors: list[str] = []

    for draft_path in draft_files:
        stem = draft_path.stem

        try:
            text = draft_path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{stem}: cannot read file — {exc}")
            continue

        fm = _extract_frontmatter(text)
        if fm is None:
            errors.append(f"{stem}: missing or malformed YAML frontmatter")
            continue

        try:
            draft = Draft.model_validate(fm)
        except ValidationError as exc:
            errors.append(f"{stem}: schema invalid — {exc}")
            continue

        if draft.slug != stem:
            errors.append(
                f"{stem}: 'slug' field '{draft.slug}' does not match filename"
            )

        if draft.brief_path and not (REPO_ROOT / draft.brief_path).is_file():
            errors.append(
                f"{stem}: brief_path '{draft.brief_path}' not found on disk"
            )

        # Check approved_for_claims alignment for any ClaimCited with claim_type set.
        if registry:
            for src in draft.sources:
                approved = registry.get(src.id)
                if approved is None:
                    errors.append(
                        f"{stem}: source '{src.id}' not found in sources/registry.json"
                    )
                    continue
                for cc in src.claims_cited:
                    if cc.claim_type is not None and cc.claim_type.value not in approved:
                        errors.append(
                            f"{stem}: source '{src.id}' block '{cc.block_id}' — "
                            f"claim_type '{cc.claim_type.value}' not in approved_for_claims"
                        )

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
        return 1

    print(f"OK: {len(draft_files)} draft(s) validated.")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
