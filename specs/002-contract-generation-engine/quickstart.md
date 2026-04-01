# Quickstart — Contract Generation Engine

## Prerequisites

- Active branch: `002-contract-generation-engine`
- Python 3.11+
- Feature 1 canonical artifacts exist under `contracts/`
- Governed input datasets exist:
  - `outputs/week3/extractions.jsonl`
  - `outputs/week5/events.jsonl`

## Generate contracts

Use the primary entry point:

1. Execute generator orchestration from `contracts/generator.py`.
2. Confirm output artifacts:
   - `generated_contracts/week3_extractions.yaml`

- `generated_contracts/week5_events.yaml`
- `generated_contracts/week3_extractions_dbt.yml`
- `generated_contracts/week5_events_dbt.yml`

## Validate expected behavior

- Structural profile includes nested fields where feasible.
- Statistical profile includes numeric distribution metrics.
- Requirement-defined invariants are preserved even if samples are currently compliant.
- Weak semantic confidence yields explicit uncertainty notes, not invented business meaning.
- Downstream context includes systems, consumed fields, likely breaking fields, and change sensitivity when available.
- Outputs are diff-stable for unchanged inputs except timestamps/version metadata.

## Failure expectations

- Missing dataset -> dataset-specific failure with explicit blocked status.
- Malformed JSONL lines -> partial generation continues with malformed-line count in metadata.
- Missing Week 4 lineage data -> generation continues with partial context annotations.

## Downstream readiness checks

Generated artifacts are ready as direct inputs for:

- validation execution features
- violation attribution features
- schema evolution intelligence features
- operational reporting features
