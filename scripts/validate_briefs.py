"""Validate briefs/*.json: Pydantic schema, slug/filename consistency, registry membership."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import ValidationError

from scripts.schemas import Brief

REPO_ROOT = Path(__file__).parent.parent
BRIEFS_DIR = REPO_ROOT / "briefs"


def _load_registry_ids(briefs_dir: Path) -> set[str]:
    """Return source IDs from the registry co-located with briefs_dir, or empty set."""
    registry_path = briefs_dir.parent / "sources" / "registry.json"
    if not registry_path.is_file():
        return set()
    try:
        raw = json.loads(registry_path.read_text(encoding="utf-8"))
        return set(raw.keys())
    except (json.JSONDecodeError, AttributeError):
        return set()


def validate(briefs_dir: Path = BRIEFS_DIR) -> int:
    if not briefs_dir.is_dir():
        print(f"ERROR: briefs directory not found: {briefs_dir}", file=sys.stderr)
        return 1

    brief_files = sorted(briefs_dir.glob("*.json"))
    if not brief_files:
        print("OK: 0 brief(s) validated.")
        return 0

    registry_ids = _load_registry_ids(briefs_dir)
    errors: list[str] = []

    for brief_path in brief_files:
        stem = brief_path.stem

        try:
            raw = brief_path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{stem}: cannot read file — {exc}")
            continue

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{stem}: invalid JSON — {exc}")
            continue

        try:
            brief = Brief.model_validate(data)
        except ValidationError as exc:
            errors.append(f"{stem}: schema invalid — {exc}")
            continue

        if brief.slug != stem:
            errors.append(
                f"{stem}: 'slug' field '{brief.slug}' does not match filename"
            )

        # Verify every source cited in the brief exists in the registry.
        if registry_ids:
            for src in brief.sources:
                if src.id not in registry_ids:
                    errors.append(
                        f"{stem}: source '{src.id}' not found in sources/registry.json"
                    )

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
        return 1

    print(f"OK: {len(brief_files)} brief(s) validated.")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
