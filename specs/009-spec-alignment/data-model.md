# Data Model: Spec Alignment and Platform Completion

## 1. SubscriptionsRegistry

Represents the canonical subscription-topology artifact.

**Fields**

- `version`: registry schema version
- `generated_at`: generation timestamp
- `interfaces`: list of interface records

**Relationships**

- Consumed by attribution, blast radius, and schema evolution
- Cross-checked against lineage snapshots

## 2. SubscriptionInterface

Represents one governed producer-consumer interface.

**Fields**

- `interface_id`
- `producer`
- `consumer`
- `schema_name` or `record_type`
- `criticality`
- `dependency_type` or `directness`

**Behavioral notes**

- Direct subscribers are first-hop descendants from a violating node.
- Transitive downstream nodes are descendants beyond the first hop.
- Contamination depth is the maximum hop distance from the violating node to any downstream node.

## 3. NumericBaselineRecord

Represents the authoritative drift baseline for a governed numeric field.

**Fields**

- `contract_or_surface_id`
- `field_name`
- `sample_count`
- `mean`
- `standard_deviation`
- `distribution_summary`

**Storage**

- `schema_snapshots/baselines.json`

## 4. EmbeddingBaselineRecord

Represents the centroid baseline used for cosine-distance embedding drift.

**Fields**

- `surface_id`
- `baseline_token_hash`
- `centroid_vector`
- `dimensions`
- `generated_at`

**Storage**

- `schema_snapshots/ai/<surface_id>/baseline_token_hash_v1.json`

## 5. ValidationResult

Represents the output of the validation runner in AUDIT/WARN/ENFORCE modes.

**Fields**

- `mode`
- `checks_passed`
- `total_checks`
- `drift_results`
- `confidence_results`
- `errors`

**Behavioral notes**

- Missing columns remain `ERROR`.
- Drift and confidence checks are independent.

## 6. AttributionCandidate

Represents a ranked candidate for violation attribution.

**Fields**

- `candidate_id`
- `confidence`
- `days_since_commit`
- `lineage_hops`
- `evidence_summary`
- `rank`

**Behavioral notes**

- At most five candidates.
- Return at least one candidate when evidence exists.

## 7. BlastRadiusSummary

Represents downstream impact from a violation or breaking change.

**Fields**

- `affected_nodes`
- `affected_pipelines`
- `direct_subscribers`
- `transitive_downstream_nodes`
- `contamination_depth`

## 8. SchemaEvolutionFinding

Represents compatibility and migration impact.

**Fields**

- `changed_field`
- `source_type`
- `target_type`
- `severity`
- `urgency`
- `consumers`
- `failure_modes`
- `rollback_requirements`
- `baseline_reestablishment_requirements`

## 9. AIEnforcementResult

Represents prompt validation, embedding drift, and structured output compliance.

**Fields**

- `prompt_validation_status`
- `quarantined_inputs`
- `embedding_drift_distance`
- `structured_output_violation_rate`
- `warn_threshold_exceeded`

## 10. ReportAction

Represents a deterministic remediation recommendation.

**Fields**

- `priority`
- `file_path`
- `field`
- `contract_clause`
- `source_evidence`
- `recommended_step`

**Behavioral notes**

- Derived from top violations or schema changes.
- Narrative enrichment must not change the ranked action list.
