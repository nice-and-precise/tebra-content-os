#!/usr/bin/env python3
"""Seeds sources/registry.json with one example source record for manual testing.

Run from repo root:
    python scripts/migrations/seed_registry.py
"""

import json
from pathlib import Path

SEED_SOURCE = {
    "schema_version": "1.1",
    "id": "src_tebra_overview",
    "type": "internal_doc",
    "title": "Tebra Product Overview 2026",
    "authority_tier": 1,
    "cite_as": "Tebra Product Overview 2026",
    "path": "sources/internal/tebra-overview.pdf",
    "url": None,
    "added_at": "2026-04-15T00:00:00Z",
    "added_by": "jordan@boreready.com",
    "approved_for_claims": ["product_feature", "pricing", "integration_capability"],
    "not_approved_for_claims": ["clinical_outcome", "regulatory_compliance"],
    "expires_at": "2027-04-15T00:00:00Z",
    "citation_api_ready": True,
}


def main() -> None:
    registry_path = Path("sources/registry.json")
    registry = {SEED_SOURCE["id"]: SEED_SOURCE}
    with registry_path.open("w") as f:
        json.dump(registry, f, indent=2)
    print(f"Seeded {registry_path} with {len(registry)} source record(s).")


if __name__ == "__main__":
    main()
