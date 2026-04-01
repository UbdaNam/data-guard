# Tasks: Validation Execution and Drift Detection Engine

**Input**: Design documents from specs/003-validation-drift-engine/
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: No test-first tasks are included because the specification and request do not require a TDD workflow.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on incomplete tasks)
- **[Story]**: User story label (`[US1]`, `[US2]`, `[US3]`) for story-phase tasks only
- Every task includes expected files and acceptance criteria inline.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize validation-engine scaffolding and canonical CLI wiring.

- [ ] T001 Create Feature 3 module scaffolding in src/validation/**init**.py, src/models/validation_models.py, and src/validators/validation_report_validator.py (Files: src/validation/**init**.py, src/models/validation_models.py, src/validators/validation_report_validator.py; AC: modules import cleanly and expose typed placeholders for runner orchestration).
- [ ] T002 [P] Add validation-engine operational dependency declarations in pyproject.toml (Files: pyproject.toml; AC: dependencies cover YAML parsing and typed models used by Feature 3 without introducing non-required frameworks).
- [ ] T003 Add runner CLI scaffold at contracts/runner.py with argument parsing for contract selection and baseline refresh mode (Files: contracts/runner.py; AC: command executes and prints structured run summary even before full check logic is added).
- [ ] T004 [P] Add Feature 3 CLI dispatch option in src/cli/foundation.py for validation execution (Files: src/cli/foundation.py; AC: foundation CLI can invoke contracts/runner.py entrypoint).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared primitives required by all user stories.

**⚠️ CRITICAL**: No user story work starts until this phase is complete.

- [ ] T005 Implement typed data models for ExecutableCheck, ValidationResult, ValidationReport, BaselineStatistic, and ValidationRun in src/models/validation_models.py (Files: src/models/validation_models.py; AC: model fields exactly match spec-required schema and status enums).
- [ ] T006 [P] Implement contract YAML loader and clause-to-check normalization in src/validation/contract_loader.py (Files: src/validation/contract_loader.py; AC: generated_contracts/\*.yaml are parsed into deterministic ExecutableCheck collections with scope classification).
- [ ] T007 [P] Implement streaming JSONL snapshot loader with canonical ordering and malformed-line capture in src/validation/dataset_loader.py (Files: src/validation/dataset_loader.py; AC: loader yields deterministic record order, tracks malformed lines, and does not crash on bad lines).
- [ ] T008 Implement check-engine orchestration skeleton with per-field/per-record/dataset dispatch and fail-safe wrapper in src/validation/check_engine.py (Files: src/validation/check_engine.py; AC: dispatch executes check handlers and converts handler exceptions into ERROR result rows without halting run).
- [ ] T009 [P] Implement baseline storage repository for schema_snapshots/baselines.json in src/validation/baseline_store.py (Files: src/validation/baseline_store.py; AC: supports read/initialize/update-with-explicit-refresh and preserves immutable default behavior).
- [ ] T010 [P] Implement result aggregation primitives in src/validation/result_aggregator.py (Files: src/validation/result_aggregator.py; AC: totals reconcile as total_checks = passed + failed + warned + errored).
- [ ] T011 [P] Implement fixed-schema report validator in src/validators/validation_report_validator.py (Files: src/validators/validation_report_validator.py; AC: validator enforces required top-level and per-result fields).

**Checkpoint**: Foundation ready for story implementation.

---

## Phase 3: User Story 1 - Execute Contract Validation Runs (Priority: P1) 🎯 MVP

**Goal**: Execute structural, semantic, and dataset-level validations and always emit complete result rows.

**Independent Test**: Run runner on week3/week5 contracts and verify complete report output with PASS/FAIL/WARN/ERROR statuses and no run halt on partial failures.

### Implementation for User Story 1

- [ ] T012 [US1] Implement structural field checks (`type`, `required`, `nullability`, `pattern`) in src/validation/check_engine.py (Files: src/validation/check_engine.py; AC: missing columns => ERROR, invalid types => FAIL, and structural-shape errors => ERROR).
- [ ] T013 [US1] Implement semantic field checks (`range`, `enum`, `relationship`) in src/validation/check_engine.py (Files: src/validation/check_engine.py; AC: semantic violations are classified deterministically and include expected vs actual diagnostics).
- [ ] T014 [US1] Implement dataset-level checks (`row_count`, `uniqueness`, `referential_integrity`) in src/validation/check_engine.py (Files: src/validation/check_engine.py; AC: dataset checks produce one result entry per attempted check with records_failing and message fields).
- [ ] T015 [US1] Implement nested path resolution strategy (object schema-walk + array wildcard iteration) in src/validation/dataset_loader.py and src/validation/check_engine.py (Files: src/validation/dataset_loader.py, src/validation/check_engine.py; AC: paths like items[*].price resolve deterministically across records/indices).
- [ ] T016 [US1] Implement error-handling and partial-execution policy in src/validation/check_engine.py and src/validation/result_aggregator.py (Files: src/validation/check_engine.py, src/validation/result_aggregator.py; AC: runner never halts full run due to bad data and all attempted checks emit result entries).
- [ ] T017 [US1] Wire US1 end-to-end in contracts/runner.py using loader + engine + aggregator interfaces (Files: contracts/runner.py; AC: runner executes per contract and returns structured summary for generated, failed, and errored checks).

**Checkpoint**: US1 independently complete and reviewable.

---

## Phase 4: User Story 2 - Detect Statistical Drift (Priority: P2)

**Goal**: Profile numeric fields, initialize immutable baselines on first successful run, and classify drift with z-score thresholds.

**Independent Test**: First run creates baselines; second run with shifted numeric values emits WARN for >2 stddev and FAIL for >3 stddev.

### Implementation for User Story 2

- [ ] T018 [US2] Implement numeric statistical profiling (`mean`, `stddev`, `min`, `max`, sample size) in src/validation/statistical_profiler.py (Files: src/validation/statistical_profiler.py; AC: profiler returns deterministic numeric summaries for drift-eligible fields only).
- [ ] T019 [US2] Implement drift detection logic with z-score computation and threshold classification in src/validation/drift_detector.py (Files: src/validation/drift_detector.py; AC: WARN when deviation >2 and FAIL when deviation >3, applied only to numeric fields).
- [ ] T020 [US2] Integrate baseline initialization and immutable-default update policy in src/validation/baseline_store.py and src/validation/drift_detector.py (Files: src/validation/baseline_store.py, src/validation/drift_detector.py; AC: first successful numeric run writes baseline and normal runs do not overwrite unless explicit refresh mode).
- [ ] T021 [US2] Add drift check synthesis from executable checks and profiler outputs in src/validation/contract_loader.py and src/validation/check_engine.py (Files: src/validation/contract_loader.py, src/validation/check_engine.py; AC: drift checks are generated only for numeric fields and emitted as result rows).
- [ ] T022 [US2] Wire baseline read/write and drift execution flow in contracts/runner.py (Files: contracts/runner.py; AC: runner reads baselines, executes drift checks, and persists baseline changes per policy).

**Checkpoint**: US2 independently complete and reviewable.

---

## Phase 5: User Story 3 - Produce Downstream-Ready Validation Artifacts (Priority: P3)

**Goal**: Emit strict fixed-schema reports with deterministic ordering/sampling for downstream features.

**Independent Test**: Re-run unchanged inputs and verify byte-stable report payload except report_id and run_timestamp.

### Implementation for User Story 3

- [ ] T023 [US3] Implement deterministic check and result ordering strategy in src/validation/result_aggregator.py (Files: src/validation/result_aggregator.py; AC: ordering key `(column_name, check_type, check_id)` is applied consistently across runs).
- [ ] T024 [US3] Implement deterministic sample_failing selection (first N failing records in canonical order) in src/validation/check_engine.py (Files: src/validation/check_engine.py; AC: sample_failing values are stable for unchanged inputs).
- [ ] T025 [US3] Implement validation report writer with fixed top-level schema and required per-result fields in src/validation/report*writer.py (Files: src/validation/report_writer.py; AC: output JSON exactly matches required schema and filename pattern validation_reports/{contract_id}*{timestamp}.json).
- [ ] T026 [US3] Integrate report schema validation before write in src/validation/report_writer.py and src/validators/validation_report_validator.py (Files: src/validation/report_writer.py, src/validators/validation_report_validator.py; AC: report write fails safe to runner summary if schema invalid and records clear error diagnostics).
- [ ] T027 [US3] Wire final report generation pipeline in contracts/runner.py using aggregator + writer modules (Files: contracts/runner.py; AC: one report per processed contract is always produced for attempted execution scope).
- [ ] T028 [US3] Ensure out-of-scope guardrails in runner and docs (no attribution, schema evolution diffing, AI extension logic, or report-generation feature logic) in contracts/runner.py and specs/003-validation-drift-engine/quickstart.md (Files: contracts/runner.py, specs/003-validation-drift-engine/quickstart.md; AC: execution behavior is validation-only and boundary is explicitly documented).

**Checkpoint**: US3 independently complete and reviewable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete operational guidance and final integration hardening.

- [ ] T029 Update Feature 3 usage documentation in README.md (Files: README.md; AC: includes runner invocation, required inputs, baseline behavior, deterministic guarantees, and fixed report schema summary).
- [ ] T030 [P] Update quickstart validation steps with final command and output verification details in specs/003-validation-drift-engine/quickstart.md (Files: specs/003-validation-drift-engine/quickstart.md; AC: quickstart reflects actual runner workflow and expected artifacts).
- [ ] T031 [P] Finalize validation artifact interface documentation in specs/003-validation-drift-engine/contracts/validation-artifacts.md (Files: specs/003-validation-drift-engine/contracts/validation-artifacts.md; AC: docs match implemented check mapping, drift policy, error classification, and determinism contract).
- [ ] T032 Run full end-to-end validation pass and capture completion evidence in specs/003-validation-drift-engine/plan.md (Files: specs/003-validation-drift-engine/plan.md; AC: plan records execution evidence for generated reports and baseline behavior without introducing out-of-scope capabilities).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Story phases (Phase 3–5)**: Depend on Foundational completion; then can proceed in priority order or parallel if staffed.
- **Polish (Phase 6)**: Depends on completion of desired user stories.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; no dependency on US2/US3.
- **US2 (P2)**: Starts after Phase 2; integrates with US1 execution surfaces but remains independently testable.
- **US3 (P3)**: Starts after Phase 2; uses results from US1/US2 while remaining independently testable for deterministic artifact behavior.

### Within Each User Story

- Data/path resolution before check execution.
- Check execution before aggregation.
- Aggregation before report writing.
- Report writing before doc finalization.

### Parallel Opportunities

- Phase 1 tasks marked [P]: T002, T004.
- Phase 2 tasks marked [P]: T006, T007, T009, T010, T011.
- US1 parallel opportunities are limited by shared file dependencies in check engine.
- US2 can run T018 and portions of T020 in parallel with careful file coordination.
- US3 can run T023 and T025 in parallel before final runner wiring.

---

## Parallel Example: User Story 2

- Task: T018 [US2] Implement statistical profiling in src/validation/statistical_profiler.py
- Task: T019 [US2] Implement drift detection in src/validation/drift_detector.py

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate that runner produces complete validation reports with structural/semantic/dataset checks.
4. Demo MVP enforcement capability.

### Incremental Delivery

1. Foundation complete.
2. Deliver US1 (contract execution + robustness).
3. Deliver US2 (drift + baselines).
4. Deliver US3 (deterministic downstream-ready artifacts).
5. Polish docs and execution evidence.

### Parallel Team Strategy

1. Team aligns on Phase 1 and Phase 2 shared contracts.
2. Then split:
   - Engineer A: check execution depth (US1)
   - Engineer B: profiling/drift/baselines (US2)
   - Engineer C: reporting/determinism/docs (US3)

---

## Notes

- [P] tasks indicate non-blocking parallel opportunities when file overlap is avoided.
- Tasks intentionally exclude violation attribution, schema evolution diffing, AI extensions, and report-generation feature logic.
- Operational artifacts must come from real execution or explicitly injected test data only.
