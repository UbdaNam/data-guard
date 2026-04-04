# Tasks: Spec Alignment and Platform Completion

**Input**: Design documents from `/specs/009-spec-alignment/`
**Prerequisites**: `spec.md` (required), `plan.md` (required), `research.md`, `data-model.md`, `quickstart.md`

**Tests**: Not requested in the feature specification. This task list focuses on implementation-ready documentation and code deltas.

**Organization**: Tasks are ordered so the subscriptions registry and shared baseline helpers exist before dependent contract, validation, attribution, AI, report, and workflow updates.

## Format: `[ID] [P?] [Story] Title`

- **[P]**: Can run in parallel with other tasks that do not touch the same files or depend on incomplete work.
- **[Story]**: User story label from the approved spec (`US1`, `US2`, `US3`, `US4`).
- Every task includes objective, files changed, dependencies, and acceptance criteria.

---

## Phase 1: Setup (Shared Governance Scaffold)

**Purpose**: Establish the canonical registry artifact and shared helpers that later components will consume.

- [ ] T001 Create the canonical subscriptions registry scaffold at `docs/governance/subscriptions_registry.yaml`.
  - Objective: Establish the first-class governance artifact at the approved path with the required top-level YAML shape.
  - Files changed: `docs/governance/subscriptions_registry.yaml`
  - Dependencies: none
  - Acceptance criteria: The file exists, is machine-readable YAML, and contains top-level `version`, `generated_at`, and `interfaces` keys.

- [ ] T002 [P] Add a registry loader/helper in `contracts/registry_loader.py`.
  - Objective: Provide shared parsing and lookup utilities for downstream attribution, blast radius, and schema evolution logic.
  - Files changed: `contracts/registry_loader.py`
  - Dependencies: T001
  - Acceptance criteria: The helper can load `docs/governance/subscriptions_registry.yaml`, validate required fields, and expose interface lookup by `interface_id`, producer, and consumer.

- [ ] T003 [P] Add canonical artifact path constants in `contracts/artifact_paths.py`.
  - Objective: Centralize repository paths for baseline, snapshot, report, and registry artifacts so later modules use the same canonical locations.
  - Files changed: `contracts/artifact_paths.py`
  - Dependencies: T001
  - Acceptance criteria: The helper defines stable constants for `docs/governance/subscriptions_registry.yaml`, `schema_snapshots/baselines.json`, `schema_snapshots/ai/`, `validation_reports/`, `violation_log/`, `generated_contracts/`, and `outputs/week4/lineage_snapshots.jsonl`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Populate the registry and shared baseline helpers before any feature work depends on them.

- [ ] T004 Populate the minimum required producer-consumer interfaces in `docs/governance/subscriptions_registry.yaml`.
  - Objective: Seed the registry with the required governed interfaces and fields so downstream components have an authoritative topology source.
  - Files changed: `docs/governance/subscriptions_registry.yaml`
  - Dependencies: T001
  - Acceptance criteria: The registry contains the minimum required interface set and each entry includes `interface_id`, `producer`, `consumer`, `schema_name` or `record_type`, `criticality`, and `dependency_type` or `directness`.

- [ ] T005 [P] Extend `contracts/registry_loader.py` with schema validation and traversal helpers.
  - Objective: Make the registry helper enforce the required schema and expose direct/transitive subscriber traversal primitives.
  - Files changed: `contracts/registry_loader.py`
  - Dependencies: T002, T004
  - Acceptance criteria: The helper rejects malformed entries, returns first-hop subscribers, returns transitive downstream nodes, and can compute contamination depth from registry relationships.

- [ ] T006 [P] Add baseline store helpers in `contracts/baseline_store.py`.
  - Objective: Centralize read/write behavior for numeric and embedding baseline artifacts used by generation, validation, and AI drift checks.
  - Files changed: `contracts/baseline_store.py`
  - Dependencies: T003
  - Acceptance criteria: The helper can read and write `schema_snapshots/baselines.json` and `schema_snapshots/ai/<surface_id>/baseline_token_hash_v1.json` using the canonical artifact paths.

---

## Phase 3: User Story 1 - Subscriptions Registry and Topology (Priority: P1)

**Goal**: A governed subscriptions registry exists as the canonical topology source and is consumable by downstream components.

**Independent Test**: The registry can be loaded, validated, and queried for subscriber topology without relying on lineage alone.

- [ ] T007 [US1] Wire the registry loader into `contracts/attributor.py` and `contracts/schema_analyzer.py`.
  - Objective: Make the registry the first source consulted for subscriber topology before or alongside lineage traversal.
  - Files changed: `contracts/attributor.py`, `contracts/schema_analyzer.py`
  - Dependencies: T005
  - Acceptance criteria: Both modules load the canonical registry through the shared helper and can resolve producers, consumers, and interfaces from the registry before falling back to lineage.

- [ ] T008 [US1] Expose registry-driven topology outputs in `contracts/attributor.py`.
  - Objective: Ensure topology outputs can distinguish direct subscribers, transitive downstream nodes, and contamination depth.
  - Files changed: `contracts/attributor.py`
  - Dependencies: T007
  - Acceptance criteria: Attribution and blast-radius outputs include `direct_subscribers`, `transitive_downstream_nodes`, and `contamination_depth` as explicit fields derived from registry relationships.

**Checkpoint**: The registry is a first-class, validated, and queryable platform artifact.

---

## Phase 4: User Story 2 - Contract Generation and Validation (Priority: P1)

**Goal**: Contract generation and validation produce authoritative baselines, explicit confidence rules, and mode-aware drift reporting.

**Independent Test**: A reviewer can run generation and validation without OpenRouter and still obtain numeric baselines, confidence constraints, drift outcomes, and complete reports.

- [ ] T009 [US2] Add numeric baseline write support for governed numeric fields in `contracts/generator.py`.
  - Objective: Persist authoritative numeric baselines for later stddev-based drift detection.
  - Files changed: `contracts/generator.py`, `schema_snapshots/baselines.json`
  - Dependencies: T006
  - Acceptance criteria: The generator writes `schema_snapshots/baselines.json` with sample count, mean, standard deviation, and distribution data for governed numeric fields.

- [ ] T010 [US2] Inject explicit 0.0–1.0 confidence constraints in `contracts/generator.py`.
  - Objective: Ensure governed confidence fields receive hard range clauses rather than inferable behavior.
  - Files changed: `contracts/generator.py`
  - Dependencies: T009
  - Acceptance criteria: Generated contracts contain explicit 0.0–1.0 constraints for governed confidence or probability fields such as `confidence`, `confidence_score`, and equivalent variants.

- [ ] T011 [US2] Extract downstream consumers from the latest Week 4 lineage snapshot in `contracts/generator.py`.
  - Objective: Inject consumer mappings from the most recent Week 4 lineage snapshot into generated contracts.
  - Files changed: `contracts/generator.py`, `outputs/week4/lineage_snapshots.jsonl`
  - Dependencies: T005, T009
  - Acceptance criteria: The generator uses the latest successfully produced Week 4 lineage snapshot and writes downstream consumer references into generated contracts.

- [ ] T012 [US2] Add optional OpenRouter-based ambiguous-field annotation and deterministic fallback in `contracts/generator.py`.
  - Objective: Allow LLM-assisted annotations only when OpenRouter is configured, while keeping the default path deterministic.
  - Files changed: `contracts/generator.py`, `.env.example` (config reference only)
  - Dependencies: T010, T011
  - Acceptance criteria: Ambiguous-field annotations are emitted only when OpenRouter env vars are present; otherwise the generator completes using deterministic non-LLM behavior.

- [ ] T013 [US2] Add the numeric baseline loader and mean/stddev drift calculation in `contracts/runner.py`.
  - Objective: Make validation load canonical baselines before drift computation.
  - Files changed: `contracts/runner.py`
  - Dependencies: T006, T009
  - Acceptance criteria: The runner loads `schema_snapshots/baselines.json` and computes drift in standard-deviation units from the loaded mean and standard deviation values.

- [ ] T014 [US2] Implement WARN > 2σ and FAIL > 3σ logic plus explicit confidence range checks in `contracts/runner.py`.
  - Objective: Separate drift thresholds from confidence validation and preserve structured ERROR results.
  - Files changed: `contracts/runner.py`
  - Dependencies: T013
  - Acceptance criteria: Drift values greater than 2σ but not greater than 3σ produce WARN, values greater than 3σ produce FAIL, and any confidence field outside 0.0–1.0 produces an independent range error.

- [ ] T015 [US2] Add `--mode` semantics for `AUDIT`, `WARN`, and `ENFORCE` in `contracts/runner.py`.
  - Objective: Support mode-specific behavior without losing full report construction.
  - Files changed: `contracts/runner.py`
  - Dependencies: T014
  - Acceptance criteria: `AUDIT` records all outcomes without escalation, `WARN` records threshold breaches as warnings, `ENFORCE` escalates threshold breaches to failures, and all modes still emit complete reports.

**Checkpoint**: Contract generation and validation are baseline-aware, mode-aware, and deterministic by default.

---

## Phase 5: User Story 3 - Attribution, Blast Radius, and Schema Evolution (Priority: P2)

**Goal**: Attribution, blast radius, and schema evolution use the registry and lineage data to produce exact confidence, impact, and migration guidance.

**Independent Test**: A reviewer can trace a violation through registry-assisted attribution and verify the required blast-radius and migration outputs.

- [ ] T016 [US3] Integrate registry-assisted subscriber resolution into `contracts/attributor.py`.
  - Objective: Make attribution consult the subscriptions registry before or alongside lineage traversal.
  - Files changed: `contracts/attributor.py`
  - Dependencies: T007
  - Acceptance criteria: Attribution uses the canonical registry to resolve producers/consumers and only then augments or cross-checks lineage evidence.

- [ ] T017 [US3] Implement the exact attribution confidence formula and five-candidate cap in `contracts/attributor.py`.
  - Objective: Make candidate ranking and confidence scoring deterministic and bounded.
  - Files changed: `contracts/attributor.py`
  - Dependencies: T016
  - Acceptance criteria: Confidence is computed as `1.0 − (days_since_commit × 0.1) − (lineage_hops × 0.2)`, no more than five ranked candidates are returned, and at least one candidate is returned when attribution evidence exists.

- [ ] T018 [US3] Enrich `blast_radius` in `contracts/attributor.py` with the required downstream impact fields.
  - Objective: Emit structured blast-radius data that distinguishes direct and transitive impact.
  - Files changed: `contracts/attributor.py`
  - Dependencies: T016, T017
  - Acceptance criteria: `blast_radius` includes `affected_nodes`, `affected_pipelines`, `direct_subscribers`, `transitive_downstream_nodes`, and `contamination_depth`.

- [ ] T019 [US3] Implement the explicit CRITICAL classifier rule in `contracts/schema_analyzer.py`.
  - Objective: Classify the float 0.0–1.0 → int 0–100 narrowing rule as a breaking change.
  - Files changed: `contracts/schema_analyzer.py`
  - Dependencies: T007
  - Acceptance criteria: Schema evolution marks the narrowing change as CRITICAL and reflects that severity in the diff output.

- [ ] T020 [US3] Add per-consumer failure-mode analysis in `contracts/schema_analyzer.py`.
  - Objective: Use registry and lineage data to name impacted consumers and likely failures.
  - Files changed: `contracts/schema_analyzer.py`
  - Dependencies: T019
  - Acceptance criteria: Migration impact outputs name specific downstream consumers and list likely failure modes for each consumer.

- [ ] T021 [US3] Add rollback and baseline re-establishment requirements to migration impact rendering in `contracts/schema_analyzer.py`.
  - Objective: Make recovery guidance explicit in schema evolution outputs.
  - Files changed: `contracts/schema_analyzer.py`
  - Dependencies: T020
  - Acceptance criteria: Migration impact outputs include rollback steps and baseline re-establishment requirements where applicable.

**Checkpoint**: Attribution and schema evolution outputs are exact, registry-aware, and operationally actionable.

---

## Phase 6: User Story 4 - AI Extensions, Reporting, and Workflow (Priority: P2)

**Goal**: AI enforcement, report generation, and workflow documentation are deterministic by default, OpenRouter-only for optional LLM assistance, and fully documented.

**Independent Test**: A reviewer can run AI enforcement and report generation with OpenRouter absent and still receive quarantines, warnings, metrics, explicit health scoring, and deterministic outputs.

- [ ] T022 [US4] Implement the embedding baseline writer/loader and cosine-distance drift detection in `contracts/ai_extensions.py`.
  - Objective: Persist and compare embedding centroids for governed AI surfaces.
  - Files changed: `contracts/ai_extensions.py`, `schema_snapshots/ai/<surface_id>/baseline_token_hash_v1.json`
  - Dependencies: T006
  - Acceptance criteria: The module writes and loads embedding baseline centroid artifacts and computes drift using cosine distance against the canonical baseline file.

- [ ] T023 [US4] Add governed prompt input JSON Schema validation and quarantine routing in `contracts/ai_extensions.py`.
  - Objective: Make invalid prompt inputs non-blocking but explicitly quarantined.
  - Files changed: `contracts/ai_extensions.py`, `outputs/quarantine/`
  - Dependencies: T022
  - Acceptance criteria: Governed prompt inputs are validated before AI execution and invalid inputs are routed to quarantine outputs instead of silently dropping or executing them.

- [ ] T024 [US4] Add structured LLM output violation-rate tracking and WARN logging in `contracts/ai_extensions.py`.
  - Objective: Track output schema quality and emit WARN entries when thresholds are exceeded.
  - Files changed: `contracts/ai_extensions.py`, `violation_log/ai_violations.jsonl`
  - Dependencies: T023
  - Acceptance criteria: The module tracks schema-violation rate per governed surface and writes WARN entries to `violation_log/ai_violations.jsonl` when configured thresholds are exceeded.

- [ ] T025 [US4] Keep all AI extension flows orchestrated through `contracts/ai_extensions.py` with OpenRouter-only environment-driven fallback behavior.
  - Objective: Ensure AI-assisted behavior stays behind one entry point and remains optional.
  - Files changed: `contracts/ai_extensions.py`, `.env.example`
  - Dependencies: T022, T023, T024
  - Acceptance criteria: All AI extension flows are invoked through `contracts/ai_extensions.py`, use OpenRouter only when environment variables are present, and fall back deterministically when OpenRouter is absent.

- [ ] T026 [US4] Update the report health score calculation and explicit score rendering in `contracts/report_generator.py`.
  - Objective: Make the report score formula deterministic and visible in outputs.
  - Files changed: `contracts/report_generator.py`
  - Dependencies: T015, T024
  - Acceptance criteria: The report uses `(checks_passed / total_checks × 100) − (20 × critical_violation_count)` and renders the calculation inputs explicitly in report output.

- [ ] T027 [US4] Add precise action extraction and prioritization in `contracts/report_generator.py`.
  - Objective: Turn top violations and schema changes into concrete remediation items.
  - Files changed: `contracts/report_generator.py`
  - Dependencies: T026
  - Acceptance criteria: Recommended actions include the exact file path, field, and contract clause, and are prioritized from the most severe evidence first.

- [ ] T028 [US4] Preserve deterministic report rendering with optional OpenRouter narrative fallback in `contracts/report_generator.py`.
  - Objective: Keep report generation non-blocking and deterministic while allowing optional enrichment.
  - Files changed: `contracts/report_generator.py`
  - Dependencies: T026, T027
  - Acceptance criteria: Reports render deterministically without OpenRouter, optional narrative enrichment is additive only, and report generation still completes when enrichment is unavailable.

- [ ] T029 [US4] Update `.env.example`, `README.md`, and the runbooks for the new registry, validation modes, AI completion, and report behavior.
  - Objective: Make the operational workflow discoverable for reviewers and maintainers.
  - Files changed: `.env.example`, `README.md`, `docs/runbooks/end_to_end.md`, `docs/runbooks/troubleshooting.md`
  - Dependencies: T025, T026, T027, T028
  - Acceptance criteria: The docs explicitly document `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, and `OPENROUTER_MODEL` as placeholder-only variables, describe the subscriptions registry path, explain `AUDIT`/`WARN`/`ENFORCE`, and show the deterministic fallback path when OpenRouter is absent.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency pass across all feature-aligned artifacts to ensure no conflicting paths or parallel systems remain.

- [ ] T030 Perform a cross-feature alignment pass across `contracts/*.py`, `README.md`, `.env.example`, and the runbooks.
  - Objective: Verify that all updated paths, formulas, and behaviors remain canonical and non-duplicative.
  - Files changed: `contracts/generator.py`, `contracts/runner.py`, `contracts/attributor.py`, `contracts/schema_analyzer.py`, `contracts/ai_extensions.py`, `contracts/report_generator.py`, `README.md`, `.env.example`, `docs/runbooks/end_to_end.md`, `docs/runbooks/troubleshooting.md`
  - Dependencies: T007, T015, T021, T029
  - Acceptance criteria: All docs and code paths reference the canonical registry, baselines, and report artifacts; no alternate registry, baseline, or LLM provider is introduced; and the platform boundaries from Features 2–8 remain intact.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)** starts immediately and creates the governance scaffold.
- **Phase 2 (Foundational)** depends on Phase 1 and blocks all user-story work.
- **Phase 3 (US1)** depends on Phase 2 and establishes registry topology consumption.
- **Phase 4 (US2)** depends on Phase 2 and the shared baseline helpers from Phase 1/2.
- **Phase 5 (US3)** depends on Phase 3 and the shared baseline helpers.
- **Phase 6 (US4)** depends on Phases 2–5 because AI, reporting, and docs consume the prior artifacts.
- **Phase 7 (Polish)** depends on completion of the core workstreams.

### User Story Dependencies

- **US1** establishes the canonical subscriptions registry and its loader.
- **US2** depends on shared baseline helpers and the registry topology source.
- **US3** depends on the registry topology and the contract/validation outputs.
- **US4** depends on the updated generator, runner, attribution, and schema outputs.

### Parallel Opportunities

- `T002` and `T003` can run in parallel because they touch different helper modules.
- `T005` and `T006` can run in parallel once the registry scaffold exists.
- In US2, `T010`, `T011`, and `T012` can be sequenced on the same generator module but are independently reviewable sub-deltas.
- In US3, `T020` and `T021` can be split across separate migration-impact edits inside `contracts/schema_analyzer.py`.
- In US4, `T023` and `T024` can be staged independently within `contracts/ai_extensions.py` after the embedding baseline flow exists.

## Implementation Strategy

### MVP First

1. Complete Phases 1–3 so the canonical subscriptions registry is in place and consumable.
2. Complete Phase 4 so contract generation and validation are baseline-aware and mode-aware.
3. Validate that the platform still runs deterministically without OpenRouter before moving to the remaining workstreams.

### Incremental Delivery

1. Ship the registry scaffold and loader.
2. Add baseline generation and runner semantics.
3. Add registry-assisted attribution and schema evolution.
4. Add AI extensions and report alignment.
5. Finish with docs and workflow updates.

### Notes

- No test tasks are included because the feature specification does not request TDD or new automated tests.
- All tasks are designed to extend the existing platform rather than create a parallel registry, validation stack, or LLM provider path.
