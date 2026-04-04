# Data Model: Schema Evolution Intelligence

## Entity: SchemaSnapshot

- Purpose: Immutable normalized schema state for one governed contract at one point in time.
- Fields:
  - `snapshot_id` (string, deterministic hash)
  - `snapshot_timestamp` (ISO-8601 UTC)
  - `contract_id` (string)
  - `schema_version` (string | null)
  - `schema_hash` (string)
  - `source_contract_path` (string)
  - `fields` (list[`NormalizedField`])
  - `rules` (list[`ContractRule`])
  - `metadata` (object)

## Entity: NormalizedField

- Purpose: Canonical field representation for deterministic comparison.
- Fields:
  - `path` (string; canonical dotted path)
  - `type` (string)
  - `nullable` (bool)
  - `required` (bool)
  - `enum_values` (list[string] | null)
  - `pattern` (string | null)
  - `minimum` (number | null)
  - `maximum` (number | null)
  - `nested_kind` (enum: `scalar`, `object`, `array`, `map`)
  - `raw_constraints` (object)

## Entity: ContractRule

- Purpose: Contract-level quality rule that may be independent of individual field diffs.
- Fields:
  - `rule_id` (string)
  - `rule_scope` (enum: `field`, `dataset`)
  - `rule_type` (string)
  - `rule_payload` (object)

## Entity: FieldMatch

- Purpose: Explain how fields from two snapshots were matched.
- Fields:
  - `from_path` (string | null)
  - `to_path` (string | null)
  - `match_type` (enum: `exact`, `explicit_rename`, `heuristic_rename`, `unmatched`)
  - `confidence` (float 0..1)
  - `evidence` (list[string])

## Entity: SchemaChange

- Purpose: Atomic schema change unit.
- Fields:
  - `change_id` (string)
  - `change_class` (enum)
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
  - `from_field` (`NormalizedField` | null)
  - `to_field` (`NormalizedField` | null)
  - `details` (object)
  - `compatibility` (`CompatibilityAssessment`)

## Entity: CompatibilityAssessment

- Purpose: Dual-axis compatibility result per change and for aggregate verdict.
- Fields:
  - `is_backward_compatible` (bool)
  - `is_forward_compatible` (bool)
  - `verdict` (enum: `fully-compatible`, `backward-compatible`, `forward-compatible`, `breaking`)
  - `rationale` (string)

## Entity: ConsumerImpact

- Purpose: Per-consumer impact and likely failure characterization.
- Fields:
  - `consumer_id` (string)
  - `interface_id` (string | null)
  - `ownership_id` (string | null)
  - `likely_failure_modes` (list[string])
  - `impact_severity` (enum: `low`, `medium`, `high`, `critical`)

## Entity: MigrationAction

- Purpose: Ordered, specific, actionable migration step.
- Fields:
  - `order` (int)
  - `owner` (string)
  - `action` (string)
  - `target` (string)
  - `verification` (string)
  - `rollback_step` (string | null)

## Entity: SchemaEvolutionReport

- Purpose: Deterministic analysis report written per contract.
- Fields:
  - `analysis_id` (string)
  - `contract_id` (string)
  - `from_snapshot_id` (string | null)
  - `to_snapshot_id` (string)
  - `change_summary` (object)
  - `structured_diff` (list[`SchemaChange`])
  - `compatibility_verdict` (`CompatibilityAssessment`)
  - `determinism_keys` (object)
  - `warnings` (list[string])
  - `context_completeness` (enum: `complete`, `partial`, `minimal`)

## Entity: MigrationImpactReport

- Purpose: Operational migration intelligence output.
- Fields:
  - `report_id` (string)
  - `analysis_id` (string)
  - `contract_id` (string)
  - `human_diff_summary` (string)
  - `structured_diff` (list[`SchemaChange`])
  - `compatibility_verdict` (`CompatibilityAssessment`)
  - `affected_consumers` (list[`ConsumerImpact`])
  - `migration_checklist` (list[`MigrationAction`])
  - `rollback_guidance` (list[string])
  - `urgency` (enum: `low`, `medium`, `high`, `critical`)
  - `confidence_change_caused_breakage` (float 0..1)
  - `enrichment_sources` (object)

## Relationships

- `SchemaSnapshot` 1 -> many `NormalizedField`
- `SchemaSnapshot` 1 -> many `ContractRule`
- Snapshot pair -> many `FieldMatch`
- `FieldMatch` and rules -> many `SchemaChange`
- `SchemaChange` 1 -> 1 `CompatibilityAssessment`
- Aggregated changes -> 1 `SchemaEvolutionReport`
- `SchemaEvolutionReport` 1 -> 1 `MigrationImpactReport`
- `MigrationImpactReport` 1 -> many `ConsumerImpact`
- `MigrationImpactReport` 1 -> many `MigrationAction`

## Validation Rules

- Snapshot IDs MUST be deterministic for identical normalized schema payloads.
- `structured_diff` MUST be stable in class-first then path ordering.
- Heuristic rename with confidence below threshold MUST be downgraded to add/remove.
- Every `breaking` verdict MUST have at least one migration checklist action and rollback guidance.
- Missing optional context MUST not block report generation; completeness flag MUST downgrade accordingly.

## State Transitions

1. `snapshot_written` -> snapshot persisted or dedupe-skipped.
2. `pair_selected` -> comparison pair resolved (latest/previous or explicit pair).
3. `diff_computed` -> flat+nested changes generated.
4. `classified` -> compatibility verdicts assigned.
5. `enriched` -> optional Feature 1/3/4 context applied.
6. `rendered` -> deterministic evolution + migration outputs emitted.
