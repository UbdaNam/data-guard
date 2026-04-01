# Tasks: Platform Foundation and Canonical Data Surface

**Input**: Design documents from `/specs/001-platform-data-surface/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are not included because the feature specification does not explicitly require TDD or dedicated test implementation in this phase.

**Organization**: Tasks are grouped by user story so each story remains independently implementable and reviewable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Each task includes expected files and acceptance criteria inline.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish canonical Python project skeleton and required repository surfaces.

- [ ] T001 Create canonical directories for foundation assets and outputs scaffold in contracts/, generated_contracts/, validation_reports/, violation_log/, schema_snapshots/, enforcer_report/, outputs/week1/, outputs/week2/, outputs/week3/, outputs/week4/, outputs/week5/, outputs/traces/ (Files: contracts/.gitkeep, generated_contracts/.gitkeep, validation_reports/.gitkeep, violation_log/.gitkeep, schema_snapshots/.gitkeep, enforcer_report/.gitkeep, outputs/week1/.gitkeep, outputs/week2/.gitkeep, outputs/week3/.gitkeep, outputs/week4/.gitkeep, outputs/week5/.gitkeep, outputs/traces/.gitkeep; AC: all canonical directories exist and are commit-visible).
- [ ] T002 [P] Scaffold required Python entrypoint stubs without implementing runtime capabilities in contracts/generator.py, contracts/runner.py, contracts/attributor.py, contracts/schema_analyzer.py, contracts/ai_extensions.py, contracts/report_generator.py (Files: six contracts/\*.py files; AC: each file has module docstring + NotImplementedError placeholder and explicitly states deferred capability scope).
- [ ] T003 [P] Initialize Python foundation package layout in src/cli/foundation.py, src/models/registry_models.py, src/models/readiness_models.py, src/validators/path_validator.py, src/validators/readiness_validator.py (Files: listed src/\*.py files; AC: import-safe modules exist with typed placeholders and no later-feature business logic).
- [ ] T004 Add project dependency/config baseline for Python foundation metadata handling in pyproject.toml and .gitignore (Files: pyproject.toml, .gitignore; AC: includes Python 3.11+, pydantic, PyYAML, pytest, and ignores generated runtime artifacts where appropriate).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define shared contracts and validation rules required before user-story artifact authoring.

- [ ] T005 Define shared provenance/readiness enum and core metadata schemas in src/models/readiness_models.py and src/models/registry_models.py (Files: src/models/readiness_models.py, src/models/registry_models.py; AC: enum exactly matches four canonical statuses and base models align with data-model.md).
- [ ] T006 [P] Implement canonical path validator scaffolding and strict path normalization rules in src/validators/path_validator.py (Files: src/validators/path_validator.py; AC: validator checks required paths against canonical inventory and reports missing/invalid paths deterministically).
- [ ] T007 [P] Implement dataset readiness validator scaffolding for existence/parseability/schema-semantic mismatch flags in src/validators/readiness_validator.py (Files: src/validators/readiness_validator.py; AC: validator emits readiness status + mismatch categories without altering canonical semantics).
- [ ] T008 Create foundation CLI orchestration skeleton for validation entrypoints in src/cli/foundation.py (Files: src/cli/foundation.py; AC: CLI commands route to path/readiness validators and only produce foundational metadata outputs).
- [ ] T009 Define artifact contract documentation for all foundational source-of-truth assets in contracts/artifact_contracts.md (Files: contracts/artifact_contracts.md; AC: required keys and enum usage are fully specified for canonical_paths, dataset_readiness, interface_registry, schema_ownership_map, requirement_traceability, and architecture source).

**Checkpoint**: Foundation code/contracts in place; user-story artifact authoring can proceed.

---

## Phase 3: User Story 1 - Canonical Platform Surface (Priority: P1) 🎯 MVP

**Goal**: Provide stable canonical project surfaces and governed dataset baseline for all later features.

**Independent Test**: Reviewer can locate canonical repository structure, canonical output datasets, and path/readiness baseline artifacts without rediscovery.

- [ ] T010 [US1] Author canonical path inventory with required root targets and output dataset paths in contracts/canonical_paths.yaml (Files: contracts/canonical_paths.yaml; AC: includes all authoritative paths from plan with path_type, required flag, owner_team, and status fields).
- [ ] T011 [P] [US1] Register canonical dataset surface entries for six governed outputs in contracts/dataset_readiness.json (Files: contracts/dataset_readiness.json; AC: contains dataset_id, canonical_path, schema_name, producer_system, consumer_systems, readiness_status, mismatch_refs for all six datasets).
- [ ] T012 [US1] Seed readiness validation output index from current repository evidence in validation_reports/readiness_index.json (Files: validation_reports/readiness_index.json; AC: each governed dataset has readiness entry with one allowed status and evidence notes).
- [ ] T013 [US1] Seed mismatch/violation index capturing current actual-vs-canonical gaps in violation_log/mismatch_index.json (Files: violation_log/mismatch_index.json; AC: mismatches are explicit, canonical target remains unchanged, and resolution_type is migration/normalization/both).
- [ ] T014 [US1] Update root README guidance for platform foundation artifacts and canonical path policy in README.md (Files: README.md; AC: README documents where each foundational artifact lives and states that later features must consume, not redefine, these assets).

**Checkpoint**: Canonical project surface is defined and reviewable as MVP foundation.

---

## Phase 4: User Story 2 - Governed Interface and Data Flow Model (Priority: P2)

**Goal**: Define authoritative inter-system interfaces, ownership boundaries, and reusable architecture flow source.

**Independent Test**: Reviewer can trace every interface arrow to producer/consumer ownership and view governed flow in architecture source.

- [ ] T015 [US2] Create versioned inter-system interface registry aligned to required contract arrows in contracts/interface_registry.yaml (Files: contracts/interface_registry.yaml; AC: every interface has interface_id, version, source_system, target_system, dataset_refs, ownership_ref, status).
- [ ] T016 [P] [US2] Create schema ownership map for producer/consumer accountability and blast-radius context in contracts/schema_ownership_map.yaml (Files: contracts/schema_ownership_map.yaml; AC: each schema ownership record includes producer_owner, consumer_owners, migration_required, blast_radius_notes, and status).
- [ ] T017 [US2] Author reusable Mermaid data flow architecture source covering six datasets and interface links in contracts/data_flow_architecture.mmd (Files: contracts/data_flow_architecture.mmd; AC: diagram includes all governed datasets, interface transitions, and ownership/readiness dependency edges).
- [ ] T018 [US2] Document architecture artifact maintenance and versioning rules in contracts/architecture.md (Files: contracts/architecture.md; AC: defines update workflow, versioning conventions, and consistency checks against interface and ownership registries).
- [ ] T019 [US2] Initialize schema snapshot index baseline for future schema evolution features in schema_snapshots/index.json (Files: schema_snapshots/index.json; AC: index references governed datasets/interfaces and clearly indicates baseline-only state without implementing diffing).

**Checkpoint**: Interface and architecture boundaries are stable and consumable by downstream capabilities.

---

## Phase 5: User Story 3 - Readiness, Gaps, and Traceability Baseline (Priority: P3)

**Goal**: Capture schema realities, migration needs, and requirement-to-artifact traceability for downstream feature planning.

**Independent Test**: Reviewer can verify requirement coverage, mismatch documentation, migration intent, and dataset readiness statuses from foundation artifacts alone.

- [ ] T020 [US3] Build platform requirement traceability map linking FR/SC items to concrete artifacts in contracts/requirement_traceability.yaml (Files: contracts/requirement_traceability.yaml; AC: each requirement entry has artifact_paths, coverage_type, status; no orphaned high-priority requirements).
- [ ] T021 [US3] Author foundational domain and schema notes linked to datasets/interfaces and mismatch records in DOMAIN_NOTES.md (Files: DOMAIN_NOTES.md; AC: includes actual-vs-canonical differences, migration/normalization requirements, semantic risk notes, and references to readiness/mismatch artifacts).
- [ ] T022 [P] [US3] Produce foundation report scaffold summarizing readiness posture and unresolved gaps in enforcer_report/foundation_report.md (Files: enforcer_report/foundation_report.md; AC: summarizes status counts and open blockers without implementing operational reporting engine behavior).
- [ ] T023 [US3] Backfill statuses across all foundational artifacts to enforce controlled enum consistency in contracts/canonical_paths.yaml, contracts/dataset_readiness.json, contracts/interface_registry.yaml, contracts/schema_ownership_map.yaml, contracts/requirement_traceability.yaml, validation_reports/readiness_index.json, violation_log/mismatch_index.json (Files: listed artifact files; AC: every record has exactly one allowed status and zero ad hoc labels).

**Checkpoint**: Readiness, gaps, and traceability baseline is complete and independently reviewable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency validation and documentation hardening for handoff to later features.

- [ ] T024 [P] Add artifact schema/examples and maintenance notes to specs feature contracts doc in specs/001-platform-data-surface/contracts/artifact-contracts.md (Files: specs/001-platform-data-surface/contracts/artifact-contracts.md; AC: examples reflect final artifact keys/status enum and align with repository artifacts).
- [ ] T025 Run foundation quickstart validation walkthrough and update any stale instructions in specs/001-platform-data-surface/quickstart.md (Files: specs/001-platform-data-surface/quickstart.md; AC: all steps reflect actual file names/paths created by this feature).
- [ ] T026 Produce final structure-and-constraints handoff note clarifying deferred capabilities in specs/001-platform-data-surface/research.md and specs/001-platform-data-surface/plan.md (Files: specs/001-platform-data-surface/research.md, specs/001-platform-data-surface/plan.md; AC: explicitly states Feature 1 does not implement contract execution, violation attribution, schema diffing, AI drift analysis, or operational report generation).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: starts immediately.
- **Phase 2 (Foundational)**: depends on Phase 1 completion.
- **Phase 3 (US1)**: depends on Phase 2 completion.
- **Phase 4 (US2)**: depends on Phase 3 for canonical dataset ids/paths.
- **Phase 5 (US3)**: depends on US1 + US2 artifacts.
- **Phase 6 (Polish)**: depends on all user stories.

### User Story Dependencies

- **US1 (P1)**: foundational MVP, no dependency on later stories.
- **US2 (P2)**: depends on canonical dataset/path definitions from US1.
- **US3 (P3)**: depends on both US1 and US2 artifacts for traceability completeness.

### Within Each User Story

- Define machine-readable artifact structure first.
- Populate records second.
- Emit validation/mismatch/readiness outputs third.
- Update human guidance docs last.

### Parallel Opportunities

- T002, T003, T006, T007 can run in parallel after T001.
- T011 can run in parallel with T010 once model contracts are stable.
- T016 can run in parallel with T015.
- T022 can run in parallel with T020/T021.
- T024 and T025 can run in parallel during polish.

---

## Parallel Example: User Story 2

- Task: "T015 Create versioned inter-system interface registry in contracts/interface_registry.yaml"
- Task: "T016 Create schema ownership map in contracts/schema_ownership_map.yaml"

---

## Implementation Strategy

### MVP First (US1 only)

1. Complete Setup and Foundational phases.
2. Deliver US1 canonical path/dataset/readiness/mismatch artifacts.
3. Validate that future teams can consume canonical surface without rediscovery.

### Incremental Delivery

1. Add US2 interface + ownership + architecture source.
2. Add US3 traceability + domain/schema notes + status normalization.
3. Finish with polish and handoff documentation.

### Guardrails

- Do not implement deferred runtime capabilities (`contracts/generator.py`, `contracts/runner.py`, `contracts/attributor.py`, `contracts/schema_analyzer.py`, `contracts/ai_extensions.py`, `contracts/report_generator.py`).
- Preserve canonical file names/paths as immutable targets in this feature.
- Record all upstream divergence explicitly; do not rewrite business meaning silently.

---

## Notes

- Each task is intentionally small and reviewable.
- Each task produces durable artifacts or validated structure components.
- Acceptance criteria are embedded in every task line.
