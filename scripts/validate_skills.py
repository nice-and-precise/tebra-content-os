"""Validate .claude/skills/*/SKILL.md: YAML frontmatter, name, description format."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / ".claude" / "skills"
_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
_YAML_FIELD_RE = re.compile(r"^(\w+):\s*(.+)$", re.MULTILINE)
_MAX_FRONTMATTER_CHARS = 1024
_NAME_RE = re.compile(r"^[a-zA-Z0-9-]+$")


def _parse_frontmatter(text: str) -> dict[str, str] | None:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return None
    block = m.group(1)
    return dict(_YAML_FIELD_RE.findall(block))


def validate(skills_dir: Path = SKILLS_DIR) -> int:
    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and d.name != "__pycache__"]
    if not skill_dirs:
        print(f"ERROR: no skill directories found in {skills_dir}", file=sys.stderr)
        return 1

    errors: list[str] = []

    for skill_dir in sorted(skill_dirs):
        skill_md = skill_dir / "SKILL.md"
        dir_name = skill_dir.name

        if not skill_md.exists():
            errors.append(f"{dir_name}: SKILL.md missing")
            continue

        text = skill_md.read_text()
        fields = _parse_frontmatter(text)

        if fields is None:
            errors.append(f"{dir_name}: SKILL.md has no YAML frontmatter")
            continue

        m = _FRONTMATTER_RE.match(text)
        frontmatter_block = m.group(0) if m else ""
        if len(frontmatter_block) > _MAX_FRONTMATTER_CHARS:
            errors.append(
                f"{dir_name}: frontmatter exceeds {_MAX_FRONTMATTER_CHARS} chars "
                f"({len(frontmatter_block)})"
            )

        if "name" not in fields:
            errors.append(f"{dir_name}: frontmatter missing 'name' field")
        elif not _NAME_RE.match(fields["name"]):
            errors.append(
                f"{dir_name}: name '{fields['name']}' contains invalid chars "
                "(only letters, numbers, hyphens allowed)"
            )
        elif fields["name"] != dir_name:
            errors.append(
                f"{dir_name}: name '{fields['name']}' does not match directory name '{dir_name}'"
            )

        if "description" not in fields:
            errors.append(f"{dir_name}: frontmatter missing 'description' field")
        elif not fields["description"].strip().lower().startswith("use when"):
            errors.append(f"{dir_name}: description must start with 'Use when'")

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
        return 1

    print(f"OK: {len(skill_dirs)} skill(s) validated.")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
