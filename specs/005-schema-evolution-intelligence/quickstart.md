# Quickstart — Schema Evolution Intelligence

## Prerequisites

- Active branch: `005-schema-evolution-intelligence`
- Python 3.11+
- Required inputs:
  - `generated_contracts/*.yaml`
  - existing or writable `schema_snapshots/{contract_id}/`
  - Feature 1 metadata artifacts (`contracts/interface_registry.yaml`, `contracts/schema_ownership_map.yaml`, readiness/canonical metadata)
- Optional enrichment inputs:
  - `validation_reports/*.json` (Feature 3)
  - `violation_log/violations.jsonl` (Feature 4)

## Primary entry point

- `contracts/schema_analyzer.py`

## Baseline flow

1. Capture or refresh schema snapshots for supported contracts.
2. Run latest-vs-previous analysis for each contract.
3. Confirm outputs:
   - `validation_reports/schema_evolution_{contract_id}.json`
   - `migration_impact_{contract_id}_{timestamp}.json`
4. Re-run unchanged inputs and confirm deterministic no-material-change behavior.

## Alternate comparison flow

- Run explicit two-snapshot comparison by `from_snapshot_id` + `to_snapshot_id` for the same contract.

## Verification checklist

- Snapshot files follow `schema_snapshots/{contract_id}/snapshot_{timestamp}_{schema_hash}.json`.
- Flat and nested field diffs are rendered with deterministic ordering.
- Change classes and compatibility verdicts follow the approved taxonomy.
- Migration impact output contains:
  - human-readable diff summary
  - machine-readable structured diff
  - compatibility verdict
  - affected consumers and likely failure modes
  - ordered migration checklist
  - rollback guidance for breaking changes
  - urgency (`low|medium|high|critical`)

## Degradation checks

- Missing optional Feature 3/4 artifacts does not block analysis.
- Missing previous snapshot yields snapshot-only or baseline-established result.
- Malformed snapshots are reported with warnings while valid comparisons continue.
- Low-confidence rename detection falls back to remove+add.

## Scope boundaries

- This feature detects/classifies schema changes and generates migration impact outputs.
- This feature does not execute validation.
- This feature does not perform git-blame attribution.
- This feature does not produce final stakeholder-facing reports.

## Validation run notes (2026-04-04)

- Ran `contracts/schema_analyzer.py --snapshot` successfully for Week 3 and Week 5 contracts.
- Verified snapshot dedupe behavior (`no_material_change=true`) when schema hash matched latest snapshot.
- Ran `contracts/schema_analyzer.py` successfully and generated baseline-established evolution outputs:
  - `validation_reports/schema_evolution_week3_extractions.v1.json`
  - `validation_reports/schema_evolution_week5_events.v1.json`
- Verified boundary enforcement: `contracts/schema_analyzer.py --validate` is rejected as out of scope.
