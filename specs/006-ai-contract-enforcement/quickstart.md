# Quickstart: AI Contract Enforcement Extensions

## Prerequisites

- Python 3.11+
- Repository root as current working directory
- Governing artifacts from prior features available:
  - `contracts/` Feature 1 metadata assets
  - `generated_contracts/` Feature 2 schemas/contracts
  - `validation_reports/` Feature 3 pattern compatibility
  - optional `validation_reports/schema_evolution_*.json` from Feature 5

## 1) Run AI contract enforcement with canonical defaults

```bash
python -m contracts.ai_extensions
```

## 2) Run with explicit paths

```bash
python -m contracts.ai_extensions \
  --week2-path outputs/week2/verdicts.jsonl \
  --week3-path outputs/week3/extractions.jsonl \
  --trace-path outputs/traces/runs.jsonl \
  --contracts-dir generated_contracts \
  --feature1-metadata-root contracts \
  --snapshot-root schema_snapshots \
  --validation-report-path validation_reports/ai_metrics.json \
  --violation-log-path violation_log/ai_violations.jsonl \
  --quarantine-dir outputs/quarantine \
  --surface-id week3_prompt_text
```

## 3) Expected outputs

- `validation_reports/ai_metrics.json`
- `violation_log/ai_violations.jsonl` (if violations occur)
- `outputs/quarantine/{run_timestamp}_{run_id}.jsonl` (if invalid prompts occur)
- `schema_snapshots/ai/{surface_id}/baseline_*.json` (first run or reset)
- `schema_snapshots/ai/{surface_id}/comparison_*.json` (comparison runs)

## 4) Determinism and reviewability checks

- Re-running on unchanged inputs should preserve:
  - stable ordering of records in metrics and violation output
  - stable baseline metadata (`algorithm`, `vector_dimensions`, `surface_id`)
  - deterministic trend computation for the same history window

## 5) Graceful degradation behavior

- Missing Feature 5 context: run still succeeds with `context_completeness.feature5_context_loaded=false`.
- Missing baseline: run creates baseline and marks drift status `baseline_created`.
- Insufficient drift sample size: run marks `insufficient_data` without false drift claims.
- Quarantine write failure when invalid prompts exist: run fails non-zero and emits explicit error.

## 6) Minimum smoke validation checklist

- Confirm no prompt record is silently dropped (`processed = valid + quarantined`).
- Confirm metrics file includes totals, rates, trend status, and artifact pointers.
- Confirm any produced violations include `category`, `surface_id`, and `record_ref`.
- Confirm drift artifacts include algorithm/version metadata and sample size.
