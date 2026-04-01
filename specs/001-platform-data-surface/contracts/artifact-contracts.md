# Artifact Contracts (Feature 1)

These contracts define the durable source-of-truth files for the foundation
feature. They are intentionally limited to metadata, readiness, ownership, and
traceability so later features can consume them without redefining paths or
semantics.

## 1. Canonical Path Inventory Contract

- File: `contracts/canonical_paths.yaml`
- Required keys per item:
  - `path`
  - `path_type`
  - `required`
  - `owner_team`
  - `status`
- Example status values:
  - `confirmed_from_repository_evidence`
  - `inferred_from_requirement_document`
  - `blocked_by_missing_upstream_data`
  - `pending_migration_or_normalization`

## 2. Dataset Readiness Inventory Contract

- File: `contracts/dataset_readiness.json`
- Required keys per dataset:
  - `dataset_id`
  - `canonical_path`
  - `schema_name`
  - `producer_system`
  - `consumer_systems`
  - `readiness_status`
  - `mismatch_refs`
- Readiness records must include evidence notes describing whether the entry is
  confirmed, inferred, blocked, or pending normalization.

## 3. Interface Registry Contract

- File: `contracts/interface_registry.yaml`
- Required keys per interface:
  - `interface_id`
  - `version`
  - `source_system`
  - `target_system`
  - `dataset_refs`
  - `ownership_ref`
  - `status`
- Each registry entry must include a semantic contract note describing the
  producer/consumer meaning for later feature reuse.

## 4. Schema Ownership Map Contract

- File: `contracts/schema_ownership_map.yaml`
- Required keys per schema ownership record:
  - `ownership_id`
  - `schema_name`
  - `producer_owner`
  - `consumer_owners`
  - `blast_radius_notes`
  - `migration_required`
  - `status`
- Ownership records must keep downstream consumer context explicit for blast
  radius review.

## 5. Requirement Traceability Contract

- File: `contracts/requirement_traceability.yaml`
- Required keys per trace row:
  - `requirement_id`
  - `artifact_paths`
  - `coverage_type`
  - `status`
- Trace rows should reference concrete foundation artifacts only; later runtime
  capabilities are intentionally excluded from Feature 1.

## 6. Data Flow Architecture Source Contract

- File: `contracts/data_flow_architecture.mmd`
- Must represent:
  - all six governed datasets,
  - all registered interfaces,
  - ownership/readiness dependency edges.
- The Mermaid source is the canonical architecture diagram and should remain the
  human-editable source of truth for foundation flow changes.

## Shared Enum (all contracts)

- `confirmed_from_repository_evidence`
- `inferred_from_requirement_document`
- `blocked_by_missing_upstream_data`
- `pending_migration_or_normalization`

## Maintenance Notes

- Update path inventory first when any artifact location changes.
- Update readiness inventory and mismatch records together when semantic gaps are
  discovered.
- Never rewrite canonical business meaning to match upstream output.
- Keep status values closed and consistent across all foundation artifacts.
