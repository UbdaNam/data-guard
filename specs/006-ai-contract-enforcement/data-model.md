# Data Model: AI Contract Enforcement Extensions

## 1) `AIEnforcementRun`

- **Purpose**: Top-level run envelope for deterministic traceability.
- **Fields**:
  - `run_id` (string, required, UUID-like)
  - `run_timestamp` (string, required, UTC ISO-8601)
  - `entrypoint` (string, required, fixed: `contracts/ai_extensions.py`)
  - `inputs` (object, required)
    - `week2_path` (string)
    - `week3_path` (string)
    - `trace_path` (string)
    - `contract_sources` (array[string])
    - `feature1_metadata_sources` (array[string])
  - `context_completeness` (object, required)
    - `feature1_loaded` (bool)
    - `feature2_loaded` (bool)
    - `feature3_conventions_loaded` (bool)
    - `feature5_context_loaded` (bool)
  - `status` (enum: `completed`, `completed_with_warnings`, `failed`)

## 2) `PromptInputCheckRecord`

- **Purpose**: Validation result for one Week 3 prompt-bound input row.
- **Fields**:
  - `record_id` (string, required)
  - `schema_version` (string, required)
  - `prompt_surface` (string, required)
  - `validation_status` (enum: `PASS`, `FAIL`, `ERROR`)
  - `failure_reasons` (array[string], required when failed)
  - `quarantined` (bool, required)
  - `quarantine_path` (string|null)

## 3) `StructuredOutputCheckRecord`

- **Purpose**: Validation result for one Week 2 structured output row.
- **Fields**:
  - `record_id` (string, required)
  - `schema_id` (string, required)
  - `schema_version` (string, required)
  - `validation_status` (enum: `PASS`, `FAIL`, `ERROR`)
  - `unknown_fields` (array[string])
  - `missing_required_fields` (array[string])
  - `type_mismatches` (array[object])
  - `nested_structure_violations` (array[object])

## 4) `TraceContractCheckRecord`

- **Purpose**: Validation result for one LangSmith trace row.
- **Fields**:
  - `trace_run_id` (string, required)
  - `event_timestamp` (string, required)
  - `contract_id` (string, required)
  - `validation_status` (enum: `PASS`, `FAIL`, `ERROR`)
  - `failure_reasons` (array[string])

## 5) `QuarantineRecord`

- **Purpose**: Durable evidence of blocked prompt input.
- **Fields**:
  - `run_id` (string, required)
  - `run_timestamp` (string, required)
  - `record_id` (string, required)
  - `source_dataset` (string, required, fixed for this feature: `outputs/week3/extractions.jsonl`)
  - `schema_version` (string, required)
  - `failure_reasons` (array[string], required)
  - `original_payload` (object, required)
- **State transitions**:
  - `detected_invalid` → `written_quarantine` → `referenced_in_metrics`

## 6) `AIViolationRecord`

- **Purpose**: Unified AI-specific violation evidence written under `violation_log/`.
- **Fields**:
  - `violation_id` (string, required, deterministic hash from run + surface + record)
  - `run_id` (string, required)
  - `category` (enum: `prompt_input`, `structured_output`, `trace_contract`, `embedding_drift`)
  - `severity` (enum: `low`, `medium`, `high`, `critical`)
  - `status` (enum: `open`, `acknowledged`, `resolved`)
  - `surface_id` (string, required)
  - `record_ref` (string, required)
  - `message` (string, required)
  - `evidence` (object, required)
  - `owner_context` (object, optional from Feature 1 artifacts)

## 7) `EmbeddingBaseline`

- **Purpose**: Baseline signature for one approved text surface.
- **Fields**:
  - `surface_id` (string, required)
  - `baseline_id` (string, required)
  - `algorithm` (string, required, e.g., `token_hash_v1`)
  - `vector_dimensions` (int, required, fixed)
  - `created_at` (string, required)
  - `sample_size` (int, required)
  - `signature_vector` (array[number], required)
  - `sample_filters` (object, required)
  - `source_paths` (array[string], required)

## 8) `EmbeddingComparisonResult`

- **Purpose**: Comparison outcome against baseline.
- **Fields**:
  - `run_id` (string, required)
  - `surface_id` (string, required)
  - `baseline_id` (string|null)
  - `comparison_status` (enum: `baseline_created`, `compared`, `insufficient_data`, `baseline_unreadable`, `skipped`)
  - `sample_size` (int, required)
  - `cosine_distance` (number|null)
  - `drift_threshold` (number)
  - `drift_detected` (bool)
  - `reason` (string)

## 9) `AIMetricsReport`

- **Purpose**: Machine-readable run + trend metrics at `validation_reports/ai_metrics.json`.
- **Fields**:
  - `run_id` (string, required)
  - `run_timestamp` (string, required)
  - `totals` (object)
    - `prompt_processed`, `prompt_quarantined`
    - `outputs_processed`, `outputs_failed`
    - `traces_processed`, `traces_failed`
    - `drift_checks_requested`, `drift_checks_compared`, `drift_checks_insufficient`
  - `rates` (object)
    - `prompt_quarantine_rate`
    - `output_violation_rate`
    - `trace_violation_rate`
    - `drift_detection_rate`
  - `trend` (object)
    - `window_size` (int)
    - `history_points_used` (int)
    - `output_violation_rate_slope` (number|null)
    - `trend_status` (enum: `insufficient_history`, `stable`, `improving`, `degrading`)
  - `artifacts` (object)
    - `quarantine_path` (string|null)
    - `violation_log_path` (string)
    - `drift_artifact_paths` (array[string])
  - `context_completeness` (object; mirrors run envelope)

## Relationships

- One `AIEnforcementRun` has many `PromptInputCheckRecord`, `StructuredOutputCheckRecord`, and `TraceContractCheckRecord`.
- One run may write zero-to-many `QuarantineRecord` and `AIViolationRecord`.
- One `EmbeddingBaseline` belongs to one `surface_id`; one run may produce one `EmbeddingComparisonResult` per `surface_id`.
- One run produces exactly one `AIMetricsReport` on successful completion.

## Validation Rules (cross-entity)

- `prompt_processed = prompt_valid + prompt_quarantined` (no silent drops).
- If any prompt record fails and quarantine write fails, run status must be `failed`.
- `comparison_status = compared` requires non-null `baseline_id` and `cosine_distance`.
- `trend_status = insufficient_history` when fewer than 3 historical points exist.
- Every violation must reference one of: prompt record ID, output record ID, trace run ID, or drift surface ID.
