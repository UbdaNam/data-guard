# Quickstart: Feature 1 Foundation Validation

## Prerequisites

- Python 3.11+
- Repository checked out on branch `001-platform-data-surface`
- Working directory at repository root

## 1) Confirm canonical target paths exist

Validate that the following paths are present or intentionally scaffolded:

- `contracts/generator.py`
- `contracts/runner.py`
- `contracts/attributor.py`
- `contracts/schema_analyzer.py`
- `contracts/ai_extensions.py`
- `contracts/report_generator.py`
- `generated_contracts/`
- `validation_reports/`
- `violation_log/`
- `schema_snapshots/`
- `enforcer_report/`
- `outputs/week1/intent_records.jsonl`
- `outputs/week2/verdicts.jsonl`
- `outputs/week3/extractions.jsonl`
- `outputs/week4/lineage_snapshots.jsonl`
- `outputs/week5/events.jsonl`
- `outputs/traces/runs.jsonl`
- `DOMAIN_NOTES.md`
- `README.md`

## 2) Create or update foundation metadata artifacts

Populate/refresh:

- `contracts/canonical_paths.yaml`
- `contracts/dataset_readiness.json`
- `contracts/interface_registry.yaml`
- `contracts/schema_ownership_map.yaml`
- `contracts/data_flow_architecture.mmd`
- `contracts/requirement_traceability.yaml`
- `DOMAIN_NOTES.md`

## 3) Enforce readiness/provenance enum

For each record in each foundation artifact, set exactly one:

- `confirmed_from_repository_evidence`
- `inferred_from_requirement_document`
- `blocked_by_missing_upstream_data`
- `pending_migration_or_normalization`

## 4) Capture mismatch evidence

If actual upstream outputs differ from canonical filenames, shapes, or semantics:

1. Add a mismatch record.
2. Preserve canonical target unchanged.
3. Add migration/normalization requirement.
4. Document business-meaning risk in `DOMAIN_NOTES.md`.

## 5) Validate review readiness

A reviewer should be able to:

- trace every required dataset and interface to ownership metadata,
- see readiness status for each governed dataset,
- locate mismatch and migration notes,
- map requirements to concrete artifacts without rediscovery.
