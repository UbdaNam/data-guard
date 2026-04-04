# Quickstart: Spec Alignment and Platform Completion

This quickstart is the reviewer/maintainer operating guide for the unified platform update.

## 1. Setup

1. Install Python 3.11+.
2. Sync dependencies using `uv sync --extra dev`.
3. Review `.env.example` and keep OpenRouter values optional.

## 2. Verify the new registry

- Confirm `docs/governance/subscriptions_registry.yaml` exists.
- Confirm the file contains `version`, `generated_at`, and `interfaces`.
- Confirm each interface record includes `interface_id`, `producer`, `consumer`, `schema_name` or `record_type`, `criticality`, and `dependency_type` or `directness`.

## 3. Run the baseline platform flow

1. `python -m contracts.generator`
2. `python -m contracts.runner`
3. `python -m contracts.attributor`
4. `python -m contracts.schema_analyzer`
5. `python -m contracts.ai_extensions`
6. `python -m contracts.report_generator`

## 4. What to expect

- Contract generation writes numeric baselines, confidence constraints, and lineage-derived consumers.
- Validation uses `schema_snapshots/baselines.json`, supports AUDIT/WARN/ENFORCE, and keeps missing columns as ERROR.
- Attribution consults the registry, ranks at most five candidates, and returns blast-radius details.
- Schema evolution marks float 0.0–1.0 → int 0–100 as CRITICAL.
- AI extensions validate prompt inputs, quarantine invalid inputs, and write WARN entries when output-violation thresholds are exceeded.
- Reports compute the exact health score and produce action items with file path, field, and contract clause references.

## 5. Deterministic fallback rules

- If OpenRouter is absent, all optional LLM-assisted behavior is skipped.
- If baselines are missing, the upstream generating step must be rerun first.
- If lineage is missing, consumer injection and downstream attribution must wait for the latest Week 4 lineage snapshot.
- If the registry is missing, downstream topology-dependent steps should stop until the registry is restored.

## 6. Maintainer navigation

- Governance: `docs/governance/subscriptions_registry.yaml`
- Generated contracts: `generated_contracts/`
- Validation reports: `validation_reports/`
- Violation logs: `violation_log/`
- Snapshots: `schema_snapshots/`
- Operational reports: `enforcer_report/`
