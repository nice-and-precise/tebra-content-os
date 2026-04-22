from __future__ import annotations

import os
import sys
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml


def append_refresh(draft_path: Path, changes: list[str]) -> None:
    if not draft_path.exists():
        raise FileNotFoundError(draft_path)

    content = draft_path.read_text()
    if not content.startswith("---"):
        raise ValueError(f"draft has no YAML frontmatter: {draft_path}")

    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"draft has malformed frontmatter (no closing ---): {draft_path}")

    _, fm_str, body = parts
    meta = yaml.safe_load(fm_str) or {}

    if "refresh" not in meta:
        raise ValueError(f"draft has no 'refresh' key in frontmatter: {draft_path}")

    refresh = meta["refresh"]
    cadence = refresh.get("refresh_cadence_days", 90)
    existing: list[str] = refresh.get("recommended_changes") or []

    now = datetime.now(UTC)
    refresh["recommended_changes"] = list(dict.fromkeys([*existing, *changes]))
    refresh["last_refreshed_at"] = now.isoformat()
    refresh["next_refresh_due"] = (now + timedelta(days=cadence)).isoformat()

    new_content = f"---\n{yaml.dump(meta)}---{body}"
    with tempfile.NamedTemporaryFile(
        mode="w", dir=draft_path.parent, prefix=".refresh-", suffix=".md", delete=False
    ) as tmp:
        tmp.write(new_content)
        tmp_path = Path(tmp.name)
    try:
        os.replace(tmp_path, draft_path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def main() -> None:
    if len(sys.argv) < 3:
        print(
            f"Usage: {sys.argv[0]} <draft_path> <change1> [<change2> ...]",
            file=sys.stderr,
        )
        sys.exit(1)

    draft_path = Path(sys.argv[1])
    changes = sys.argv[2:]

    try:
        append_refresh(draft_path, changes)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Updated refresh block in {draft_path} ({len(changes)} changes appended).")


if __name__ == "__main__":
    main()
