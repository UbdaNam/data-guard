# Domain and Schema Notes

## Canonical Platform Surface

The platform governs six canonical datasets:

- `outputs/week1/intent_records.jsonl`
- `outputs/week2/verdicts.jsonl`
- `outputs/week3/extractions.jsonl`
- `outputs/week4/lineage_snapshots.jsonl`
- `outputs/week5/events.jsonl`
- `outputs/traces/runs.jsonl`

## Known Reality vs Canonical Standard

| Dataset                 | Observed Reality                                         | Canonical Standard                                                | Gap Type            | Required Action                                                  | Readiness                          |
| ----------------------- | -------------------------------------------------------- | ----------------------------------------------------------------- | ------------------- | ---------------------------------------------------------------- | ---------------------------------- |
| week1.intent_records    | Path known; exact upstream shape not yet fully confirmed | intent_records.jsonl canonical name and governed record semantics | shape semantics     | preserve canonical shape; document field-level gap               | inferred_from_requirement_document |
| week2.verdicts          | Path known; authoritative semantics still under review   | verdicts.jsonl canonical record set                               | readiness           | confirm repository evidence and maintain standard                | inferred_from_requirement_document |
| week3.extractions       | Upstream content may not match canonical meaning         | extraction canonical standard                                     | filename + semantic | normalize upstream or migrate producer output                    | blocked_by_missing_upstream_data   |
| week4.lineage_snapshots | Trace data expected; full lineage confidence pending     | lineage snapshot canonical standard                               | readiness           | retain canonical target and verify lineage integrity             | inferred_from_requirement_document |
| week5.events            | Event semantics may require normalization                | event canonical standard                                          | semantic            | do not rewrite business meaning silently; document normalization | pending_migration_or_normalization |
| traces.runs             | Repository structure currently supports trace runs       | run trace canonical standard                                      | none known          | preserve canonical path and maintain readiness checks            | confirmed_from_repository_evidence |

## Schema Reality Notes

- Canonical filenames and field semantics are the platform standard, even if upstream systems differ.
- Every mismatch must be recorded explicitly and linked to migration or normalization requirements.
- A field that looks similar but carries different business meaning must be treated as a semantic mismatch.
- Readiness status must be exposed per governed dataset and kept in sync with the dataset readiness inventory.

## Foundational Constraints

- No later feature may redefine canonical paths or ownership boundaries without updating these notes first.
- No silent rewriting of business meaning is permitted.
- Evidence-backed repository observations take precedence over inference.
