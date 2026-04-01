# Data Model: Platform Foundation and Canonical Data Surface

## Entity: CanonicalPathEntry

- Description: One authoritative file or directory path for platform operation.
- Fields:
  - `path` (string, required)
  - `path_type` (enum: `file` | `directory`)
  - `domain` (enum: `contracts` | `generated_contracts` | `validation_reports` | `violation_log` | `schema_snapshots` | `enforcer_report` | `outputs` | `docs`)
  - `required` (boolean)
  - `owner_team` (string)
  - `status` (enum: controlled readiness/provenance set)

## Entity: DatasetRegistration

- Description: Governed dataset definition for one canonical input/output surface.
- Fields:
  - `dataset_id` (string, unique)
  - `canonical_path` (string, references `CanonicalPathEntry.path`)
  - `schema_name` (string)
  - `producer_system` (string)
  - `consumer_systems` (array[string])
  - `semantic_summary` (string)
  - `readiness_status` (enum)
  - `mismatch_refs` (array[string], optional)

## Entity: InterfaceRegistryEntry

- Description: Inter-system contract boundary and movement definition.
- Fields:
  - `interface_id` (string, unique)
  - `version` (string)
  - `source_system` (string)
  - `target_system` (string)
  - `dataset_refs` (array[string], references `DatasetRegistration.dataset_id`)
  - `schema_refs` (array[string])
  - `ownership_ref` (string, references `SchemaOwnershipRecord.ownership_id`)
  - `status` (enum)

## Entity: SchemaOwnershipRecord

- Description: Producer/consumer ownership and downstream impact contract.
- Fields:
  - `ownership_id` (string, unique)
  - `schema_name` (string)
  - `producer_owner` (string)
  - `consumer_owners` (array[string])
  - `blast_radius_notes` (string)
  - `migration_required` (boolean)
  - `status` (enum)

## Entity: SchemaMismatchRecord

- Description: Evidence-backed difference between actual upstream and canonical target.
- Fields:
  - `mismatch_id` (string, unique)
  - `dataset_id` (string, references `DatasetRegistration.dataset_id`)
  - `mismatch_type` (enum: `filename` | `shape` | `field_semantics`)
  - `observed_value` (string or object)
  - `canonical_value` (string or object)
  - `business_meaning_risk` (string)
  - `resolution_type` (enum: `migration` | `normalization` | `both`)
  - `status` (enum)

## Entity: RequirementTraceRecord

- Description: Link between feature/platform requirement and concrete artifact coverage.
- Fields:
  - `requirement_id` (string)
  - `artifact_paths` (array[string])
  - `coverage_type` (enum: `direct` | `partial` | `planned`)
  - `status` (enum)

## Relationships

- `DatasetRegistration.canonical_path` -> `CanonicalPathEntry.path` (many-to-one)
- `InterfaceRegistryEntry.dataset_refs` -> `DatasetRegistration.dataset_id` (many-to-many)
- `InterfaceRegistryEntry.ownership_ref` -> `SchemaOwnershipRecord.ownership_id` (many-to-one)
- `SchemaMismatchRecord.dataset_id` -> `DatasetRegistration.dataset_id` (many-to-one)
- `RequirementTraceRecord.artifact_paths` -> multiple artifact files/paths

## Validation Rules

- Every governed dataset must map to exactly one canonical path.
- Every artifact record must include one allowed status enum value.
- Every mismatch must specify `resolution_type` and never alter canonical target values.
- `coverage_type=direct` requires at least one existing artifact path.

## State Transitions

Status enum transitions (allowed):

- `inferred_from_requirement_document` -> `confirmed_from_repository_evidence`
- `blocked_by_missing_upstream_data` -> `pending_migration_or_normalization`
- `pending_migration_or_normalization` -> `confirmed_from_repository_evidence`

Disallowed:

- Any transition that bypasses mismatch capture when canonical divergence exists.
