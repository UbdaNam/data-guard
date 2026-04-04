# Contract: Operational Report Artifacts

## Scope

Defines machine-readable and human-readable output contracts for Feature 7 report generation.

## 1) Machine-readable output

- **Path**: `enforcer_report/report_data.json`
- **Format**: UTF-8 JSON object
- **Top-level key order (required)**:
  1. `report_id`
  2. `report_date`
  3. `reporting_window`
  4. `data_health_score`
  5. `section_completeness`
  6. `violations_summary`
  7. `top_violations`
  8. `schema_changes_summary`
  9. `ai_risk_summary`
  10. `recommended_actions`
  11. `evidence_index`
  12. `generation_metadata`

### Required section contracts

- `reporting_window`
  - `start`, `end`, `selection_mode`, `resolved_from_sources`
- `data_health_score`
  - `value`, `score_status`, `check_penalty`, `critical_penalty`, `raw_score`, `formula_version`, `reason`
- `section_completeness`
  - object keyed by required section names with `status`, `missing_sources`, `reason`
- `top_violations[]`
  - `rank`, `violation_id`, `severity`, `recurrence_count`, `latest_occurrence`, `affected_surface`, `owner`, `evidence`
- `schema_changes_summary`
  - aggregate counts + prioritized `top_changes[]`
- `ai_risk_summary`
  - current rates, drift/trend flags, completeness indicators
- `recommended_actions[]`
  - `action_id`, `issue_key`, `priority_score`, `remediation_target`, `affected_location`, `owner`, `verification_step`, `aggregate_count`, `evidence`
- `evidence_index[]`
  - `artifact_path`, `record_selector`, `claim_type`
- `generation_metadata`
  - generation timestamps/duration, input counts, enrichment status, fallback marker

## 2) Human-readable output

- **Path**: `enforcer_report/report_{date}.md`
- **Format**: UTF-8 Markdown
- **Required section order**:
  1. Data Health Score
  2. Violations this period
  3. Schema changes detected
  4. AI system risk assessment
  5. Recommended actions
  6. Evidence traceability notes

## 3) Determinism contract

- Ranked collections use stable tuple comparators and deterministic ID tie-breaks.
- Required section ordering is fixed for both JSON and Markdown.
- Only metadata fields may vary run-to-run on unchanged evidence:
  - `report_id`
  - `generation_metadata.generated_at`
  - `generation_metadata.duration_ms`

## 4) Graceful degradation contract

- Missing upstream artifact families MUST NOT block report generation.
- Affected sections remain present with `status=insufficient_evidence`.
- `missing_sources` includes unresolved expected paths/patterns.
- No incidents/actions may be fabricated to fill missing data.

## 5) Optional OpenRouter enrichment contract

- Provider must be OpenRouter only.
- Configuration source is environment variables only:
  - `OPENROUTER_API_KEY`
  - `OPENROUTER_BASE_URL`
  - `OPENROUTER_MODEL`
- Enrichment is optional and non-blocking.
- Failure/missing configuration must force deterministic fallback narrative.
- Enriched text must be evidence-grounded and cannot introduce unsupported claims.
