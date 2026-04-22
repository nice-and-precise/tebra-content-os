# Schema migrations

Migration scripts live here. Each script transforms data files from one schema version to the next.

## Naming convention

`v{old}_to_v{new}_{entity}.py`

Examples:
- `v1_to_v2_brief.py` — migrates `/briefs/*.json` from schema_version 1.0 to 2.0
- `v1_to_v2_source.py` — migrates `/sources/**/*.json` from schema_version 1.0 to 2.0

## When to add a migration

Every breaking schema change in `DATA_CONTRACTS.md` requires:
1. A new schema version (e.g., `1.0` → `2.0`)
2. A migration script here
3. Dual-read support in consumers for at least one minor version
4. An entry in `docs/RESEARCH_GAPS_AND_DECISIONS.md` section 2

## Script contract

Each migration script must:
- Accept a single JSON file path as `sys.argv[1]`
- Write the migrated output to stdout as valid JSON
- Exit 0 on success, non-zero on error
- Be idempotent (safe to run twice on the same file)

## Running migrations

```bash
# Migrate a single brief
python scripts/migrations/v1_to_v2_brief.py briefs/tebra-vs-athenahealth.json > /tmp/migrated.json
mv /tmp/migrated.json briefs/tebra-vs-athenahealth.json

# Migrate all briefs
for f in briefs/*.json; do
  python scripts/migrations/v1_to_v2_brief.py "$f" > /tmp/migrated.json && mv /tmp/migrated.json "$f"
done
```

No migration scripts exist yet. This directory is populated at the first schema version bump.
