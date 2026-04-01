# Tasks: Contract Generation Engine

**Input**: Design documents from specs/002-contract-generation-engine/
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: No test-first tasks are included because the spec does not explicitly require a TDD workflow. Validation is via story-level independent test criteria and artifact checks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on incomplete tasks)
- **[Story]**: User story label (`[US1]`, `[US2]`, `[US3]`) for story-phase tasks only
- Every task includes expected files and acceptance criteria in-line.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize durable generator scaffolding and canonical feature wiring.

- [x] T001 Create Feature 2 generation package scaffolding in src/generation/**init**.py, src/models/contract_models.py, and src/validators/contract_quality_validator.py (Files: src/generation/**init**.py, src/models/contract_models.py, src/validators/contract_quality_validator.py; AC: modules import cleanly and expose typed stubs used by later tasks).
- [x] T002 [P] Add YAML rendering dependency and generation extras in pyproject.toml (Files: pyproject.toml; AC: dependency set includes PyYAML and install resolves without altering canonical project layout).
- [x] T003 [P] Add generator command entry wiring in contracts/generator.py and src/cli/foundation.py (Files: contracts/generator.py, src/cli/foundation.py; AC: generator entrypoint callable exists and routes to orchestration without implementing validation/attribution/reporting behavior).
- [x] T004 Capture Feature 2 operational guidance skeleton in specs/002-contract-generation-engine/quickstart.md (Files: specs/002-contract-generation-engine/quickstart.md; AC: quickstart references canonical Week 3/Week 5 inputs and canonical generated_contracts output paths).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared core modules required by all user stories.

**⚠️ CRITICAL**: No user story work starts until this phase is complete.

- [x] T005 Implement canonical artifact resolver for Feature 1 dependencies in src/generation/dataset_loader.py (Files: src/generation/dataset_loader.py; AC: loader reads contracts/canonical_paths.yaml, contracts/dataset_readiness.json, contracts/interface_registry.yaml, contracts/schema_ownership_map.yaml, contracts/requirement_traceability.yaml, DOMAIN_NOTES.md without path drift).
- [x] T006 Implement internal contract data model types in src/models/contract_models.py (Files: src/models/contract_models.py; AC: typed entities cover DatasetTarget, ProfiledField, InvariantClause, DownstreamContextAnnotation, CanonicalMismatchRecord, GeneratedContract, DbtSchemaArtifact, GenerationMetadata).
- [x] T007 [P] Implement deterministic writer and metadata signature utility in src/generation/deterministic_writer.py (Files: src/generation/deterministic_writer.py; AC: stable ordering + atomic write + deterministic signature are implemented, with only timestamp/version metadata allowed to vary).
- [x] T008 [P] Implement generation quality guardrails in src/validators/contract_quality_validator.py (Files: src/validators/contract_quality_validator.py; AC: validator enforces canonical output names, required metadata fields, and prohibition of out-of-scope runner/attribution/evolution/report execution behavior).
- [x] T009 Add shared orchestration interfaces in contracts/schema_analyzer.py and src/generation/schema_inference.py (Files: contracts/schema_analyzer.py, src/generation/schema_inference.py; AC: schema analyzer delegates to generation modules and supports nested path representation + parent-child retention).
- [x] T010 Create renderer interfaces for Bitol and dbt outputs in src/generation/renderers.py (Files: src/generation/renderers.py; AC: renderer contracts support primary Bitol YAML + dbt YAML counterpart generation and explicit unsupported mapping notes).

**Checkpoint**: Foundation ready for story implementation.

---

## Phase 3: User Story 1 - Baseline Contract Generation (Priority: P1) 🎯 MVP

**Goal**: Generate baseline contracts for Week 3 and Week 5 from canonical JSONL inputs with structural/statistical profiling and invariant synthesis.

**Independent Test**: Running generator produces both canonical primary contract files for week3/week5 with structural profiles, statistical summaries, inferred + requirement-defined invariants, and uncertainty/mismatch annotations when needed.

- [x] T011 [US1] Implement canonical JSONL dataset loader with malformed-line tolerance in src/generation/dataset_loader.py (Files: src/generation/dataset_loader.py; AC: supports outputs/week3/extractions.jsonl and outputs/week5/events.jsonl, records malformed-line diagnostics, and preserves run continuity when possible).
- [x] T012 [P] [US1] Implement structural profiling engine for fields and nested fields in src/generation/profilers.py (Files: src/generation/profilers.py; AC: outputs field paths, parent paths, type frequencies, presence/null rates, and nested coverage where feasible).
- [x] T013 [P] [US1] Implement statistical profiling engine in src/generation/profilers.py (Files: src/generation/profilers.py; AC: computes numeric summaries, enum candidacy frequencies, uniqueness indicators, and sparse-field signals for clause synthesis).
- [x] T014 [US1] Implement invariant synthesis from observed data plus requirement-defined rules for Week 3/Week 5 in src/generation/invariant_synthesizer.py (Files: src/generation/invariant_synthesizer.py; AC: emits required/range/enum/pattern/positivity/monotonicity_candidate/relationship/dataset_check clauses, preserving requirement-document constraints even when samples currently comply).
- [x] T015 [US1] Implement weak-semantic-confidence handling in src/generation/invariant_synthesizer.py and src/models/contract_models.py (Files: src/generation/invariant_synthesizer.py, src/models/contract_models.py; AC: unsupported business meaning is never invented, explicit uncertainty placeholders/notes are emitted, and structural baseline generation never fails solely due to low semantic confidence).
- [x] T016 [US1] Implement Bitol-compatible contract rendering for Week 3 and Week 5 in src/generation/renderers.py and contracts/generator.py (Files: src/generation/renderers.py, contracts/generator.py; AC: writes generated_contracts/week3_extractions.yaml and generated_contracts/week5_events.yaml with canonical schema targeting + mismatch evidence sections).
- [x] T017 [US1] Wire US1 end-to-end orchestration in contracts/generator.py (Files: contracts/generator.py; AC: single run resolves canonical inputs, profiles datasets, synthesizes invariants, and emits primary outputs + generation metadata without invoking validation runner responsibilities).

**Checkpoint**: US1 independently complete and reviewable.

---

## Phase 4: User Story 2 - Downstream Context Preservation (Priority: P2)

**Goal**: Embed lineage-aware downstream consumer context in generated contracts using Feature 1 and Week 4 metadata.

**Independent Test**: Generated contracts include downstream systems, consumed fields, likely breaking fields, and consumer-facing change sensitivity with explicit partial/unknown markers when lineage metadata is incomplete.

- [x] T018 [US2] Implement lineage/interface metadata ingestion in src/generation/lineage_injector.py (Files: src/generation/lineage_injector.py; AC: consumes contracts/interface_registry.yaml, contracts/schema_ownership_map.yaml, and outputs/week4/lineage_snapshots.jsonl when available).
- [x] T019 [US2] Implement downstream context injection model mapping in src/generation/lineage_injector.py and src/models/contract_models.py (Files: src/generation/lineage_injector.py, src/models/contract_models.py; AC: populates downstream_systems, consumed_fields, likely_breaking_fields, consumer_change_sensitivity, and coverage_status).
- [x] T020 [US2] Integrate lineage context injection into generator orchestration in contracts/generator.py (Files: contracts/generator.py; AC: every generated contract carries downstream context annotations or explicit partial_context markers with source references).
- [x] T021 [US2] Add canonical mismatch/context evidence logging in src/generation/deterministic_writer.py and validation_reports/readiness_index.json metadata flow (Files: src/generation/deterministic_writer.py, validation_reports/readiness_index.json; AC: output metadata captures lineage coverage state and mismatch evidence references without implementing blast-radius calculations).

**Checkpoint**: US2 independently complete and reviewable.

---

## Phase 5: User Story 3 - Extensible Dual-Format Outputs (Priority: P3)

**Goal**: Produce dbt-compatible counterpart artifacts and deterministic multi-dataset output behavior with extension-ready architecture.

**Independent Test**: Generator emits canonical dbt counterparts for Week 3/Week 5, deterministic outputs across unchanged runs, and remains dataset-config extensible without core pipeline rewrites.

- [x] T022 [US3] Implement dbt-compatible schema YAML renderer in src/generation/renderers.py (Files: src/generation/renderers.py; AC: outputs generated_contracts/week3_extractions_dbt.yml and generated_contracts/week5_events_dbt.yml with supported mappings: not_null, accepted_values, relationships, unique).
- [x] T023 [US3] Add unsupported-clause mapping notes and counterpart trace metadata in src/generation/renderers.py and src/models/contract_models.py (Files: src/generation/renderers.py, src/models/contract_models.py; AC: unsupported clause mappings are explicitly recorded, not dropped silently).
- [x] T024 [US3] Implement deterministic output write policy and run metadata in src/generation/deterministic_writer.py and contracts/generator.py (Files: src/generation/deterministic_writer.py, contracts/generator.py; AC: repeated unchanged-input runs produce diff-stable artifacts except allowed timestamp/version metadata fields).
- [x] T025 [US3] Implement dataset-target configuration routing for future governed datasets in src/generation/dataset_loader.py and contracts/generator.py (Files: src/generation/dataset_loader.py, contracts/generator.py; AC: architecture supports adding week1/week2/week4/traces via configuration/artifact registration without per-dataset code forks).
- [x] T026 [US3] Finalize output naming/versioning enforcement in src/validators/contract_quality_validator.py and src/generation/deterministic_writer.py (Files: src/validators/contract_quality_validator.py, src/generation/deterministic_writer.py; AC: canonical output filenames and required metadata contracts are strictly enforced for week3/week5 artifacts).

**Checkpoint**: US3 independently complete and reviewable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and capability hardening across all stories.

- [x] T027 Update user-facing generator usage in README.md (Files: README.md; AC: documents generator invocation, required Feature 1 artifacts, canonical input/output paths, and explicit out-of-scope responsibilities).
- [x] T028 [P] Align feature quickstart with finalized command/outputs in specs/002-contract-generation-engine/quickstart.md (Files: specs/002-contract-generation-engine/quickstart.md; AC: quickstart reflects actual generator workflow and all four canonical output files).
- [x] T029 [P] Update generator artifact contract documentation in specs/002-contract-generation-engine/contracts/generator-artifacts.md (Files: specs/002-contract-generation-engine/contracts/generator-artifacts.md; AC: docs match implemented Bitol/dbt rendering, metadata, determinism, and failure-status behavior).
- [x] T030 Run full end-to-end generation sanity pass and capture completion notes in specs/002-contract-generation-engine/plan.md (Files: specs/002-contract-generation-engine/plan.md; AC: plan records completion evidence for Week 3/Week 5 outputs and confirms no validation-runner/attribution/evolution/report behavior was implemented).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: starts immediately.
- **Phase 2 (Foundational)**: depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: depends on Phase 2.
- **Phase 4 (US2)**: depends on Phase 2; integrates cleanly with US1 outputs.
- **Phase 5 (US3)**: depends on Phase 2; integrates with US1 and US2 generated models.
- **Phase 6 (Polish)**: depends on completion of targeted user stories.

### User Story Dependencies

- **US1 (P1)**: first MVP slice; no dependency on other user stories.
- **US2 (P2)**: depends on foundational model/orchestration from US1 for contract attachment points.
- **US3 (P3)**: depends on US1 contract model and rendering surfaces; can proceed after US1 core paths exist.

### Within Each User Story

- Loader/profile/model foundations before clause/render integrations.
- Core generation before deterministic/polish checks.
- Story checkpoint reached only after independent test criteria pass.

### Parallel Opportunities

- Setup: `T002`, `T003` can run in parallel.
- Foundational: `T007`, `T008` can run in parallel after `T005`/`T006` interface alignment.
- US1: `T012` and `T013` parallel after `T011`.
- Polish: `T028` and `T029` parallel after implementation stabilizes.

---

## Parallel Example: User Story 1

- Parallel Task A: `T012 [US1]` in `src/generation/profilers.py` (structural profiling)
- Parallel Task B: `T013 [US1]` in `src/generation/profilers.py` (statistical profiling)

After both complete, continue with `T014` (invariant synthesis) and `T016` (Bitol rendering integration).

---

## Implementation Strategy

### MVP First (US1 only)

1. Complete Setup (Phase 1).
2. Complete Foundational (Phase 2).
3. Complete US1 (Phase 3).
4. Validate canonical Week 3 + Week 5 contract generation artifacts.
5. Stop for review before downstream enrichment.

### Incremental Delivery

1. Ship US1 baseline generation.
2. Add US2 lineage/downstream context enrichment.
3. Add US3 dual-format + deterministic extensibility.
4. Polish docs and completion evidence.

### Parallel Team Strategy

1. Team member A: loader/profiling/invariant synthesis (`T011`-`T015`).
2. Team member B: lineage context injection (`T018`-`T021`) after core model stabilizes.
3. Team member C: dbt/deterministic output work (`T022`-`T026`) after renderer interfaces exist.

---

## Notes

- All tasks preserve canonical paths and metadata contracts from Feature 1.
- No task includes validation execution, violation attribution, schema evolution diffing, AI-specific checks, or report generation behavior.
- Each task is scoped as a small, reviewable, durable capability increment.
