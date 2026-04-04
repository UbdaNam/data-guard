# Tasks: Operational Report Generation

**Input**: Design documents from `/specs/007-operational-report-generation/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Explicit test tasks are not required by the feature spec; each task includes acceptance criteria and execution checks.

**Organization**: Tasks are grouped by user story for independent implementation and validation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable (different files, no dependency on incomplete tasks)
- **[Story]**: User story mapping label (`[US1]`, `[US2]`, `[US3]`)
- Every task includes expected file paths and acceptance criteria.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish Feature 7 scaffolding and canonical artifact contracts.

- [x] T001 Create Feature 7 reporting package scaffold in src/reporting/**init**.py and src/reporting/pipeline.py; Acceptance: package imports cleanly and pipeline module exposes a callable orchestration entrypoint signature.
- [x] T002 Create operational report artifact contract doc in specs/007-operational-report-generation/contracts/operational-report-artifacts.md; Acceptance: contract documents required output files, required key order, and required markdown section order aligned to FR-037/FR-038.
- [x] T003 [P] Add Feature 7 package export note in src/**init**.py; Acceptance: repository import path remains stable and no existing feature exports are removed.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared domain infrastructure required by all user stories.

**⚠️ CRITICAL**: Complete this phase before starting user-story tasks.

- [x] T004 Implement typed report domain models in src/reporting/models.py; Acceptance: models cover ReportingWindow, EvidenceReference, SectionCompleteness, DataHealthScore, ViolationsSummary, SchemaChangesSummary, AiRiskSummary, RecommendedAction, and OperationalReportData.
- [x] T005 [P] Implement canonical environment configuration parser in src/reporting/env_config.py; Acceptance: parser reads only OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL and returns deterministic "missing_config" status without raising when optional values are absent.
- [x] T006 [P] Implement section completeness helpers in src/reporting/completeness.py; Acceptance: helpers produce complete/partial/insufficient_evidence states with explicit missing_sources paths and reason text.
- [x] T007 Implement report JSON serializer with deterministic key order in src/reporting/json_renderer.py; Acceptance: output order exactly matches FR-037 and nested collections honor deterministic ordering utilities.
- [x] T008 Implement report markdown section template in src/reporting/markdown_renderer.py; Acceptance: markdown renders fixed section order from FR-038 even when one or more sections are insufficient_evidence.
- [x] T009 Create CLI scaffold in contracts/report_generator.py; Acceptance: CLI parses report window and enrichment flags, delegates to src/reporting/pipeline.py, and does not implement validation/attribution/schema-evolution/AI-metric generation logic.

**Checkpoint**: Foundation ready; user-story implementation can begin.

---

## Phase 3: User Story 1 - Unified Operational Health Summary (Priority: P1) 🎯 MVP

**Goal**: Generate machine-readable report data from upstream evidence with deterministic scoring and ranking.

**Independent Test**: Run `python -m contracts.report_generator` and verify `enforcer_report/report_data.json` contains required keys, Data Health Score semantics, top violations, schema summary, AI risk summary, recommended actions, and evidence index.

### Implementation for User Story 1

- [x] T010 [US1] Implement upstream artifact loading and normalization in src/reporting/artifact_loader.py; Acceptance: loader ingests validation_reports/\*.json, violation_log/violations.jsonl, schema evolution outputs, validation_reports/ai_metrics.json, and Feature 1 metadata with per-source completeness metadata.
- [x] T011 [P] [US1] Implement deterministic reporting window resolver in src/reporting/window_resolver.py; Acceptance: explicit start/end bounds are honored and fallback latest_available mode resolves a stable window using normalized timestamps plus tie-breakers.
- [x] T012 [P] [US1] Implement exact FR-032/FR-033 Data Health Score calculator in src/reporting/health_score.py; Acceptance: formula terms, clamping, one-decimal rounding, and null/insufficient_evidence behavior match spec.
- [x] T013 [P] [US1] Implement top violation ranking utilities in src/reporting/ranking.py; Acceptance: ranking order is severity > recurrence > latest occurrence > stable violation_id and is reproducible across repeated runs.
- [x] T014 [US1] Implement schema change summary builder in src/reporting/ranking.py; Acceptance: builder filters by resolved reporting window and prioritizes breaking/high-impact changes deterministically.
- [x] T015 [P] [US1] Implement AI risk summary builder in src/reporting/report_builder.py; Acceptance: summary reads Feature 6 metrics, includes trend/completeness markers, and marks insufficient_evidence when history is missing.
- [x] T016 [US1] Implement evidence-grounded recommended action generator in src/reporting/action_generator.py; Acceptance: actions consolidate by issue_type+affected_surface+field_or_interface and include remediation target, affected location, owner context, verification step, and evidence references.
- [x] T017 [US1] Implement report data assembly in src/reporting/report_builder.py; Acceptance: assembled OperationalReportData includes all required sections and machine-readable evidence references for every claim/action.
- [x] T018 [US1] Implement machine-readable report writer in src/reporting/pipeline.py and src/reporting/json_renderer.py; Acceptance: writes enforcer_report/report_data.json atomically with required deterministic structure and section_completeness.

**Checkpoint**: US1 produces complete machine-readable report output independently.

---

## Phase 4: User Story 2 - Evidence-Backed Risk and Change Narrative (Priority: P2)

**Goal**: Produce clear markdown narrative aligned to structured evidence and canonical section contracts.

**Independent Test**: Run report generation with known violations/schema changes and verify markdown clearly communicates top risks/actions while each claim maps to evidence entries in report_data.json.

### Implementation for User Story 2

- [x] T019 [US2] Implement markdown narrative rendering from structured report data in src/reporting/markdown*renderer.py; Acceptance: output file enforcer_report/report*{date}.md includes fixed section order and deterministic issue/action list ordering.
- [x] T020 [P] [US2] Add evidence-traceability notes rendering in src/reporting/markdown_renderer.py; Acceptance: markdown includes an evidence traceability section with references to artifact_path and record_selector entries.
- [x] T021 [US2] Integrate markdown generation into pipeline in src/reporting/pipeline.py; Acceptance: each successful run writes both enforcer*report/report_data.json and enforcer_report/report*{date}.md.
- [x] T022 [US2] Add canonical path and responsibility-boundary guards in src/reporting/pipeline.py and contracts/report_generator.py; Acceptance: runtime clearly enforces read-only upstream artifact usage and does not execute upstream validation, attribution, schema evolution, or AI metric generation logic.

**Checkpoint**: US2 produces stakeholder-facing markdown that remains evidence-grounded and boundary-safe.

---

## Phase 5: User Story 3 - Deterministic and Resilient Reporting (Priority: P3)

**Goal**: Ensure optional OpenRouter enrichment is safe, optional, and non-blocking with deterministic fallback.

**Independent Test**: Run with no OpenRouter env vars and with simulated OpenRouter failures; verify generation succeeds with fallback narrative and deterministic outputs.

### Implementation for User Story 3

- [x] T023 [US3] Implement OpenRouter-only optional enrichment client in src/reporting/llm_enrichment.py; Acceptance: client uses only OPENROUTER_API_KEY/OPENROUTER_BASE_URL/OPENROUTER_MODEL and refuses non-OpenRouter providers.
- [x] T024 [P] [US3] Implement deterministic non-LLM fallback narrative builder in src/reporting/llm_enrichment.py and src/reporting/markdown_renderer.py; Acceptance: fallback is used when enrichment disabled/missing_config/failed and output remains complete.
- [x] T025 [US3] Implement enrichment safety post-validation in src/reporting/llm_enrichment.py; Acceptance: enriched text cannot introduce unsupported incidents/actions and falls back automatically on evidence-grounding violations.
- [x] T026 [US3] Integrate enrichment flow into pipeline and CLI flags in src/reporting/pipeline.py and contracts/report_generator.py; Acceptance: enrichment is optional-only and never required for successful report generation.
- [x] T027 [US3] Implement graceful degradation for missing upstream artifact families in src/reporting/artifact_loader.py and src/reporting/completeness.py; Acceptance: report generation continues with required sections present and explicit insufficient_evidence + missing_sources references.

**Checkpoint**: US3 guarantees resilient deterministic behavior with optional enrichment only.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and operational readiness updates across stories.

- [x] T028 [P] Create or update .env.example in .env.example; Acceptance: file documents OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL and marks enrichment as optional.
- [x] T029 [P] Update report generation usage docs in README.md; Acceptance: README includes CLI usage, expected input artifacts, output paths, optional enrichment behavior, and deterministic fallback note.
- [x] T030 Run quickstart validation updates in specs/007-operational-report-generation/quickstart.md; Acceptance: quickstart commands and expected outputs match implemented CLI behavior and canonical artifact paths.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: starts immediately.
- **Phase 2 (Foundational)**: depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: depends on Phase 2.
- **Phase 4 (US2)**: depends on Phase 2 and integrates US1 structured output.
- **Phase 5 (US3)**: depends on Phase 2 and integrates US2 markdown pipeline.
- **Phase 6 (Polish)**: depends on completion of desired user stories.

### User Story Dependencies

- **US1 (P1)**: no dependency on other user stories once foundational work is complete.
- **US2 (P2)**: depends on US1 `OperationalReportData` output schema for markdown rendering.
- **US3 (P3)**: depends on US2 markdown pipeline integration and shared foundational modules.

### Dependency Graph

- `US1 -> US2 -> US3`
- Foundational tasks `T004-T009` must complete before `T010+`.

---

## Parallel Execution Examples

### User Story 1

- Parallel set A: `T011`, `T012`, `T013`, `T015`
- Then continue with dependent tasks: `T014 -> T016 -> T017 -> T018`

### User Story 2

- Parallel set A: `T020` while `T019` is in progress if renderer sections are split by function.
- Then continue with dependent tasks: `T019 -> T021 -> T022`

### User Story 3

- Parallel set A: `T024` can run after `T023` interface contract is defined.
- Then continue with dependent tasks: `T023 -> T025 -> T026`, with `T027` in parallel after loader/completeness interfaces stabilize.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete US1 tasks (`T010-T018`).
3. Validate machine-readable report generation and deterministic ranking/score behavior.
4. Demo/deploy MVP capability.

### Incremental Delivery

1. Deliver US1 machine-readable operational reporting.
2. Add US2 markdown narrative and evidence traceability rendering.
3. Add US3 optional OpenRouter enrichment with deterministic fallback and resilience.
4. Finish polish tasks (`T028-T030`).

### Task Completeness Validation

- Every user story has independent test criteria and a complete implementation slice.
- All requested capabilities from the prompt are covered by explicit tasks.
- Tasks preserve canonical paths and metadata contracts from Features 1–6.
- No task includes implementation of upstream validation, attribution, schema evolution, or AI metric generation logic.
