"""Validate sources/registry.json: Pydantic schema, on-disk file presence, expiry."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError

from scripts.schemas import Source

REPO_ROOT = Path(__file__).parent.parent
REGISTRY_PATH = REPO_ROOT / "sources" / "registry.json"
EXPIRY_WARN_DAYS = 30


def validate(registry_path: Path = REGISTRY_PATH) -> int:
    if not registry_path.is_file():
        print(f"ERROR: registry not found: {registry_path}", file=sys.stderr)
        return 1

    try:
        raw = registry_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: cannot read registry — {exc}", file=sys.stderr)
        return 1

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: registry is not valid JSON — {exc}", file=sys.stderr)
        return 1

    if not isinstance(data, dict) or not data:
        print("ERROR: registry must be a non-empty JSON object", file=sys.stderr)
        return 1

    errors: list[str] = []
    warnings: list[str] = []
    now = datetime.now(tz=UTC)

    for source_id, record in data.items():
        try:
            source = Source.model_validate(record)
        except ValidationError as exc:
            errors.append(f"{source_id}: schema invalid — {exc}")
            continue

        if source.id != source_id:
            errors.append(
                f"{source_id}: 'id' field '{source.id}' does not match registry key"
            )

        if source.path is not None and not (REPO_ROOT / source.path).is_file():
            errors.append(f"{source_id}: path '{source.path}' not found on disk — expected a file")

        expires_at = source.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        delta_days = (expires_at - now).days
        if delta_days < 0:
            errors.append(
                f"{source_id}: expired {-delta_days} day(s) ago (expires_at: {expires_at.date()})"
            )
        elif delta_days < EXPIRY_WARN_DAYS:
            warnings.append(
                f"{source_id}: expires in {delta_days} day(s) — renewal needed soon"
            )

    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  {w}")

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
        return 1

    print(f"OK: {len(data)} source(s) validated.")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
