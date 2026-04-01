# Data Model — Contract Generation Engine

## Entity: DatasetTarget
- **Purpose**: Canonical description of one governed input dataset.
- **Fields**:
  - `dataset_id` (str)
  - `canonical_input_path` (str)
  - `canonical_contract_output_path` (str)
  - `canonical_dbt_output_path` (str)
  - `readiness_status` (enum: confirmed_from_repository_evidence, inferred_from_requirement_document, blocked_by_missing_upstream_data, pending_migration_or_normalization)
  - `schema_name` (str)

## Entity: ProfiledField
- **Purpose**: Structural and statistical characterization of one field path.
- **Fields**:
  - `field_path` (str, nested path format)
  - `parent_path` (str | null)
  - `observed_types` (list[str])
  - `presence_rate` (float)
  - `null_rate` (float)
  - `numeric_stats` (object | null: min, max, mean)
  - `candidate_enum_values` (list[str] | null)
  - `uniqueness_rate` (float | null)
  - `pattern_candidates` (list[str] | null)
  - `semantic_confidence` (enum: high, medium, low)
  - `uncertainty_note` (str | null)

## Entity: InvariantClause
- **Purpose**: One generated contract clause.
- **Fields**:
  - `clause_id` (str)
  - `field_path` (str | null for dataset-level)
  - `clause_type` (enum: required, range, enum, pattern, positivity, monotonicity_candidate, relationship, uniqueness, dataset_check)
  - `source` (enum: inferred, requirement_defined, merged)
  - `expression` (object)
  - `confidence` (enum: high, medium, low)
  - `supported_in_dbt` (bool)

## Entity: DownstreamContextAnnotation
- **Purpose**: Preserved downstream context for later impact analysis.
- **Fields**:
  - `downstream_systems` (list[str])
  - `consumed_fields` (list[str])
  - `likely_breaking_fields` (list[str])
  - `consumer_change_sensitivity` (list[object])
  - `coverage_status` (enum: full, partial, unknown)
  - `context_sources` (list[str])

## Entity: CanonicalMismatchRecord
- **Purpose**: Observed-vs-canonical difference evidence.
- **Fields**:
  - `dataset_id` (str)
  - `mismatch_type` (enum: filename, shape, field_name, semantic)
  - `canonical_value` (str)
  - `observed_value` (str)
  - `impact_note` (str)
  - `migration_or_normalization_required` (bool)

## Entity: GeneratedContract
- **Purpose**: Primary Bitol-compatible output model.
- **Fields**:
  - `contract_id` (str)
  - `dataset_target` (DatasetTarget)
  - `schema_fields` (list[ProfiledField])
  - `clauses` (list[InvariantClause])
  - `downstream_context` (DownstreamContextAnnotation)
  - `mismatch_records` (list[CanonicalMismatchRecord])
  - `metadata` (GenerationMetadata)

## Entity: DbtSchemaArtifact
- **Purpose**: dbt-compatible counterpart for supported clause types.
- **Fields**:
  - `model_name` (str)
  - `columns` (list[object])
  - `tests` (list[object])
  - `unsupported_clause_mappings` (list[str])

## Entity: GenerationMetadata
- **Purpose**: Run traceability and deterministic diff controls.
- **Fields**:
  - `run_id` (str)
  - `generator_version` (str)
  - `contract_schema_version` (str)
  - `generated_at` (datetime)
  - `input_artifact_hashes` (dict[str, str])
  - `input_record_counts` (dict[str, int])
  - `malformed_line_count` (int)
  - `deterministic_signature` (str)

## Relationships
- `DatasetTarget` 1..1 -> 1..1 `GeneratedContract`
- `GeneratedContract` 1..* -> 0..* `InvariantClause`
- `GeneratedContract` 1..* -> 0..* `ProfiledField`
- `GeneratedContract` 1..1 -> 1..1 `DownstreamContextAnnotation`
- `GeneratedContract` 1..* -> 0..* `CanonicalMismatchRecord`
- `GeneratedContract` 1..1 -> 1..1 `DbtSchemaArtifact`
- `GeneratedContract` 1..1 -> 1..1 `GenerationMetadata`
