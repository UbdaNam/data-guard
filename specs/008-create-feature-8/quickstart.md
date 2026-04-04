# Quickstart: Developer Workflow and End-to-End Runbook

This guide is the reviewer-facing path to verify the Data Contract Enforcer from a fresh clone.

## 1) Set up the environment

- Install Python 3.11 or newer.
- Sync dependencies with the lockfile-based workflow:

```bash
uv sync --extra dev
```

- Verify the interpreter and environment are available.

## 2) Review environment configuration

- The baseline workflow requires no secrets.
- `.env.example` contains placeholders only.
- Optional OpenRouter settings are only needed if you want LLM-assisted report enrichment:
  - `OPENROUTER_API_KEY`
  - `OPENROUTER_BASE_URL`
  - `OPENROUTER_MODEL`

If you do not configure them, the workflow stays deterministic.

## 3) Run the canonical platform sequence

### Contract generation

```bash
python -m contracts.generator
```

**Expected outputs**

- `generated_contracts/week3_extractions.yaml`
- `generated_contracts/week5_events.yaml`
- DBT companion files in `generated_contracts/`

**Success signal**

- The command exits successfully and prints the generated contract summary.

### Validation execution

```bash
python -m contracts.runner
```

**Expected outputs**

- `validation_reports/*.json`
- `schema_snapshots/baselines.json`

**Success signal**

- The command exits successfully and prints the validation summary JSON.

### Violation attribution

```bash
python -m contracts.attributor
```

**Expected outputs**

- `violation_log/violations.jsonl`

**Success signal**

- The command exits successfully and prints attribution summary JSON.

### Schema evolution analysis

```bash
python -m contracts.schema_analyzer
```

Optional snapshot-only mode:

```bash
python -m contracts.schema_analyzer --snapshot
```

**Expected outputs**

- `validation_reports/schema_evolution_*.json`
- `migration_impact_*.json`
- `validation_reports/schema_evolution_run_summary.json`

**Success signal**

- The command exits successfully and prints the schema-evolution summary JSON.

### AI contract enforcement

```bash
python -m contracts.ai_extensions
```

**Expected outputs**

- `validation_reports/ai_metrics.json`
- `violation_log/ai_violations.jsonl`
- `outputs/quarantine/*.jsonl`
- `schema_snapshots/ai/*`

**Success signal**

- The command exits successfully and prints the AI enforcement summary JSON.

### Operational report generation

```bash
python -m contracts.report_generator
```

Optional enrichment:

```bash
python -m contracts.report_generator --enable-llm-enrichment
```

**Expected outputs**

- `enforcer_report/report_data.json`
- `enforcer_report/report_{date}.md`

**Success signal**

- The command exits successfully and prints a JSON status object with `status: completed`.

## 4) Quick verification checklist

- Contract artifacts exist in `generated_contracts/`
- Validation reports exist in `validation_reports/`
- Violations exist in `violation_log/violations.jsonl`
- Schema evolution outputs exist in `validation_reports/`
- AI metrics exist in `validation_reports/ai_metrics.json`
- Report artifacts exist in `enforcer_report/`

## 5) When something fails

- Missing inputs: regenerate the earliest upstream artifact first.
- Missing OpenRouter config: skip enrichment and continue with the deterministic baseline.
- Partial runs: rerun from the earliest missing prerequisite, not just the last failing command.

For detailed failures and rerun guidance, use the optional troubleshooting runbook.
