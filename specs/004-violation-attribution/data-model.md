# Data Model: Violation Attribution and Blast Radius Analysis

## Entity: AttributionEligibleResult

- Purpose: Normalized Feature 3 validation result that is eligible for attribution.
- Fields:
  - `report_id` (string)
  - `contract_id` (string | null)
  - `dataset_id` (string | null)
  - `snapshot_id` (string)
  - `detected_at` (ISO-8601 string)
  - `check_id` (string)
  - `check_type` (string)
  - `status` (enum: `FAIL`, `ERROR`)
  - `column_name` (string | null)
  - `eligibility_class` (enum)
  - `skip_reason` (string | null)

## Entity: SchemaAnchor

- Purpose: Governed schema/interface anchor derived from check mapping.
- Fields:
  - `anchor_id` (string)
  - `contract_id` (string | null)
  - `dataset_id` (string | null)
  - `field_path` (string | null)
  - `dataset_rule` (string | null)
  - `interface_id` (string | null)
  - `ownership_id` (string | null)
  - `mapping_confidence` (float 0..1)

## Entity: LineageNode

- Purpose: Node in selected Week 4 lineage graph.
- Fields:
  - `node_id` (string)
  - `dataset_id` (string | null)
  - `interface_id` (string | null)
  - `producer` (string | null)
  - `consumers` (list[string])
  - `metadata` (object)

## Entity: LineagePathEvidence

- Purpose: Captures upstream traversal evidence for one candidate origin.
- Fields:
  - `source_anchor_id` (string)
  - `path_node_ids` (list[string])
  - `hop_count` (int)
  - `stop_reason` (enum: `external_boundary`, `repository_root`, `no_upstream_nodes`, `max_hops`)
  - `is_complete` (bool)

## Entity: CommitEvidence

- Purpose: Git-derived evidence attached to candidate files.
- Fields:
  - `file_path` (string)
  - `commit_hash` (string)
  - `author_name` (string)
  - `author_email` (string)
  - `authored_at` (ISO-8601 string)
  - `summary` (string)
  - `line_start` (int | null)
  - `line_end` (int | null)
  - `blame_used` (bool)

## Entity: BlameCandidate

- Purpose: Ranked plausible attribution target.
- Fields:
  - `candidate_id` (string)
  - `source_node_id` (string)
  - `candidate_files` (list[string])
  - `path_evidence` (`LineagePathEvidence`)
  - `commit_evidence` (list[`CommitEvidence`])
  - `factor_scores` (object)
    - `recency` (float 0..1)
    - `hop_proximity` (float 0..1)
    - `directness` (float 0..1)
    - `line_blame` (float 0..1)
    - `lineage_completeness` (float 0..1)
  - `confidence_score` (float 0..100)
  - `confidence_band` (enum: `high`, `medium`, `low`)
  - `uncertainty_reasons` (list[string])

## Entity: BlastRadiusSummary

- Purpose: Structured downstream impact estimate.
- Fields:
  - `affected_nodes` (list[string])
  - `affected_pipelines` (list[string])
  - `affected_interfaces` (list[string])
  - `direct_impact` (object)
    - `nodes` (list[string])
    - `pipelines` (list[string])
    - `interfaces` (list[string])
  - `indirect_impact` (object)
    - `nodes` (list[string])
    - `pipelines` (list[string])
    - `interfaces` (list[string])
  - `estimated_impacted_records` (int | null)
  - `estimated_impacted_datasets` (int | null)
  - `knowledge_completeness` (enum: `full`, `partial`, `minimal`)
  - `unknown_downstream_count` (int)

## Entity: ViolationRecord

- Purpose: Persisted machine-readable output for downstream features.
- Fields:
  - `violation_id` (string)
  - `check_id` (string)
  - `detected_at` (ISO-8601 string)
  - `contract_id` (string | null)
  - `dataset_id` (string | null)
  - `status` (enum: `FAIL`, `ERROR`)
  - `blame_chain` (list[`BlameCandidate`], min=1, max=5)
  - `blast_radius` (`BlastRadiusSummary`)
  - `attribution_confidence_summary` (object | null)
  - `record_version` (string)

## Relationships

- `AttributionEligibleResult` 1.._ -> 1.._ `SchemaAnchor`
- `SchemaAnchor` 1 -> 0..\* `LineageNode`
- `LineageNode` 1.._ -> 0.._ `BlameCandidate`
- `BlameCandidate` 1 -> 1 `LineagePathEvidence`
- `BlameCandidate` 1 -> 0..\* `CommitEvidence`
- `ViolationRecord` 1 -> 1..5 `BlameCandidate`
- `ViolationRecord` 1 -> 1 `BlastRadiusSummary`

## Validation Rules

- `violation_id` MUST be deterministic for same identity inputs.
- `blame_chain` length MUST be between 1 and 5 for attributable violations.
- `confidence_score` MUST be in range [0, 100].
- `direct_impact` MUST include only 1-hop downstream nodes.
- `indirect_impact` MUST include only >=2-hop downstream nodes.
- If lineage or git evidence is incomplete, `uncertainty_reasons` MUST be non-empty.

## State Transitions

1. `detected` -> validation failure loaded.
2. `mapped` -> schema/interface anchor derived.
3. `attributed_partial` -> lineage and/or git evidence partially available.
4. `attributed_ranked` -> bounded ranked blame chain computed.
5. `impact_estimated` -> blast radius computed.
6. `persisted` -> JSONL violation record written (or deduped as existing).
