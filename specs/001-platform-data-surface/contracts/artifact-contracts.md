# Artifact Contracts (Feature 1)

## 1. Canonical Path Inventory Contract

- File: `contracts/canonical_paths.yaml`
- Required keys per item:
  - `path`
  - `path_type`
  - `required`
  - `owner_team`
  - `status`

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

## 5. Requirement Traceability Contract

- File: `contracts/requirement_traceability.yaml`
- Required keys per trace row:
  - `requirement_id`
  - `artifact_paths`
  - `coverage_type`
  - `status`

## 6. Data Flow Architecture Source Contract

- File: `contracts/data_flow_architecture.mmd`
- Must represent:
  - all six governed datasets,
  - all registered interfaces,
  - ownership/readiness dependency edges.

## Shared Enum (all contracts)

- `confirmed_from_repository_evidence`
- `inferred_from_requirement_document`
- `blocked_by_missing_upstream_data`
- `pending_migration_or_normalization`
