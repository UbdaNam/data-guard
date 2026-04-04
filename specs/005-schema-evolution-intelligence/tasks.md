# Tasks: Schema Evolution Intelligence

**Input**: Design documents from /specs/005-schema-evolution-intelligence/
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/schema-evolution-artifacts.md, quickstart.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create feature module skeleton and deterministic CLI wiring.

- [ ] T001 Create evolution package and exports in src/evolution/**init**.py
- [ ] T002 [P] Create schema evolution model file skeleton in src/models/schema_evolution_models.py
- [ ] T003 [P] Create schema evolution validator skeleton in src/validators/schema_evolution_validator.py
- [ ] T004 Wire Feature 5 CLI command surface (`--snapshot`, pair selection, output options) in contracts/schema_analyzer.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement shared building blocks required by all stories.

**⚠️ CRITICAL**: No user story work starts before this phase is complete.

- [ ] T005 Implement canonical schema normalization primitives in src/evolution/normalizer.py
- [ ] T006 [P] Implement deterministic snapshot identity/hash utilities in src/evolution/snapshot_writer.py
- [ ] T007 [P] Implement snapshot loading, validation, and malformed-snapshot warnings in src/evolution/snapshot_loader.py
- [ ] T008 [P] Define core Pydantic entities from data-model.md in src/models/schema_evolution_models.py
- [ ] T009 Implement compatibility taxonomy rule engine (dual-axis -> verdict) in src/evolution/classifier.py
- [ ] T010 Implement end-to-end pipeline orchestration shell (load -> diff -> classify -> render) in src/evolution/pipeline.py

**Checkpoint**: Foundation ready; user stories can proceed.

---

## Phase 3: User Story 1 - Detect and Classify Schema Change (Priority: P1) 🎯 MVP

**Goal**: Persist snapshots, compute deterministic diffs, and classify compatibility for contract changes.

**Independent Test**: For one Week 3/Week 5 contract, write snapshot(s), compare latest-vs-previous and explicit pair, and verify stable structured diff + compatibility verdict.

- [ ] T011 [US1] Implement append-only snapshot write with dedupe (`no_material_change`) in src/evolution/snapshot_writer.py (AC: duplicate latest schema hash does not create a new snapshot file)
- [ ] T012 [P] [US1] Implement field matching precedence (exact -> explicit rename -> heuristic) in src/evolution/matcher.py (AC: low-confidence rename falls back to remove+add)
- [ ] T013 [P] [US1] Implement deterministic flat+nested diff computation and change classes in src/evolution/differ.py (AC: emits all required change classes from contract)
- [ ] T014 [US1] Integrate classifier with per-change and aggregate verdict generation in src/evolution/classifier.py (AC: outputs backward/forward booleans and derived verdict)
- [ ] T015 [US1] Implement deterministic evolution report rendering in src/evolution/renderer.py (AC: writes validation*reports/schema_evolution*{contract_id}.json with stable ordering)
- [ ] T016 [US1] Extend orchestration for latest-vs-previous and explicit snapshot pair selection in src/evolution/pipeline.py (AC: rejects cross-contract pair, supports explicit ids)
- [ ] T017 [US1] Add evolution artifact contract validation rules in src/validators/schema_evolution_validator.py (AC: required sections and deterministic ordering are validated)
- [ ] T018 [US1] Finalize CLI execution path for User Story 1 flows in contracts/schema_analyzer.py (AC: snapshot-only baseline mode works when no prior snapshot exists)

**Checkpoint**: User Story 1 is independently functional.

---

## Phase 4: User Story 2 - Produce Operational Migration Intelligence (Priority: P2)

**Goal**: Generate actionable migration impact outputs with urgency, failure modes, and rollback guidance.

**Independent Test**: Introduce a breaking schema change and verify migration output includes affected consumers, failure modes, urgency, checklist actions, and rollback guidance.

- [ ] T019 [US2] Implement migration impact report assembly model bindings in src/models/schema_evolution_models.py (AC: report schema includes required sections from contracts doc)
- [ ] T020 [P] [US2] Implement affected-consumer resolution from Feature 1 ownership/interface artifacts in src/evolution/migration_generator.py (AC: preserves consumer + ownership context when present)
- [ ] T021 [P] [US2] Implement likely failure mode derivation by change class in src/evolution/migration_generator.py (AC: each impacted consumer has non-empty likely_failure_modes)
- [ ] T022 [US2] Implement ordered actionable migration checklist generation in src/evolution/migration_generator.py (AC: each item contains owner, action, target, verification)
- [ ] T023 [US2] Implement rollback guidance and urgency assignment logic in src/evolution/migration_generator.py (AC: breaking verdict always includes rollback_guidance)
- [ ] T024 [US2] Render migration artifact file output in src/evolution/renderer.py (AC: writes migration*impact*{contract*id}*{timestamp}.json deterministically)
- [ ] T025 [US2] Integrate migration generation into orchestrated run path in src/evolution/pipeline.py (AC: one run emits both evolution and migration artifacts)

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Reusable Cross-Feature Evolution Context (Priority: P3)

**Goal**: Enrich severity/confidence/prioritization using optional Feature 3/4 evidence without breaking baseline outputs.

**Independent Test**: Run analysis with and without Feature 3/4 artifacts and confirm deterministic baseline output remains complete while enrichment fields appear when context exists.

- [ ] T026 [US3] Implement optional context ingestion for Feature 3/4 artifacts in src/evolution/context_enricher.py (AC: missing artifacts downgrade completeness, not execution success)
- [ ] T027 [P] [US3] Implement severity/confidence/prioritization adjustment policy in src/evolution/context_enricher.py (AC: baseline schema verdict unchanged when enrichment absent)
- [ ] T028 [US3] Integrate enricher into orchestration with explicit completeness flags in src/evolution/pipeline.py (AC: context_completeness is complete/partial/minimal as applicable)
- [ ] T029 [US3] Extend renderers to persist enrichment_sources and confidence fields in src/evolution/renderer.py (AC: enrichment provenance is machine-readable)
- [ ] T030 [US3] Enforce Feature 5 boundaries in CLI and validator paths in contracts/schema_analyzer.py (AC: no validation execution, no git-blame attribution, no stakeholder-report generation)

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, documentation, and execution validation.

- [ ] T031 [P] Add deterministic sorting and id stability guards across diff/render flow in src/evolution/differ.py
- [ ] T032 [P] Add graceful-degradation warning normalization and error messaging in src/evolution/snapshot_loader.py
- [ ] T033 Update operator documentation and usage examples for Feature 5 in README.md
- [ ] T034 Execute quickstart validation scenarios and capture findings in specs/005-schema-evolution-intelligence/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 (Setup): no dependencies.
- Phase 2 (Foundational): depends on Phase 1; blocks all story work.
- Phase 3 (US1): depends on Phase 2.
- Phase 4 (US2): depends on US1 outputs (diff + compatibility artifacts).
- Phase 5 (US3): depends on US1 + US2 outputs and integrates optional context.
- Phase 6 (Polish): depends on all implemented stories.

### User Story Dependencies

- US1 (P1): first deliverable and MVP.
- US2 (P2): depends on US1 report/diff output shape.
- US3 (P3): depends on US1 baseline and US2 migration output structure.

### Parallel Opportunities

- Setup: T002 and T003 parallel after T001.
- Foundational: T006, T007, T008 parallel after T005.
- US1: T012 and T013 parallel after T011.
- US2: T020 and T021 parallel after T019.
- US3: T027 parallel with initial T026 scaffolding once ingestion contracts are defined.
- Polish: T031 and T032 parallel.

---

## Parallel Example: User Story 1

- Run T012 [US1] in src/evolution/matcher.py and T013 [US1] in src/evolution/differ.py at the same time.
- Merge both before T014 classifier integration.

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 + Phase 2.
2. Complete US1 tasks (T011-T018).
3. Validate snapshot write/dedupe, deterministic diff, and compatibility verdict outputs.

### Incremental Delivery

1. Deliver MVP (US1).
2. Add migration intelligence (US2).
3. Add optional cross-feature enrichment (US3).
4. Run final polish tasks and quickstart validation.

### Small-Batch Review Guidance

- Keep each task scoped to one file whenever possible.
- Prefer merging in dependency order (T001 -> T034).
- Validate artifact contracts at each phase checkpoint before moving forward.

---

## Notes

- All tasks follow required checklist format: `- [ ] T### [P?] [US?] Description with file path`.
- Story labels are applied only to user-story phases.
- Out-of-scope actions remain excluded by design: validation execution, blame attribution, stakeholder-facing final report generation.
