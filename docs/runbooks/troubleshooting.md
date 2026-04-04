# Troubleshooting Runbook: Developer Workflow and End-to-End Runbook

This guide explains the minimum recovery steps for common workflow failures.

## Recovery principles

- Start with the earliest missing prerequisite.
- Rerun upstream steps before downstream steps.
- Treat missing OpenRouter configuration as non-blocking.
- Verify the canonical artifact path that should exist before moving on.

## Failure cases

### Missing input datasets

- **Likely cause**: Source inputs in `outputs/week3/` or `outputs/week5/` are absent.
- **Impact**: Contract generation cannot produce the expected contract artifacts.
- **Recovery**: Restore the source datasets, then rerun `python -m contracts.generator` before continuing.

### Missing generated contracts

- **Likely cause**: Contract generation has not been run or failed earlier.
- **Impact**: Validation, attribution, schema analysis, and reporting cannot proceed reliably.
- **Recovery**: Rerun `python -m contracts.generator`, then rerun validation.

### Missing subscriptions registry

- **Likely cause**: The canonical registry at `docs/governance/subscriptions_registry.yaml` is absent or malformed.
- **Impact**: Attribution and schema-evolution downstream analysis may be incomplete.
- **Recovery**: Restore the registry file before rerunning attribution or schema-evolution analysis.

### Malformed validation reports

- **Likely cause**: Validation output is incomplete, corrupted, or from the wrong run.
- **Impact**: Attribution and later reporting steps may fail or produce incomplete evidence.
- **Recovery**: Regenerate validation reports with `python -m contracts.runner`, then rerun attribution and downstream steps.

### Missing lineage snapshots

- **Likely cause**: Attribution prerequisites are incomplete or the lineage run was not available.
- **Impact**: Violation attribution may not produce complete blame chains.
- **Recovery**: Restore the lineage snapshot source, rerun validation if needed, then rerun attribution.

### Missing schema snapshots

- **Likely cause**: Schema analysis or prior snapshot creation has not been completed.
- **Impact**: Schema evolution outputs and report evidence may be incomplete.
- **Recovery**: Rerun `python -m contracts.schema_analyzer` starting from the earliest missing prerequisite.

### Absent OpenRouter configuration

- **Likely cause**: `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, or `OPENROUTER_MODEL` are unset.
- **Impact**: None for the deterministic baseline; optional enrichment is skipped.
- **Recovery**: No action required unless enriched narratives are desired. The report generator will continue on the baseline path.

### Partial feature execution

- **Likely cause**: A downstream command was run before its prerequisite outputs existed.
- **Impact**: Outputs may be missing, stale, or incomplete.
- **Recovery**: Regenerate the earliest missing prerequisite first, then rerun each dependent command in order.

### Validation mode confusion

- **Likely cause**: The runner was invoked with the wrong `--mode` for the intended workflow.
- **Impact**: Threshold breaches may remain warnings in `AUDIT` or `WARN`, or be escalated in `ENFORCE`.
- **Recovery**: Rerun `python -m contracts.runner --mode WARN` for standard review, or `--mode ENFORCE` when warning escalation is required.

## Rerun order examples

- If contracts are missing, run `python -m contracts.generator` first.
- If validation reports are missing, run `python -m contracts.runner` after contract generation.
- If attribution artifacts are missing, rerun validation first, then `python -m contracts.attributor`.
- If schema evolution outputs are missing, rerun contract generation and validation before `python -m contracts.schema_analyzer`.
- If AI metrics are missing, rerun `python -m contracts.ai_extensions` before reporting.
- If report outputs are missing, rerun `python -m contracts.report_generator` after the earlier artifacts are restored.

## Where to look

- `generated_contracts/` for contract generation outputs
- `validation_reports/` for validation, schema evolution, and AI metrics outputs
- `violation_log/` for attribution outputs
- `schema_snapshots/` for baselines and AI snapshot evidence
- `enforcer_report/` for stakeholder-facing report outputs

## When to stop

If the earliest prerequisite cannot be restored from existing repository inputs, stop and resolve the missing upstream artifact before rerunning downstream steps.
