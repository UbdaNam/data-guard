# End-to-End Runbook: Developer Workflow and End-to-End Runbook

This runbook documents the full operator workflow for the Data Contract Enforcer.

## Baseline assumptions

- Python 3.11+ is installed.
- Dependencies are synced with `uv sync --extra dev`.
- `.env.example` has been reviewed and optional OpenRouter values are unset unless explicitly needed.
- The workflow below runs deterministically without OpenRouter.

## Canonical command sequence

### 1) Contract generation

```bash
python -m contracts.generator
```

**Inputs**

- `outputs/week3/extractions.jsonl`
- `outputs/week5/events.jsonl`

**Outputs**

- `generated_contracts/week3_extractions.yaml`
- `generated_contracts/week5_events.yaml`
- `generated_contracts/week3_extractions_dbt.yml`
- `generated_contracts/week5_events_dbt.yml`

**Success signal**

- The command prints the generated contract summary and exits successfully.

### 2) Validation execution

```bash
python -m contracts.runner
```

**Inputs**

- Generated contracts from step 1

**Outputs**

- `validation_reports/*.json`
- `schema_snapshots/baselines.json`

**Success signal**

- The command prints the validation summary JSON and exits successfully.

### 3) Violation attribution

```bash
python -m contracts.attributor
```

**Inputs**

- Validation reports
- `outputs/week4/lineage_snapshots.jsonl`
- `contracts/interface_registry.yaml`
- `contracts/schema_ownership_map.yaml`
- Generated contracts

**Outputs**

- `violation_log/violations.jsonl`

**Success signal**

- The command prints attribution summary JSON and exits successfully.

### 4) Schema evolution analysis

```bash
python -m contracts.schema_analyzer
```

Optional snapshot-only mode:

```bash
python -m contracts.schema_analyzer --snapshot
```

**Inputs**

- Generated contracts
- Validation reports when present
- Violation log when present

**Outputs**

- `validation_reports/schema_evolution_*.json`
- `migration_impact_*.json`
- `validation_reports/schema_evolution_run_summary.json`

**Success signal**

- The command prints the schema evolution summary JSON and exits successfully.

### 5) AI contract enforcement

```bash
python -m contracts.ai_extensions
```

**Inputs**

- `outputs/week2/verdicts.jsonl`
- `outputs/week3/extractions.jsonl`
- `outputs/traces/runs.jsonl`
- `generated_contracts/`
- `contracts/`

**Outputs**

- `validation_reports/ai_metrics.json`
- `violation_log/ai_violations.jsonl`
- `schema_snapshots/ai/`
- `outputs/quarantine/`

**Success signal**

- The command prints the AI enforcement summary JSON and exits successfully.

### 6) Operational report generation

```bash
python -m contracts.report_generator
```

Optional enrichment:

```bash
python -m contracts.report_generator --enable-llm-enrichment
```

**Inputs**

- `validation_reports/*.json`
- `violation_log/violations.jsonl`
- `validation_reports/schema_evolution_*.json`
- `validation_reports/ai_metrics.json`
- `contracts/schema_ownership_map.yaml`
- `contracts/interface_registry.yaml`

**Outputs**

- `enforcer_report/report_data.json`
- `enforcer_report/report_{date}.md`

**Success signal**

- The command prints a JSON status object with `status: completed`.

## Dependency order

Rerun the earliest missing prerequisite first:

1. Generate contracts if they are missing.
2. Run validation before attribution and schema analysis.
3. Run attribution before schema analysis if the violation log is needed.
4. Run schema analysis before AI/report generation when those outputs are missing.
5. Run AI enforcement before reporting when AI metrics are required.
6. Run reporting last.

## Artifact index

- `generated_contracts/`: contract outputs from Feature 2.
- `validation_reports/`: validation, schema evolution, and AI metrics outputs from Features 3, 5, and 6.
- `violation_log/`: attribution outputs from Features 4 and 6.
- `schema_snapshots/`: baselines and AI snapshots from Features 3 and 6.
- `outputs/`: raw evidence inputs and quarantine traces.
- `enforcer_report/`: stakeholder-facing report outputs from Feature 7.

## OpenRouter behavior

- OpenRouter is optional.
- If environment variables are absent, the workflow remains deterministic.
- If enrichment is enabled and fails, the report generation step falls back to the deterministic baseline.
