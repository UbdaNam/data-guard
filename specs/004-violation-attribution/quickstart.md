# Quickstart — Violation Attribution and Blast Radius Analysis

## Prerequisites

- Active branch: `004-violation-attribution`
- Python 3.11+
- Inputs available:
  - `validation_reports/*.json` (Feature 3)
  - `outputs/week4/lineage_snapshots.jsonl` (Week 4)
  - Feature 1 metadata (`contracts/interface_registry.yaml`, `contracts/schema_ownership_map.yaml`, canonical surface artifacts)
  - Feature 2 contracts (`generated_contracts/*.yaml`) for schema/check mapping support
- Local git history available in repository clone

## Primary command

1. Run attribution from `contracts/attributor.py`.
2. Confirm output file exists at `violation_log/violations.jsonl`.
3. Re-run unchanged inputs and confirm deterministic ordering and duplicate suppression.

Example:

```bash
python contracts/attributor.py --dry-run
python contracts/attributor.py
```

## Verification checklist

- Eligibility filtering applied to `FAIL` and selected attributable `ERROR` classes.
- Every attributable violation has 1–5 ranked blame candidates.
- `blame_chain[]` entries include confidence score and uncertainty reasons when needed.
- `blast_radius{}` includes:
  - `affected_nodes`
  - `affected_pipelines`
  - `affected_interfaces`
  - estimated impacted records/datasets where inferable
- Direct/indirect impact split follows hop rules (direct=1, indirect>=2).

## Degradation behavior checks

- Missing lineage data does not halt run; records are emitted with partial blast radius and uncertainty.
- Missing git history does not halt run; lineage-only candidates emitted with lower confidence.
- Weak mapping does not fabricate certainty; confidence and uncertainty fields remain explicit.

## Expected summary

- `processed_reports` reflects the number of validation reports considered.
- `attributed_violations` reflects eligible failures that received at least one candidate.
- `written_violations` reflects the number of JSONL records appended to the output file.
- `skipped_results` reflects PASS results plus non-attributable or unresolved failures.

## Scope boundary checks

- Attribution + blast radius are executed.
- Validation execution is not performed by Feature 4.
- Schema evolution classification is not performed by Feature 4.
- Stakeholder report generation is not performed by Feature 4.
