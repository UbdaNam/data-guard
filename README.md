# data-guard

Production-grade Python platform for data contract enforcement across internal
systems.

## Operating Model

- Spec-first delivery using Spec Kit feature specifications
- Canonical repository structure with explicitly documented deviations only
- First-class data contract artifacts (schemas, lineage, validation, violations)
- Evidence-backed outputs from real executions or explicitly injected test data
- Downstream impact-aware schema and interface evolution

Project governance is defined in .specify/memory/constitution.md.

## Validation Execution (Feature 3)

Primary entry point:

- contracts/runner.py

Primary governed inputs:

- generated_contracts/week3_extractions.yaml
- generated_contracts/week5_events.yaml
- outputs/week3/extractions.jsonl
- outputs/week5/events.jsonl
- schema_snapshots/baselines.json

Primary generated outputs:

- validation*reports/{contract_id}*{timestamp}.json
- schema_snapshots/baselines.json

Validation can also be triggered via:

- src/cli/foundation.py validate-contracts

Operational guarantees:

- Structural checks cover `type`, `required`, `nullability`, and `pattern`
- Semantic checks cover `range`, `enum`, and `relationship`
- Dataset-level checks cover `row_count`, `uniqueness`, and `referential_integrity`
- Missing columns and unexpected structures return `ERROR`
- Invalid type violations return `FAIL`
- Unchanged inputs produce identical report content except `report_id` and `run_timestamp`

## Violation Attribution (Feature 4)

Primary entry point:

- contracts/attributor.py

Primary governed inputs:

- validation_reports/\*.json
- outputs/week4/lineage_snapshots.jsonl
- contracts/interface_registry.yaml
- contracts/schema_ownership_map.yaml
- generated_contracts/\*.yaml

Primary generated outputs:

- violation_log/violations.jsonl

Attribution can also be triggered via:

- src/cli/foundation.py attribute-violations

Operational guarantees:

- Only `FAIL` and selected attributable `ERROR` classes are considered.
- Blame chains are confidence-ranked and bounded to 1–5 candidates.
- Missing lineage or git evidence degrades gracefully instead of failing the run.
- Duplicate violation IDs are suppressed on reruns by default.
- Unsupported validation, schema-evolution, AI-check, or report modes are rejected.

## Contract Generation (Feature 2)

Primary entry point:

- contracts/generator.py

Primary governed inputs:

- outputs/week3/extractions.jsonl
- outputs/week5/events.jsonl

Primary generated outputs:

- generated_contracts/week3_extractions.yaml
- generated_contracts/week5_events.yaml
- generated_contracts/week3_extractions_dbt.yml
- generated_contracts/week5_events_dbt.yml

Generation can also be triggered via:

- src/cli/foundation.py generate-contracts

Out-of-scope for Feature 2:

- validation execution
- violation attribution
- schema evolution diff execution
- AI-specific enforcement checks
- report generation
