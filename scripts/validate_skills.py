"""Validate .claude/skills/*/SKILL.md: YAML frontmatter, name, description format."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / ".claude" / "skills"
MAX_FRONTMATTER_CHARS = 1024

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
_YAML_FIELD_RE = re.compile(r"^(\w+):\s*(.+)$", re.MULTILINE)
_NAME_RE = re.compile(r"^[a-zA-Z0-9-]+$")


def parse_frontmatter(text: str) -> tuple[str, dict[str, str]] | None:
    """Return (raw_block, fields) if frontmatter present, else None."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return None
    return m.group(0), dict(_YAML_FIELD_RE.findall(m.group(1)))


def validate(skills_dir: Path = SKILLS_DIR) -> int:
    if not skills_dir.is_dir():
        print(f"ERROR: skills directory not found: {skills_dir}", file=sys.stderr)
        return 1
    skill_dirs = [
        d for d in skills_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".") and d.name != "__pycache__"
    ]
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

        try:
            raw = skill_md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"{dir_name}: SKILL.md could not be read — {exc}")
            continue
        parsed = parse_frontmatter(raw)
        if parsed is None:
            errors.append(f"{dir_name}: SKILL.md has no YAML frontmatter")
            continue

        block, fields = parsed
        if len(block) > MAX_FRONTMATTER_CHARS:
            errors.append(
                f"{dir_name}: frontmatter exceeds {MAX_FRONTMATTER_CHARS} chars ({len(block)})"
            )

        name = fields.get("name")
        if name is None:
            errors.append(f"{dir_name}: frontmatter missing 'name' field")
        elif not _NAME_RE.match(name):
            errors.append(
                f"{dir_name}: name '{name}' contains invalid chars "
                "(only letters, numbers, hyphens allowed)"
            )
        elif name != dir_name:
            errors.append(
                f"{dir_name}: name '{name}' does not match directory name '{dir_name}'"
            )

        description = fields.get("description")
        if description is None:
            errors.append(f"{dir_name}: frontmatter missing 'description' field")
        elif not description.strip().lower().startswith("use when"):
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
