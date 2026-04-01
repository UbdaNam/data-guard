# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]  
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]  
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]  
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]  
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]  
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- [ ] Spec-first gate: Active spec exists and defines behavior, boundaries, and
      acceptance scenarios before implementation work.
- [ ] Canonical structure gate: Plan uses challenge-required canonical repository
      layout, or explicitly documents approved deviations.
- [ ] Compounding design gate: Deliverables are durable assets reusable by later
      features; no isolated throwaway artifacts.
- [ ] Data contract gate: Schemas, clauses, lineage mappings, validation outputs,
      and violation records are treated as first-class artifacts with stable paths.
- [ ] Evidence gate: Plan defines how mismatch evidence, validation runs, and
      operational reports are generated from real or explicitly injected test data.
- [ ] Python production gate: Module boundaries, typed structures where
      appropriate, deterministic paths, and reproducible CLI commands are defined.
- [ ] Downstream impact gate: Schema/interface changes capture owners,
      dependents, blast radius, and migration expectations.
- [ ] Operability gate: Outputs are structured for translation into plain-language
      operational guidance.
- [ ] Prompt architecture gate: Feature framing builds on approved specs and
      enduring platform capabilities, not temporary checkpoint framing.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
src/
├── contracts/          # canonical schemas, clauses, lineage maps
├── validators/         # contract and quality validation logic
├── pipelines/          # ingestion/normalization/enforcement flows
├── reporting/          # plain-language-ready summaries and exports
├── cli/                # reproducible command entry points
└── lib/                # shared typed utilities and domain primitives

data/
├── samples/            # explicitly injected test data
└── baselines/          # schema drift and comparison baselines

artifacts/
├── validation/         # generated validation outputs
├── violations/         # generated violation records
└── snapshots/          # generated schema snapshots

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Document the selected canonical structure and reference the
real directories captured above. Any deviation MUST be justified in spec and plan.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation                  | Why Needed         | Simpler Alternative Rejected Because |
| -------------------------- | ------------------ | ------------------------------------ |
| [e.g., 4th project]        | [current need]     | [why 3 projects insufficient]        |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient]  |
