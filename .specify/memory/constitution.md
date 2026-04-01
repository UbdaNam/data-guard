<!--
Sync Impact Report
- Version change: N/A (template) → 1.0.0
- Modified principles:
	- Template Principle 1 → I. Spec-First Delivery
	- Template Principle 2 → II. Canonical Structure Discipline
	- Template Principle 3 → III. Compounding Feature Design
	- Template Principle 4 → IV. Data Contracts as Product Primitives
	- Template Principle 5 → V. Evidence Over Assumption
	- Added VI. Production-Grade Python Conventions
	- Added VII. No Fabricated Operational Artifacts
	- Added VIII. Downstream Impact Awareness
	- Added IX. Plain-Language Operability
	- Added X. Feature Prompts Reinforce Platform Architecture
- Added sections:
	- Platform Constraints
	- Delivery Workflow & Quality Gates
- Removed sections:
	- None
- Templates requiring updates:
	- ✅ .specify/templates/plan-template.md
	- ✅ .specify/templates/spec-template.md
	- ✅ .specify/templates/tasks-template.md
	- ⚠ pending (not present): .specify/templates/commands/*.md
- Runtime guidance updates:
	- ✅ README.md
- Deferred TODOs:
	- None
-->

# data-guard Constitution

## Core Principles

### I. Spec-First Delivery

All work MUST begin from the active Spec Kit feature specification in
specs/[###-feature-name]/spec.md. Implementation planning and coding MUST NOT start
until product behavior, boundaries, and acceptance scenarios are defined in the
active specification.

Rationale: This prevents implementation drift and keeps delivery tied to explicit
product intent.

### II. Canonical Structure Discipline

The repository MUST use the challenge-required file and folder structure as the
canonical project layout. Any deviation MUST be explicitly documented in the active
specification and supporting implementation notes before code is merged.

Rationale: Stable structure reduces onboarding cost and avoids accidental divergence
between features.

### III. Compounding Feature Design

Each feature MUST produce durable assets reused by later features. Teams MUST NOT
ship isolated artifacts that subsequent features must replace or reinterpret.

Rationale: Compounding assets create cumulative delivery velocity and reduce
rework.

### IV. Data Contracts as Product Primitives

Schemas, contract clauses, lineage mappings, validation outputs, and violation
records are first-class platform assets. These assets MUST be stored in stable,
discoverable repository locations and referenced by feature specifications and
plans.

Rationale: The platform exists to enforce data contracts; those artifacts are core
product state, not byproducts.

### V. Evidence Over Assumption

If upstream datasets or prior outputs diverge from the canonical target schema,
the system MUST record the mismatch, preserve the canonical target as the
standard, and define explicit migration or normalization requirements.

Rationale: Recorded evidence enables reliable remediation and auditability.

### VI. Production-Grade Python Conventions

Implementation plans MUST assume a maintainable Python project with clear module
boundaries, reproducible CLI entry points, deterministic paths, typed data
structures where appropriate, and evaluator-runnable commands.

Rationale: Operational reliability requires predictable structure and execution.

### VII. No Fabricated Operational Artifacts

Validation reports, violation logs, schema snapshots, drift baselines, and
generated reports MUST come from actual executions on real or explicitly injected
test data. Fabricated or manually invented operational outputs are prohibited.

Rationale: Trust in contract enforcement depends on traceable, reproducible
evidence.

### VIII. Downstream Impact Awareness

When schemas, fields, or interfaces are defined or changed, ownership and
downstream consumer context MUST be captured so later features can compute blast
radius and migration impact without rediscovery.

Rationale: Explicit downstream metadata reduces accidental breakage and migration
risk.

### IX. Plain-Language Operability

Technical outputs that may feed stakeholder-facing reporting MUST be structured so
they can be translated into plain-language operational guidance without reverse
engineering.

Rationale: Operational stakeholders require clear, non-ambiguous guidance derived
from technical evidence.

### X. Feature Prompts Reinforce Platform Architecture

Every feature prompt MUST preserve canonical repository layout, build on prior
approved specifications, and describe enduring product capabilities. Prompts MUST
NOT frame delivery around temporary submission checkpoints or deadlines.

Rationale: Product architecture consistency depends on feature framing, not only on
implementation details.

## Platform Constraints

- Python is the primary implementation language for production deliverables.
- Project modules MUST be organized for maintainability and deterministic imports.
- Contract artifacts MUST remain versioned and discoverable in repository paths
  declared by active specs.
- Commands in specs, plans, and quickstarts MUST be executable in evaluator
  environments without private tooling assumptions.

## Delivery Workflow & Quality Gates

1. Specification gate: A feature MUST have an approved spec with testable user
   scenarios before planning starts.
2. Planning gate: The implementation plan MUST pass Constitution Check items tied
   to all ten principles.
3. Execution gate: Tasks MUST map to user stories and include contract/evidence
   generation work where applicable.
4. Validation gate: Completion requires reproducible execution outputs for
   validations, violations, and reports.
5. Change gate: Schema/interface changes MUST include downstream impact and
   migration expectations.

## Governance

This constitution supersedes conflicting local process notes. All feature specs,
plans, tasks, and implementation reviews MUST include a constitution compliance
check.

Amendments MUST include: (1) proposed text changes, (2) impact on existing
templates/guidance, and (3) semantic version bump justification.

Versioning policy:

- MAJOR: Backward-incompatible governance or principle removals/redefinitions.
- MINOR: New principle/section additions or materially expanded guidance.
- PATCH: Clarifications, wording improvements, and non-semantic refinements.

Compliance review expectations:

- Each pull request MUST confirm adherence to applicable principles.
- Reviewers MUST reject changes that omit required spec-first, data contract,
  evidence, or downstream impact obligations.
- Runtime guidance documents (including README and Spec Kit templates) MUST remain
  synchronized with amended principles.

**Version**: 1.0.0 | **Ratified**: 2026-04-01 | **Last Amended**: 2026-04-01
