# Tasks: Violation Attribution and Blast Radius Analysis

**Input**: Design documents from /specs/004-violation-attribution/
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: No test-first tasks are included because the specification and request do not require a TDD workflow.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on incomplete tasks)
- **[Story]**: User story label (`[US1]`, `[US2]`, `[US3]`) for story-phase tasks only
- Every task includes expected files and acceptance criteria inline.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Feature 4 scaffolding and canonical CLI entry behavior.

- [ ] T001 Create Feature 4 module scaffolding in src/attribution/**init**.py, src/models/attribution_models.py, and src/validators/violation_record_validator.py (Files: src/attribution/**init**.py, src/models/attribution_models.py, src/validators/violation_record_validator.py; AC: modules import cleanly and expose typed placeholders for attribution flow).
- [ ] T002 Add attribution CLI scaffold in contracts/attributor.py with argument parsing for report selection, dry-run mode, and output path override (Files: contracts/attributor.py; AC: command executes and prints structured summary without implementing full attribution logic yet).
- [ ] T003 [P] Add Feature 4 invocation path in src/cli/foundation.py for `attribute-violations` command dispatch (Files: src/cli/foundation.py; AC: foundation CLI can invoke contracts/attributor.py and return JSON output).
- [ ] T004 [P] Add default output path guardrails and directory bootstrap for violation_log/violations.jsonl (Files: contracts/attributor.py, src/attribution/violation_writer.py; AC: first run creates violation_log directory safely without writing invalid records).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared attribution primitives required by all user stories.

**⚠️ CRITICAL**: No user story work starts until this phase is complete.

- [ ] T005 Implement typed attribution entities and enums from data-model.md in src/models/attribution_models.py (Files: src/models/attribution_models.py; AC: models include ViolationRecord, BlameCandidate, BlastRadiusSummary, and validation constraints for score range and candidate count).
- [ ] T006 [P] Implement Feature 1 metadata loaders for interface registry and schema ownership map in src/attribution/artifact_resolver.py (Files: src/attribution/artifact_resolver.py; AC: canonical contracts/interface_registry.yaml and contracts/schema_ownership_map.yaml parse into typed maps with explicit parse errors).
- [ ] T007 [P] Implement Feature 2 contract metadata loader for field/check mapping support in src/attribution/schema_mapper.py (Files: src/attribution/schema_mapper.py; AC: generated_contracts/\*.yaml can be loaded and indexed by contract_id and field path).
- [ ] T008 Implement validation report ingestion primitives with deterministic report/result ordering in src/attribution/validation_failure_loader.py (Files: src/attribution/validation_failure_loader.py; AC: validation_reports/\*.json parsed deterministically with malformed-report handling and stable sort keys).
- [ ] T009 [P] Implement violation record schema validation in src/validators/violation_record_validator.py (Files: src/validators/violation_record_validator.py; AC: validator enforces required fields including violation_id, check_id, detected_at, blame_chain[], and blast_radius{}).
- [ ] T010 [P] Implement deterministic violation identity utility and dedupe index helpers in src/attribution/result_aggregator.py (Files: src/attribution/result_aggregator.py; AC: identical identity inputs produce identical violation_id and dedupe lookups are stable across runs).
- [ ] T011 Implement append-safe JSONL writer foundation in src/attribution/violation_writer.py (Files: src/attribution/violation_writer.py; AC: writes valid JSONL lines atomically, preserves prior records, and supports duplicate suppression by violation_id).

**Checkpoint**: Foundation ready for story implementation.

---

## Phase 3: User Story 1 - Attribute Violations to Plausible Origins (Priority: P1) 🎯 MVP

**Goal**: Convert eligible validation failures into governed schema anchors and upstream lineage-based attribution candidates.

**Independent Test**: Run attribution on Feature 3 validation reports and confirm each attributable violation yields 1..N bounded upstream candidates with explicit uncertainty when mapping is partial.

### Implementation for User Story 1

- [ ] T012 [US1] Implement attribution eligibility filter (`FAIL` + selected attributable `ERROR` classes) and non-eligible skip reasons in src/attribution/validation_failure_loader.py (Files: src/attribution/validation_failure_loader.py; AC: eligible and skipped results are separated with explicit reason codes).
- [ ] T013 [US1] Implement failure-to-schema-element mapping using check_id, column_name, and dataset-level fallback anchors in src/attribution/schema_mapper.py (Files: src/attribution/schema_mapper.py; AC: field-level and dataset-level checks map to governed schema/interface anchors or emit non-attributable reason).
- [ ] T014 [US1] Implement latest valid Week 4 lineage snapshot selection from outputs/week4/lineage_snapshots.jsonl using in-record timestamp precedence with deterministic fallback (Files: src/attribution/lineage_selector.py; AC: snapshot selection is deterministic and invalid lines are reported without halting run).
- [ ] T015 [US1] Implement lineage graph normalization and upstream BFS traversal engine with bounded hop count in src/attribution/lineage_graph.py (Files: src/attribution/lineage_graph.py; AC: traversal follows upstream direction and records stop_reason for each terminated path).
- [ ] T016 [US1] Implement lineage-node to repository-file and owned-artifact resolution in src/attribution/artifact_resolver.py (Files: src/attribution/artifact_resolver.py; AC: resolved candidates include source node, candidate file paths, and ownership/interface references when available).
- [ ] T017 [US1] Wire US1 pipeline in contracts/attributor.py from validation loader -> schema mapper -> lineage selector/traversal -> artifact resolution (Files: contracts/attributor.py; AC: command emits structured in-memory attribution candidates without git enrichment or blast radius yet).
- [ ] T018 [US1] Enforce attributable-violation guardrail (only governed dataset/interface/lineage-connected failures proceed) in contracts/attributor.py and src/attribution/schema_mapper.py (Files: contracts/attributor.py, src/attribution/schema_mapper.py; AC: non-governed failures are recorded as skipped and never produce fabricated blame candidates).
- [ ] T019 [US1] Add graceful-degradation handling for missing/incomplete lineage with explicit uncertainty fields in src/attribution/lineage_graph.py and src/attribution/result_aggregator.py (Files: src/attribution/lineage_graph.py, src/attribution/result_aggregator.py; AC: run continues and candidates include uncertainty_reasons when lineage is partial or stale).

**Checkpoint**: US1 independently complete and reviewable.

---

## Phase 4: User Story 2 - Link Violations to Change History (Priority: P2)

**Goal**: Enrich attribution candidates with bounded git evidence and confidence-ranked blame chains.

**Independent Test**: For attributable violations, verify git-enriched candidates include recent commit evidence, optional line blame (when ranges exist), normalized confidence scores, and stable ranking.

### Implementation for User Story 2

- [ ] T020 [US2] Implement bounded git log integration (90-day window, per-file commit cap) in src/attribution/git_enricher.py (Files: src/attribution/git_enricher.py; AC: candidate files produce commit evidence with hash, author, timestamp, and summary while respecting configured limits).
- [ ] T021 [US2] Implement source-range derivation from lineage metadata and conditional line-level blame execution in src/attribution/git_enricher.py (Files: src/attribution/git_enricher.py; AC: blame runs only when start/end ranges are valid and otherwise falls back to file-level history with explicit marker).
- [ ] T022 [US2] Implement confidence scoring formula normalization factors and score clamping in src/attribution/confidence_scorer.py (Files: src/attribution/confidence_scorer.py; AC: score is 0..100 and factors include recency, hop proximity, directness, blame availability, and lineage completeness).
- [ ] T023 [US2] Implement bounded candidate count and stable ranking/tie-break rules in src/attribution/result_aggregator.py (Files: src/attribution/result_aggregator.py; AC: attributable violations return 1..5 candidates sorted by score desc, hops asc, commit time desc, hash asc).
- [ ] T024 [US2] Implement low-confidence representation (`confidence_band` + uncertainty_reasons) and optional attribution_confidence_summary in src/attribution/result_aggregator.py (Files: src/attribution/result_aggregator.py; AC: non-high confidence candidates always carry uncertainty reasons and summary remains machine-readable).
- [ ] T025 [US2] Wire git enrichment and scoring into contracts/attributor.py execution pipeline (Files: contracts/attributor.py, src/attribution/git_enricher.py, src/attribution/confidence_scorer.py; AC: CLI output includes ranked blame_chain entries with commit evidence and confidence metadata).
- [ ] T026 [US2] Add graceful-degradation policy for missing git history/shallow clones in src/attribution/git_enricher.py and src/attribution/result_aggregator.py (Files: src/attribution/git_enricher.py, src/attribution/result_aggregator.py; AC: run continues with lineage-only attribution and explicit uncertainty annotations).

**Checkpoint**: US2 independently complete and reviewable.

---

## Phase 5: User Story 3 - Estimate Blast Radius for Prioritization (Priority: P3)

**Goal**: Compute structured downstream impact and persist deterministic, append-safe violation records.

**Independent Test**: Run full attribution and confirm each persisted violation record includes blast_radius dimensions (nodes/pipelines/interfaces/estimated impact), direct vs indirect split, and structured partial-knowledge representation.

### Implementation for User Story 3

- [ ] T027 [US3] Implement downstream lineage traversal and blast radius aggregation in src/attribution/blast_radius.py (Files: src/attribution/blast_radius.py; AC: blast_radius contains affected_nodes, affected_pipelines, affected_interfaces, and estimated impacted records/datasets where inferable).
- [ ] T028 [US3] Implement direct (1-hop) vs indirect (>=2-hop) downstream impact separation in src/attribution/blast_radius.py (Files: src/attribution/blast_radius.py; AC: direct_impact and indirect_impact sections are populated according to hop-based rules).
- [ ] T029 [US3] Implement partial-knowledge encoding for incomplete downstream mappings in src/attribution/blast_radius.py (Files: src/attribution/blast_radius.py; AC: knowledge_completeness and unknown_downstream_count are set consistently when mappings are incomplete).
- [ ] T030 [US3] Implement full violation record assembly and validation before write in src/attribution/result_aggregator.py and src/validators/violation_record_validator.py (Files: src/attribution/result_aggregator.py, src/validators/violation_record_validator.py; AC: records include required identity fields, blame_chain[], blast_radius{}, and optional confidence summary with schema validation pass).
- [ ] T031 [US3] Implement deterministic ordering + append-safe persistence + dedupe into violation_log/violations.jsonl in src/attribution/violation_writer.py (Files: src/attribution/violation_writer.py; AC: reruns on unchanged inputs do not duplicate existing records and preserve stable record ordering semantics).
- [ ] T032 [US3] Wire final end-to-end attribution flow in contracts/attributor.py (Files: contracts/attributor.py, src/attribution/blast_radius.py, src/attribution/violation_writer.py; AC: one persisted record per attributable violation with complete structured fields and run summary output).

**Checkpoint**: US3 independently complete and reviewable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize workflow documentation, boundary guardrails, and execution evidence.

- [ ] T033 Update attribution workflow usage and artifact semantics in README.md (Files: README.md; AC: docs include command usage, primary inputs, output path, deterministic behavior, and graceful degradation notes).
- [ ] T034 [P] Add/refresh feature quickstart verification steps for attribution execution and output validation in specs/004-violation-attribution/quickstart.md (Files: specs/004-violation-attribution/quickstart.md; AC: quickstart aligns with implemented command and record schema checks).
- [ ] T035 [P] Finalize artifact contract documentation for violation records in specs/004-violation-attribution/contracts/violation-artifacts.md (Files: specs/004-violation-attribution/contracts/violation-artifacts.md; AC: documented fields and behavioral guarantees match implementation).
- [ ] T036 Add explicit scope-guard checks to prevent schema evolution classification, AI-specific checks, stakeholder report generation, and validation execution in contracts/attributor.py (Files: contracts/attributor.py; AC: unsupported modes are rejected with clear messages and no out-of-scope behavior is executed).
- [ ] T037 Run end-to-end attribution on canonical inputs and capture completion evidence in specs/004-violation-attribution/plan.md (Files: specs/004-violation-attribution/plan.md; AC: plan records produced violations path, summary counts, and degradation behavior observations from real execution).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Story Phases (3-5)**: Depend on Foundational completion.
  - Execute in priority order for incremental value (US1 -> US2 -> US3).
  - US2 depends on US1 mapping/traversal outputs.
  - US3 depends on US1+US2 finalized candidate structures.
- **Polish (Phase 6)**: Depends on completion of desired user stories.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; no dependency on other stories.
- **US2 (P2)**: Starts after US1 checkpoint because git enrichment/scoring operates on US1 candidate structures.
- **US3 (P3)**: Starts after US1+US2 checkpoints because blast radius and persistence require finalized ranked attribution outputs.

### Dependency Graph (Story Completion Order)

`US1 -> US2 -> US3`

### Within Each User Story

- Loaders/mappers before traversal/enrichment.
- Traversal/enrichment before ranking.
- Ranking before record assembly.
- Record assembly before persistence.

---

## Parallel Opportunities

- **Phase 1**: T003 and T004 can run in parallel after T002 starts.
- **Phase 2**: T006, T007, T009, and T010 can run in parallel after T005.
- **US1**: T014 and T016 can run in parallel after T013; T019 can run in parallel with T018 after T017.
- **US2**: T020 and T022 can run in parallel; T024 and T026 can run in parallel after T023.
- **US3**: T028 and T029 can run in parallel after T027; T034 and T035 can run in parallel in Phase 6.

### Parallel Example: User Story 1

- Run T014 (lineage snapshot selector) and T016 (artifact resolver) in parallel after T013 mapping contract is stable.
- Run T018 (governed-anchor guardrail) and T019 (lineage degradation handling) in parallel after T017 pipeline wiring.

### Parallel Example: User Story 2

- Run T020 (git log integration) and T022 (confidence scoring module) in parallel.
- Run T024 (confidence summary/uncertainty shaping) and T026 (git-missing degradation) in parallel after ranking contract from T023.

### Parallel Example: User Story 3

- Run T028 (direct/indirect split) and T029 (partial-knowledge encoding) in parallel after T027 base blast radius aggregation.
- Run T034 and T035 documentation updates in parallel during polish.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate independent US1 behavior on canonical validation reports.
4. Stop and review before git enrichment and blast radius expansion.

### Incremental Delivery

1. Setup + Foundational -> stable attribution primitives.
2. Deliver US1 -> governed upstream attribution baseline.
3. Deliver US2 -> git-enriched confidence-ranked blame chains.
4. Deliver US3 -> downstream blast radius + durable violation log output.
5. Finish with polish and execution evidence.

### Parallel Team Strategy

1. Team aligns on Phase 1 + Phase 2 interfaces.
2. Developer A drives US1 mapping/traversal.
3. Developer B drives US2 git enrichment/scoring once US1 contracts are ready.
4. Developer C drives US3 blast radius/persistence once ranked candidate contracts are ready.

---

## Notes

- All tasks preserve canonical paths and reuse Feature 1-3 artifact contracts.
- No task implements schema evolution classification, AI-specific checks, stakeholder report generation, or validation execution.
- All task lines follow strict checklist format with Task ID, optional [P], optional [USx], explicit files, and acceptance criteria.
