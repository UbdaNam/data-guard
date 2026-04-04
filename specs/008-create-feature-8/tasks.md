# Tasks: Developer Workflow and End-to-End Runbook

**Input**: Design documents from `/specs/008-create-feature-8/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md, README.md, .env.example

**Tests**: Not required by the feature spec. This feature is documentation-first and focuses on reviewer/maintainer operability.

**Organization**: Tasks are grouped by user story and ordered so each phase produces reviewable documentation artifacts.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable (different files, no dependency on incomplete tasks)
- **[Story]**: User story mapping label (`[US1]`, `[US2]`, `[US3]`)
- Every task includes expected file paths and acceptance criteria.

## Phase 1: Setup (Shared Documentation Scaffold)

**Purpose**: Establish the documentation surfaces that the runbook will organize and link together.

- [x] T001 Create the reviewer-facing README scaffold in `README.md`; Expected files changed: `README.md`; Acceptance: the file has a concise mission statement plus top-level sections for quickstart, command order, outputs, OpenRouter, troubleshooting, and maintainer links.
- [x] T002 [P] Create the optional end-to-end runbook scaffold in `docs/runbooks/end_to_end.md`; Expected files changed: `docs/runbooks/end_to_end.md`; Acceptance: the file exists with headings for command sequence, dependency mapping, and artifact inventory.
- [x] T003 [P] Create the optional troubleshooting runbook scaffold in `docs/runbooks/troubleshooting.md`; Expected files changed: `docs/runbooks/troubleshooting.md`; Acceptance: the file exists with headings for failure cases, recovery order, and rerun guidance.
- [x] T004 [P] Update `.env.example` with placeholder-only OpenRouter variables and no secrets; Expected files changed: `.env.example`; Acceptance: the file contains only placeholder values and explanatory comments for optional enrichment settings.

---

## Phase 2: Foundational Documentation Rules

**Purpose**: Lock the shared rules that every later documentation section must follow.

- [x] T005 Document the fresh-clone setup path in `README.md`; Expected files changed: `README.md`; Acceptance: the file states Python 3.11+ and the canonical `uv sync --extra dev` setup flow, plus first-run verification guidance.
- [x] T006 Document required vs optional workflow boundaries in `README.md` and `docs/runbooks/end_to_end.md`; Expected files changed: `README.md`, `docs/runbooks/end_to_end.md`; Acceptance: the baseline required steps are clearly separated from optional OpenRouter-backed behavior and supporting documentation.
- [x] T007 Document the canonical command order and prerequisite mapping in `README.md` and `docs/runbooks/end_to_end.md`; Expected files changed: `README.md`, `docs/runbooks/end_to_end.md`; Acceptance: the documented sequence matches the real entry points in `contracts/generator.py`, `contracts/runner.py`, `contracts/attributor.py`, `contracts/schema_analyzer.py`, `contracts/ai_extensions.py`, and `contracts/report_generator.py`.
- [x] T008 Document expected output inventory by script in `README.md` and `docs/runbooks/end_to_end.md`; Expected files changed: `README.md`, `docs/runbooks/end_to_end.md`; Acceptance: each command lists the canonical repo-relative outputs already established by Features 1–7.

---

## Phase 3: User Story 1 - Fresh-Clone Setup (Priority: P1)

**Goal**: A reviewer can clone the repo, set up the environment, and identify the required configuration without reverse engineering the project.

**Independent Test**: A fresh-clone reviewer can follow `README.md` and `.env.example` to reach a ready-to-run baseline and locate the reviewer verification checklist.

- [x] T009 [US1] Add the reviewer quick-start checklist to `README.md`; Expected files changed: `README.md`; Acceptance: the checklist covers setup, configuration, first-run verification, and the canonical artifact families a reviewer should confirm.
- [x] T010 [P] [US1] Add the maintainer navigation index to `README.md`; Expected files changed: `README.md`; Acceptance: the README points to the core artifact directories (`generated_contracts/`, `validation_reports/`, `violation_log/`, `schema_snapshots/`, `outputs/`, `enforcer_report/`) without overwhelming first-time readers.
- [x] T011 [US1] Align `.env.example` and `README.md` on the no-secrets rule; Expected files changed: `.env.example`, `README.md`; Acceptance: the docs explicitly state that secrets are never committed and that placeholders-only environment values are sufficient for the baseline.

**Checkpoint**: US1 is complete when a reviewer can understand setup, configuration, and the first verification step from the README alone.

---

## Phase 4: User Story 2 - Canonical End-to-End Execution (Priority: P2)

**Goal**: The documented workflow explains the full command sequence and expected outputs across Features 1–7.

**Independent Test**: A teammate can follow the end-to-end runbook and match each command to the real output artifacts produced by the platform.

- [x] T012 [US2] Expand `docs/runbooks/end_to_end.md` with the command-by-command execution flow; Expected files changed: `docs/runbooks/end_to_end.md`; Acceptance: the runbook documents the six canonical commands, their real repo-relative inputs, and their generated outputs.
- [x] T013 [P] [US2] Add the command dependency and rerun-order table to `docs/runbooks/end_to_end.md`; Expected files changed: `docs/runbooks/end_to_end.md`; Acceptance: the table shows which outputs are prerequisites for later steps and explains rerun order from earliest missing prerequisite to latest dependent artifact.
- [x] T014 [US2] Add the reviewer-visible output summaries to `README.md`; Expected files changed: `README.md`; Acceptance: each script has a concise success signal and output inventory that is quick to verify at a glance.

**Checkpoint**: US2 is complete when the README and end-to-end runbook together explain the full operational sequence and the expected artifact inventory.

---

## Phase 5: User Story 3 - Troubleshooting and Recovery (Priority: P3)

**Goal**: The documentation helps maintainers recover from missing inputs, partial runs, and optional OpenRouter configuration gaps.

**Independent Test**: A maintainer can use the troubleshooting runbook to identify a failure mode, understand its impact, and rerun the correct earliest prerequisite first.

- [x] T015 [US3] Expand `docs/runbooks/troubleshooting.md` with the minimum recovery cases; Expected files changed: `docs/runbooks/troubleshooting.md`; Acceptance: the guide covers missing input datasets, missing generated contracts, malformed validation reports, missing lineage snapshots, missing schema snapshots, absent OpenRouter configuration, and partial feature execution.
- [x] T016 [P] [US3] Document OpenRouter configuration and deterministic fallback behavior in `README.md` and `docs/runbooks/troubleshooting.md`; Expected files changed: `README.md`, `docs/runbooks/troubleshooting.md`; Acceptance: optional enrichment is clearly described as non-blocking and the deterministic baseline is documented as the default.
- [x] T017 [US3] Add the maintainer recovery navigation guide to the optional runbooks; Expected files changed: `docs/runbooks/end_to_end.md`, `docs/runbooks/troubleshooting.md`; Acceptance: the runbooks cross-link to the canonical artifact paths and explain where to inspect failures and rerun outputs.

**Checkpoint**: US3 is complete when the troubleshooting guidance makes the recovery order unambiguous and preserves the optional nature of OpenRouter.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Ensure the documentation remains concise, aligned, and directly usable.

- [x] T018 [P] Validate the documented paths and outputs against the real Feature 1–7 entry points; Expected files changed: `README.md`, `docs/runbooks/end_to_end.md`, `docs/runbooks/troubleshooting.md`, `.env.example`; Acceptance: no command, output path, or artifact family is invented, stale, or missing from the docs.
- [x] T019 Finalize the README as a concise reviewer-facing index with links to the optional deep-dive runbooks; Expected files changed: `README.md`; Acceptance: the README stays scannable, includes the reviewer verification checklist, and routes maintainers to the deeper runbooks without duplicating their content.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: starts immediately and creates the doc surfaces.
- **Phase 2 (Foundational)**: depends on Phase 1 and establishes shared documentation rules.
- **Phase 3 (US1)**: depends on Phase 2.
- **Phase 4 (US2)**: depends on Phase 2 and the quick-start structure from US1.
- **Phase 5 (US3)**: depends on Phase 2 and the command/output mapping from US2.
- **Phase 6 (Polish)**: depends on completion of the core documentation for the desired user stories.

### User Story Dependencies

- **US1 (P1)**: establishes quick-start, configuration, and reviewer verification.
- **US2 (P2)**: depends on US1’s quick-start structure and shared path/index guidance.
- **US3 (P3)**: depends on US2’s command/output mapping and the shared required-vs-optional boundary.

### Dependency Graph

- `US1 -> US2 -> US3`
- `T001-T004` must complete before `T005+`
- `T005-T008` must complete before the story phases

---

## Parallel Execution Examples

### Setup

- Parallel set A: `T002`, `T003`, and `T004` can proceed after the README scaffold exists because they touch different files.

### User Story 2

- Parallel set A: `T013` can run alongside `T014` after the command sequence is established, because one task is the dependency table and the other is the reviewer output summary.

### User Story 3

- Parallel set A: `T016` can run alongside `T017` if the OpenRouter guidance and the recovery navigation guide are being added to different files at the same time.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete the scaffold and foundational docs.
2. Finish US1 so a reviewer can set up the platform and verify the baseline from `README.md` and `.env.example`.
3. Confirm the README is concise and points to the deeper runbooks.

### Incremental Delivery

1. Deliver the reviewer quick-start and maintainer artifact index.
2. Add the full end-to-end runbook with command ordering and expected outputs.
3. Add the troubleshooting runbook with ordered recovery guidance.
4. Finish with a final consistency pass so all documented paths match the real Feature 1–7 scripts and outputs.

### Task Completeness Validation

- Every task produces or updates a concrete documentation artifact.
- Every command in the docs maps to a real `contracts/*.py` entry point.
- Optional OpenRouter behavior is described as optional only and never as a required baseline.
- The final documentation set must let a fresh-clone reviewer and a maintainer both navigate the platform without reverse engineering.
