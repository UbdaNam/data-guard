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

## Schema Evolution Intelligence (Feature 5)

Primary entry point:

- contracts/schema_analyzer.py

Primary governed inputs:

- generated_contracts/\*.yaml
- schema*snapshots/{contract_id}/snapshot*{timestamp}\_{schema_hash}.json
- contracts/interface_registry.yaml
- contracts/schema_ownership_map.yaml
- optional: validation_reports/\*.json and violation_log/violations.jsonl

Primary generated outputs:

- validation*reports/schema_evolution*{contract_id}.json
- migration*impact*{contract*id}*{timestamp}.json
- validation_reports/schema_evolution_run_summary.json

Schema evolution can also be triggered via:

- contracts/schema_analyzer.py --snapshot

Operational guarantees:

- Snapshot writes are deduplicated for no-material-change hashes.
- Diff output is deterministic (class order then canonical field path order).
- Compatibility classification is dual-axis (backward/forward) with derived verdict.
- Migration guidance includes affected consumers, failure modes, checklist actions, and rollback for breaking changes.
- Missing optional Feature 3/4 context degrades with warnings and completeness flags.

Out-of-scope for Feature 5:

- validation execution
- git-blame attribution
- final stakeholder-facing report generation

## AI Contract Enforcement Extensions (Feature 6)

Primary entry point:

- contracts/ai_extensions.py

Primary governed inputs:

- outputs/week2/verdicts.jsonl
- outputs/week3/extractions.jsonl
- outputs/traces/runs.jsonl
- generated_contracts/prompt_inputs/week3_prompt_input.schema.json
- generated_contracts/\*.yaml (governing contract context)
- contracts/\*.yaml|json (Feature 1 metadata context)
- optional: validation*reports/schema_evolution*\*.json

Primary generated outputs:

- validation_reports/ai_metrics.json
- violation_log/ai_violations.jsonl
- outputs/quarantine/{run*timestamp}*{run_id}.jsonl
- schema_snapshots/ai/{surface_id}/baseline_token_hash_v1.json
- schema*snapshots/ai/{surface_id}/comparison*{run*timestamp}*{run_id}.json

AI enforcement can be triggered via:

- python -m contracts.ai_extensions

Operational guarantees:

- Prompt inputs are classified as valid or quarantined with no silent drop.
- Week 2 structured outputs receive deterministic conformance outcomes.
- Trace records receive contract outcomes; malformed run IDs/timestamps are recorded as violations.
- Embedding drift is deterministic (`token_hash_v1`, fixed dimensions, cosine distance).
- Missing baseline creates baseline; insufficient sample size yields explicit status.
- Metrics and artifact pointers are written in machine-readable form for downstream reuse.

Out-of-scope for Feature 6:

- replacing the general validation runner
- git-blame attribution
- schema evolution classification logic
- final stakeholder-facing report generation

## Operational Report Generation (Feature 7)

Primary entry point:

- contracts/report_generator.py

Primary governed inputs:

- validation_reports/\*.json
- violation_log/violations.jsonl
- validation*reports/schema_evolution*\*.json
- validation_reports/ai_metrics.json
- contracts/schema_ownership_map.yaml
- contracts/interface_registry.yaml

Primary generated outputs:

- enforcer_report/report_data.json
- enforcer*report/report*{date}.md

Report generation can be triggered via:

- python -m contracts.report_generator

Optional OpenRouter enrichment:

- Enable with `--enable-llm-enrichment`
- Environment-only configuration:
  - OPENROUTER_API_KEY
  - OPENROUTER_BASE_URL
  - OPENROUTER_MODEL
- Missing or failed enrichment automatically falls back to deterministic non-LLM
  narrative and does not block report generation.

Operational guarantees:

- Deterministic ordering of ranked findings and actions.
- Fixed report_data.json key order and fixed markdown section order.
- Required sections remain present with explicit `insufficient_evidence` status
  when upstream artifacts are partially missing.
- Evidence references are preserved for claims and recommended actions.

Out-of-scope for Feature 7:

- validation execution
- git-blame attribution
- schema evolution classification logic
- AI metric generation logic

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
