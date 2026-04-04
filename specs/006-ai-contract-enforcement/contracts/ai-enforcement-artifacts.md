# Contract Specification: AI Enforcement Interfaces and Artifacts

## 1) CLI Contract (`contracts/ai_extensions.py`)

### Command

- `python -m contracts.ai_extensions` (or equivalent repository execution path)

### Inputs (defaulted, override-capable)

- `--week2-path` (default: `outputs/week2/verdicts.jsonl`)
- `--week3-path` (default: `outputs/week3/extractions.jsonl`)
- `--trace-path` (default: `outputs/traces/runs.jsonl`)
- `--contracts-dir` (default: `generated_contracts/`)
- `--feature1-metadata-root` (default: `contracts/`)
- `--snapshot-root` (default: `schema_snapshots/`)
- `--validation-report-path` (default: `validation_reports/ai_metrics.json`)
- `--violation-log-path` (default: `violation_log/ai_violations.jsonl`)
- `--quarantine-dir` (default: `outputs/quarantine/`)
- `--surface-id` (required for drift checks; governed text surface identifier)

### Exit behavior

- `0`: run completed (possibly with warnings and explicit completeness flags)
- non-zero: hard failure (e.g., mandatory write path unavailable, unrecoverable parsing/system errors)

## 2) Quarantine Artifact Contract

### Path and naming

- `outputs/quarantine/{run_timestamp}_{run_id}.jsonl`
- `run_timestamp` format: `YYYYMMDDTHHMMSSZ` (UTC)

### Write strategy

- Build in-memory ordered invalid-record stream
- Write to temp file in same directory
- Atomic rename to final path
- If invalid prompt records exist and write fails: fail run loudly

### Record schema

```json
{
  "run_id": "string",
  "run_timestamp": "string",
  "record_id": "string",
  "source_dataset": "outputs/week3/extractions.jsonl",
  "schema_version": "string",
  "failure_reasons": ["string"],
  "original_payload": {}
}
```

## 3) AI Violation Log Contract

### Path

- `violation_log/ai_violations.jsonl`

### Append strategy

- Append-only JSONL in deterministic in-run order (`category`, `surface_id`, `record_ref`)
- One line per violation; no in-place mutation

### Record schema

```json
{
  "violation_id": "string",
  "run_id": "string",
  "category": "prompt_input|structured_output|trace_contract|embedding_drift",
  "severity": "low|medium|high|critical",
  "status": "open|acknowledged|resolved",
  "surface_id": "string",
  "record_ref": "string",
  "message": "string",
  "evidence": {},
  "owner_context": {}
}
```

## 4) AI Metrics Report Contract

### Path

- `validation_reports/ai_metrics.json`

### File behavior

- Overwrite single latest run summary (deterministic, sorted keys)
- Include bounded history section for trend calculations

### Schema (required top-level keys)

```json
{
  "run_id": "string",
  "run_timestamp": "string",
  "totals": {},
  "rates": {},
  "trend": {
    "window_size": 10,
    "history_points_used": 0,
    "output_violation_rate_slope": null,
    "trend_status": "insufficient_history|stable|improving|degrading"
  },
  "artifacts": {},
  "context_completeness": {},
  "history": []
}
```

## 5) Embedding Baseline and Comparison Contracts

### Paths

- Baseline: `schema_snapshots/ai/{surface_id}/baseline_{algorithm}_{version}.json`
- Comparison: `schema_snapshots/ai/{surface_id}/comparison_{run_timestamp}_{run_id}.json`

### Baseline schema

```json
{
  "surface_id": "string",
  "baseline_id": "string",
  "algorithm": "token_hash_v1",
  "vector_dimensions": 256,
  "created_at": "string",
  "sample_size": 0,
  "sample_filters": {},
  "source_paths": ["string"],
  "signature_vector": [0.0]
}
```

### Comparison schema

```json
{
  "run_id": "string",
  "surface_id": "string",
  "baseline_id": "string|null",
  "comparison_status": "baseline_created|compared|insufficient_data|baseline_unreadable|skipped",
  "sample_size": 0,
  "cosine_distance": 0.0,
  "drift_threshold": 0.0,
  "drift_detected": false,
  "reason": "string"
}
```

## 6) Reuse and boundary contract

- Reuse Feature 1 canonical metadata for ownership and context enrichment.
- Reuse Feature 2 schema/contract sources as governing validation definitions.
- Reuse Feature 3 report/validator conventions for deterministic formatting.
- Optionally ingest Feature 5 schema evolution outputs for interpretive context only.
- Must not replace `contracts/runner.py`, must not generate final stakeholder reports, and must not perform git attribution.
