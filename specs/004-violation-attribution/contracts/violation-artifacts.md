# Contracts: Violation Attribution Artifacts

## Output Artifact

- Path: `violation_log/violations.jsonl`
- Format: JSON Lines (one `ViolationRecord` per line)
- Producer: Feature 4 attribution engine (`contracts/attributor.py`)
- Consumers: later schema-evolution interpretation, operational reporting, and prioritization workflows

## Record Schema (required fields)

```json
{
  "violation_id": "string",
  "check_id": "string",
  "detected_at": "ISO-8601 timestamp",
  "contract_id": "string|null",
  "dataset_id": "string|null",
  "status": "FAIL|ERROR",
  "blame_chain": [
    {
      "candidate_id": "string",
      "source_node_id": "string",
      "candidate_files": ["string"],
      "confidence_score": 0.0,
      "confidence_band": "high|medium|low",
      "uncertainty_reasons": ["string"],
      "factor_scores": {
        "recency": 0.0,
        "hop_proximity": 0.0,
        "directness": 0.0,
        "line_blame": 0.0,
        "lineage_completeness": 0.0
      },
      "path_evidence": {
        "hop_count": 0,
        "stop_reason": "external_boundary|repository_root|no_upstream_nodes|max_hops",
        "is_complete": true
      },
      "commit_evidence": [
        {
          "file_path": "string",
          "commit_hash": "string",
          "author_name": "string",
          "authored_at": "ISO-8601 timestamp",
          "line_start": 0,
          "line_end": 0,
          "blame_used": false
        }
      ]
    }
  ],
  "blast_radius": {
    "affected_nodes": ["string"],
    "affected_pipelines": ["string"],
    "affected_interfaces": ["string"],
    "direct_impact": {
      "nodes": ["string"],
      "pipelines": ["string"],
      "interfaces": ["string"]
    },
    "indirect_impact": {
      "nodes": ["string"],
      "pipelines": ["string"],
      "interfaces": ["string"]
    },
    "estimated_impacted_records": 0,
    "estimated_impacted_datasets": 0,
    "knowledge_completeness": "full|partial|minimal",
    "unknown_downstream_count": 0
  },
  "attribution_confidence_summary": {
    "top_score": 0.0,
    "top_band": "high|medium|low",
    "candidate_count": 1,
    "has_partial_evidence": false
  },
  "record_version": "v1"
}
```

## Behavioral Contract

- Output MUST be deterministic for unchanged inputs (except run metadata if present).
- Blame chain cardinality MUST be bounded to 1–5 candidates.
- Attribution MUST degrade gracefully under missing lineage/git evidence.
- Partial knowledge MUST be explicit (`uncertainty_reasons`, `knowledge_completeness`).
- Output MUST remain machine-readable and append-safe for repeated runs.

## Non-goals (Feature Boundary)

- Does not execute validation.
- Does not perform schema evolution classification.
- Does not generate stakeholder-facing reports.
