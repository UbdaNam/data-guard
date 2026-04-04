# Tasks: AI Contract Enforcement Extensions

**Input**: Design documents from `specs/006-ai-contract-enforcement/`
**Prerequisites**: [plan.md](specs/006-ai-contract-enforcement/plan.md), [spec.md](specs/006-ai-contract-enforcement/spec.md), [research.md](specs/006-ai-contract-enforcement/research.md), [data-model.md](specs/006-ai-contract-enforcement/data-model.md), [contracts/ai-enforcement-artifacts.md](specs/006-ai-contract-enforcement/contracts/ai-enforcement-artifacts.md)

**Tests**: Not mandated as TDD in the feature spec; implementation tasks include executable acceptance criteria and quickstart verification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish Feature 6 module scaffolding and canonical AI artifact roots.

- [ ] T001 Create Feature 6 package scaffold in src/ai_enforcement/**init**.py and src/ai_enforcement/pipeline.py; Files: src/ai_enforcement/**init**.py, src/ai_enforcement/pipeline.py; AC: package imports without runtime errors and pipeline exposes a callable orchestration function.
- [ ] T002 Create typed model scaffold for AI entities in src/models/ai_enforcement_models.py and export in src/models/**init**.py; Files: src/models/ai_enforcement_models.py, src/models/**init**.py; AC: models compile with `pydantic` and include run, quarantine, violation, drift, and metrics envelopes.
- [ ] T003 [P] Create validator scaffold for AI artifact payloads in src/validators/ai_enforcement_validator.py and export in src/validators/**init**.py; Files: src/validators/ai_enforcement_validator.py, src/validators/**init**.py; AC: validator module loads and provides validation entrypoints for metrics, violations, quarantine, and drift artifacts.
- [ ] T004 [P] Add canonical output root initialization helpers in src/ai_enforcement/renderer.py; Files: src/ai_enforcement/renderer.py; AC: helper ensures `validation_reports/`, `violation_log/`, `outputs/quarantine/`, and `schema_snapshots/ai/` exist using deterministic `pathlib` logic.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement cross-story infrastructure that blocks all user stories until complete.

**⚠️ CRITICAL**: No user story work begins before this phase is done.

- [ ] T005 Implement Feature 1/2/3/5 artifact ingestion layer in src/ai_enforcement/contract_loader.py; Files: src/ai_enforcement/contract_loader.py; AC: loader resolves canonical metadata and schema artifacts from `contracts/`, `generated_contracts/`, and optional Feature 5 outputs without redefining upstream contracts.
- [ ] T006 Implement deterministic run metadata and ID utilities in src/ai_enforcement/renderer.py; Files: src/ai_enforcement/renderer.py; AC: run timestamp format is UTC `YYYYMMDDTHHMMSSZ`, run IDs are stable-format UUID/hash strings, and artifact ordering keys are centralized.
- [ ] T007 Implement CLI scaffold and argument parsing in contracts/ai_extensions.py; Files: contracts/ai_extensions.py; AC: CLI accepts canonical defaults, supports path overrides, validates required `--surface-id` for drift mode, and invokes pipeline without using general runner/attributor/schema analyzer/report generator.
- [ ] T008 Implement pipeline wiring for staged execution and boundary guards in src/ai_enforcement/pipeline.py; Files: src/ai_enforcement/pipeline.py; AC: pipeline stages are prompt/output/trace/drift/aggregate, boundary guard rejects non-AI runner replacement behavior, and context completeness flags are emitted.

**Checkpoint**: Foundation complete; user stories can now proceed.

---

## Phase 3: User Story 1 - Govern Prompt and Output Schemas (Priority: P1) 🎯 MVP

**Goal**: Validate governed prompt inputs and structured outputs, quarantine invalid prompts, and compute output violation rates.

**Independent Test**: Running the CLI on Week 3 + Week 2 inputs classifies every prompt record as valid/quarantined, records output conformance outcomes, and emits rate-ready counters.

### Implementation for User Story 1

- [ ] T009 [US1] Define the first governed prompt input schema asset in generated_contracts/prompt_inputs/week3_prompt_input.schema.json; Files: generated_contracts/prompt_inputs/week3_prompt_input.schema.json; AC: schema defines required keys/version constraints for Week 3 prompt surface and is discoverable by loader.
- [ ] T010 [US1] Implement prompt input schema validator in src/ai_enforcement/prompt_validator.py; Files: src/ai_enforcement/prompt_validator.py; AC: validator returns PASS/FAIL/ERROR per record with explicit failure reasons and schema version context.
- [ ] T011 [US1] Implement quarantine writer with atomic write in src/ai*enforcement/quarantine_writer.py; Files: src/ai_enforcement/quarantine_writer.py; AC: invalid prompts write to `outputs/quarantine/{run_timestamp}*{run_id}.jsonl` in deterministic order and write failure hard-fails run when invalid records exist.
- [ ] T012 [P] [US1] Implement structured Week 2 output schema validator in src/ai_enforcement/output_validator.py; Files: src/ai_enforcement/output_validator.py; AC: validator detects missing required fields, type mismatches, nested shape violations, and unknown fields per governed schema.
- [ ] T013 [US1] Implement violation-rate metric calculator for prompt/output surfaces in src/ai_enforcement/metrics.py; Files: src/ai_enforcement/metrics.py; AC: calculator computes $rate = failures / max(processed, 1)$ by schema/prompt version and returns deterministic numeric outputs.
- [ ] T014 [US1] Integrate prompt/output validators and quarantine flow into pipeline stage orchestration; Files: src/ai_enforcement/pipeline.py, src/ai_enforcement/prompt_validator.py, src/ai_enforcement/output_validator.py, src/ai_enforcement/quarantine_writer.py; AC: processed prompt count equals valid+quarantined and output conformance results are captured for downstream violation writing.

**Checkpoint**: User Story 1 independently functional.

---

## Phase 4: User Story 2 - Govern Trace and Embedding Drift Signals (Priority: P2)

**Goal**: Validate trace contracts and produce deterministic embedding baseline/comparison drift outcomes.

**Independent Test**: Running the CLI on trace + drift surface produces trace validation outcomes and either baseline creation or comparison outcomes with explicit statuses.

### Implementation for User Story 2

- [ ] T015 [US2] Implement LangSmith trace contract validator in src/ai_enforcement/trace_validator.py; Files: src/ai_enforcement/trace_validator.py; AC: validator flags missing run IDs/malformed timestamps/contract field violations and returns machine-readable PASS/FAIL/ERROR records.
- [ ] T016 [P] [US2] Implement embedding sample selector in src/ai_enforcement/drift.py; Files: src/ai_enforcement/drift.py; AC: selector deterministically extracts governed text samples for `surface_id` with explicit insufficient-data signaling.
- [ ] T017 [US2] Implement baseline writer/loader under schema_snapshots strategy in src/ai_enforcement/drift.py; Files: src/ai_enforcement/drift.py; AC: baseline persists to `schema_snapshots/ai/{surface_id}/baseline_token_hash_v1.json`, includes algorithm/version metadata, and loader handles missing/unreadable baseline statuses.
- [ ] T018 [US2] Implement deterministic drift calculator in src/ai_enforcement/drift.py; Files: src/ai_enforcement/drift.py; AC: calculator computes signature vector and cosine distance with fixed preprocessing/dimensions and emits `baseline_created|compared|insufficient_data|baseline_unreadable` statuses.
- [ ] T019 [US2] Integrate trace and drift stages into pipeline with graceful degradation flags; Files: src/ai_enforcement/pipeline.py, src/ai_enforcement/trace_validator.py, src/ai_enforcement/drift.py; AC: absence of Feature 5 context does not fail run, trace/drift outcomes are included, and partial-context flags are explicit.

**Checkpoint**: User Story 2 independently functional.

---

## Phase 5: User Story 3 - Produce Durable AI Contract Evidence (Priority: P3)

**Goal**: Persist durable AI metrics and AI-specific violation artifacts for downstream reuse.

**Independent Test**: Full run writes metrics, violations, quarantine pointers, and drift artifact pointers in canonical locations with deterministic ordering.

### Implementation for User Story 3

- [ ] T020 [US3] Implement AI-specific violation writer in src/ai_enforcement/violation_writer.py; Files: src/ai_enforcement/violation_writer.py; AC: violations append to `violation_log/ai_violations.jsonl` with deterministic in-run order and required fields (`category`, `surface_id`, `record_ref`, `severity`, `evidence`).
- [ ] T021 [US3] Implement AI metric aggregation model assembly in src/ai_enforcement/metrics.py; Files: src/ai_enforcement/metrics.py, src/models/ai_enforcement_models.py; AC: aggregation emits totals/rates/trend/context completeness/artifact pointers matching data-model contract.
- [ ] T022 [US3] Implement trend calculation and bounded history merge in src/ai_enforcement/metrics.py; Files: src/ai_enforcement/metrics.py; AC: uses 10-run window, slope-based trend status (`insufficient_history|stable|improving|degrading`), and deterministic history merge behavior when prior metrics are missing.
- [ ] T023 [US3] Implement AI metrics output writer in src/ai_enforcement/renderer.py; Files: src/ai_enforcement/renderer.py; AC: writes `validation_reports/ai_metrics.json` via atomic replace with sorted keys and validates payload before write.
- [ ] T024 [US3] Wire violation writer and metrics writer into pipeline completion stage; Files: src/ai_enforcement/pipeline.py, src/ai_enforcement/violation_writer.py, src/ai_enforcement/renderer.py; AC: successful runs always emit metrics file, violations when applicable, and artifact paths referenced in metrics.

**Checkpoint**: User Story 3 independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final deterministic behavior checks and operator-facing usage guidance.

- [ ] T025 [P] Add deterministic ordering/reviewability guards and acceptance checks across writers; Files: src/ai_enforcement/renderer.py, src/ai_enforcement/quarantine_writer.py, src/ai_enforcement/violation_writer.py, src/ai_enforcement/drift.py; AC: unchanged inputs produce stable ordering and stable serialization for all generated artifacts.
- [ ] T026 Update README usage instructions for Feature 6 CLI and artifact semantics; Files: README.md; AC: README documents canonical inputs/outputs, boundary exclusions (no stakeholder report generation/git attribution/general schema evolution logic), and graceful degradation behavior.
- [ ] T027 Run quickstart validation and document execution-backed evidence notes; Files: specs/006-ai-contract-enforcement/quickstart.md; AC: quickstart reflects validated command flow and confirms expected artifacts in canonical paths.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: starts immediately.
- **Phase 2 (Foundational)**: depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: depends on Phase 2 completion.
- **Phase 4 (US2)**: depends on Phase 2 completion; can proceed in parallel with US1 after foundation.
- **Phase 5 (US3)**: depends on outputs from US1 and US2.
- **Phase 6 (Polish)**: depends on all user stories.

### User Story Dependencies

- **US1 (P1)**: independent MVP after foundational work.
- **US2 (P2)**: independent of US1 logic, but shares foundational loaders/models.
- **US3 (P3)**: integrates evidence from US1 and US2.

### Within-Story Ordering

- Define schema/assets before validators.
- Validators before writers.
- Writers before pipeline integration.
- Integration before polish/documentation.

## Parallel Opportunities

- Setup parallel tasks: `T003`, `T004`.
- US1 parallel task: `T012` can proceed while quarantine writer is implemented.
- US2 parallel task: `T016` can run alongside trace validator.
- Polish parallel task: `T025` can run with README updates once implementation is stable.

## Parallel Example: User Story 1

- Parallel Task A: `T011` quarantine writer in `src/ai_enforcement/quarantine_writer.py`
- Parallel Task B: `T012` output validator in `src/ai_enforcement/output_validator.py`

## Parallel Example: User Story 2

- Parallel Task A: `T015` trace validator in `src/ai_enforcement/trace_validator.py`
- Parallel Task B: `T016` embedding sample selector in `src/ai_enforcement/drift.py`

## Parallel Example: User Story 3

- Parallel Task A: `T021` metrics aggregation in `src/ai_enforcement/metrics.py`
- Parallel Task B: `T020` violation writer in `src/ai_enforcement/violation_writer.py`

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 and Phase 2.
2. Deliver US1 (prompt/output validation + quarantine + rate calculator).
3. Validate MVP independently using Week 2/Week 3 surfaces.

### Incremental Delivery

1. Add US2 (trace + drift baseline/comparison) with graceful degradation.
2. Add US3 (durable metrics/violation outputs).
3. Complete polish and documentation.

### Boundary Enforcement

- Preserve canonical metadata contracts from Features 1–5 as read-only upstream inputs.
- Do not implement final stakeholder report generation.
- Do not implement git attribution logic.
- Do not implement general schema evolution classification logic.
