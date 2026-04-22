"""Tests for scripts/validate_skills.py."""

from pathlib import Path

from scripts.validate_skills import validate

SKILLS_DIR = Path(__file__).parent.parent / ".claude" / "skills"


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
    result = validate(SKILLS_DIR)
    assert result == 0


def test_validate_fails_missing_skill_md(tmp_path: Path):
    (tmp_path / "my-skill").mkdir()
    result = validate(tmp_path)
    assert result == 1


def test_validate_fails_missing_name(tmp_path: Path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("---\ndescription: Use when testing\n---\n# Body\n")
    result = validate(tmp_path)
    assert result == 1


def test_validate_fails_name_mismatch(tmp_path: Path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: other-name\ndescription: Use when testing\n---\n# Body\n"
    )
    result = validate(tmp_path)
    assert result == 1


def test_validate_fails_bad_name_chars(tmp_path: Path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: my (skill)\ndescription: Use when testing\n---\n# Body\n"
    )
    result = validate(tmp_path)
    assert result == 1


def test_validate_fails_missing_description(tmp_path: Path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("---\nname: my-skill\n---\n# Body\n")
    result = validate(tmp_path)
    assert result == 1


def test_validate_fails_description_not_starting_with_use_when(tmp_path: Path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: my-skill\ndescription: Apply this when testing\n---\n# Body\n"
    )
    result = validate(tmp_path)
    assert result == 1


def test_validate_fails_frontmatter_too_long(tmp_path: Path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    long_desc = "Use when " + ("x" * 1020)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: my-skill\ndescription: {long_desc}\n---\n# Body\n"
    )
    result = validate(tmp_path)
    assert result == 1


def test_validate_fails_no_frontmatter(tmp_path: Path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# Just a heading\nNo frontmatter here.\n")
    result = validate(tmp_path)
    assert result == 1


def test_validate_empty_skills_dir(tmp_path: Path):
    result = validate(tmp_path)
    assert result == 1


def test_each_skill_has_name_matching_directory():
    import re

    fm_re = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
    field_re = re.compile(r"^(\w+):\s*(.+)$", re.MULTILINE)

    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        text = skill_md.read_text()
        m = fm_re.match(text)
        assert m, f"{skill_dir.name}: no frontmatter"
        fields = dict(field_re.findall(m.group(1)))
        assert fields.get("name") == skill_dir.name, (
            f"{skill_dir.name}: name mismatch — got '{fields.get('name')}'"
        )


def test_each_skill_description_starts_with_use_when():
    import re

    fm_re = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
    field_re = re.compile(r"^(\w+):\s*(.+)$", re.MULTILINE)

    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        text = skill_md.read_text()
        m = fm_re.match(text)
        assert m, f"{skill_dir.name}: no frontmatter"
        fields = dict(field_re.findall(m.group(1)))
        desc = fields.get("description", "")
        assert desc.lower().startswith("use when"), (
            f"{skill_dir.name}: description must start with 'Use when', got '{desc[:40]}'"
        )
