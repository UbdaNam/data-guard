# Contracts: Schema Evolution Artifacts

## Output Artifacts

- Evolution report:
  - `validation_reports/schema_evolution_{contract_id}.json`
- Migration impact report:
  - `migration_impact_{contract_id}_{timestamp}.json`
- Snapshot store:
  - `schema_snapshots/{contract_id}/snapshot_{timestamp}_{schema_hash}.json`

## Snapshot Contract

Required fields:

- `snapshot_id` (deterministic schema hash)
- `snapshot_timestamp` (UTC ISO-8601)
- `contract_id`
- `schema_hash`
- `source_contract_path`
- `fields[]` (normalized field records)
- `rules[]` (contract-level quality rules)

Behavioral rules:

- Snapshot writes are append-only for materially changed schemas.
- Duplicate schema hash against latest snapshot for same contract MUST not create a new file.
- Snapshot identity and file naming MUST be deterministic.

## Evolution Report Contract

Required sections:

- `analysis_id`
- `contract_id`
- `from_snapshot_id`
- `to_snapshot_id`
- `structured_diff[]`
- `compatibility_verdict`
- `change_summary`
- `warnings[]`
- `context_completeness`

`structured_diff[]` change classes:

- `add_nullable_field`
- `add_required_field`
- `remove_field`
- `rename_field`
- `widen_type`
- `narrow_type`
- `change_enum_values`
- `change_constraints`
- `change_nested_structure`
- `change_semantic_scale`

Compatibility model:

- Per change and aggregate verdict MUST include:
  - `is_backward_compatible`
  - `is_forward_compatible`
  - derived `verdict` (`fully-compatible`, `backward-compatible`, `forward-compatible`, `breaking`)

## Migration Impact Report Contract

Required sections:

- `report_id`
- `analysis_id`
- `contract_id`
- `human_diff_summary`
- `structured_diff[]`
- `compatibility_verdict`
- `affected_consumers[]`
- `migration_checklist[]` (ordered)
- `rollback_guidance[]` (mandatory for breaking changes)
- `urgency` (`low|medium|high|critical`)
- `confidence_change_caused_breakage`
- `enrichment_sources`

Guidance rule:

- Migration checklist entries MUST be specific and actionable (owner, action,
  target, verification), not generic suggestions.

## Determinism and Degradation

- Diff rendering MUST be deterministic (class order + canonical path sort).
- Missing or malformed snapshots MUST emit explicit warnings and completeness flags.
- Missing optional validation/violation context MUST not block outputs.
- Low-confidence rename candidates MUST degrade to add/remove classification.

## Responsibility Boundary

- In scope:
  - schema snapshot writing
  - schema diffing and compatibility classification
  - migration impact output generation
- Out of scope:
  - executing validation runs
  - git-blame attribution
  - final stakeholder-facing report generation
