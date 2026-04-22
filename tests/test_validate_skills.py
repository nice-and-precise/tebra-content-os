"""Tests for scripts/validate_skills.py."""

from pathlib import Path

from scripts.validate_skills import parse_frontmatter, validate

SKILLS_DIR = Path(__file__).parent.parent / ".claude" / "skills"


def write_skill(tmp_path: Path, name: str, content: str) -> Path:
    """Create a skill directory with a SKILL.md file and return the skill dir."""
    skill_dir = tmp_path / name
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(content)
    return skill_dir


def test_all_skills_present():
    expected = {
        "tebra-brand-voice",
        "citation-block-library",
        "healthcare-compliance",
        "bofu-comparison-page",
        "bofu-roi-calculator",
        "bofu-case-study",
        "bofu-implementation-guide",
    }
    found = {d.name for d in SKILLS_DIR.iterdir() if d.is_dir()}
    assert expected.issubset(found), f"Missing skills: {expected - found}"


def test_validate_passes_on_real_skills():
    assert validate(SKILLS_DIR) == 0


def test_validate_fails_missing_skill_md(tmp_path: Path):
    (tmp_path / "my-skill").mkdir()
    assert validate(tmp_path) == 1


def test_validate_fails_missing_name(tmp_path: Path):
    write_skill(tmp_path, "my-skill", "---\ndescription: Use when testing\n---\n# Body\n")
    assert validate(tmp_path) == 1


def test_validate_fails_name_mismatch(tmp_path: Path):
    write_skill(
        tmp_path, "my-skill", "---\nname: other-name\ndescription: Use when testing\n---\n# Body\n"
    )
    assert validate(tmp_path) == 1


def test_validate_fails_bad_name_chars(tmp_path: Path):
    write_skill(
        tmp_path, "my-skill", "---\nname: my (skill)\ndescription: Use when testing\n---\n# Body\n"
    )
    assert validate(tmp_path) == 1


def test_validate_fails_missing_description(tmp_path: Path):
    write_skill(tmp_path, "my-skill", "---\nname: my-skill\n---\n# Body\n")
    assert validate(tmp_path) == 1


def test_validate_fails_description_not_starting_with_use_when(tmp_path: Path):
    write_skill(
        tmp_path,
        "my-skill",
        "---\nname: my-skill\ndescription: Apply this when testing\n---\n# Body\n",
    )
    assert validate(tmp_path) == 1


def test_validate_fails_frontmatter_too_long(tmp_path: Path):
    long_desc = "Use when " + ("x" * 1020)
    write_skill(
        tmp_path, "my-skill", f"---\nname: my-skill\ndescription: {long_desc}\n---\n# Body\n"
    )
    assert validate(tmp_path) == 1


def test_validate_fails_no_frontmatter(tmp_path: Path):
    write_skill(tmp_path, "my-skill", "# Just a heading\nNo frontmatter here.\n")
    assert validate(tmp_path) == 1


def test_validate_empty_skills_dir(tmp_path: Path):
    assert validate(tmp_path) == 1


def _iter_real_skill_fields():
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        parsed = parse_frontmatter(skill_md.read_text())
        assert parsed is not None, f"{skill_dir.name}: no frontmatter"
        yield skill_dir.name, parsed[1]


def test_each_skill_has_name_matching_directory():
    for dir_name, fields in _iter_real_skill_fields():
        assert fields.get("name") == dir_name, (
            f"{dir_name}: name mismatch — got '{fields.get('name')}'"
        )


def test_each_skill_description_starts_with_use_when():
    for dir_name, fields in _iter_real_skill_fields():
        desc = fields.get("description", "")
        assert desc.lower().startswith("use when"), (
            f"{dir_name}: description must start with 'Use when', got '{desc[:40]}'"
        )
