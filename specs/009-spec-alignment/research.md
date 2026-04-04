# Research: Spec Alignment and Platform Completion

## Decision 1: Canonical subscriptions registry path and schema

- **Decision**: Use `docs/governance/subscriptions_registry.yaml` as the canonical registry.
- **Rationale**: Keeps the registry in a stable, reviewable governance location and avoids introducing a parallel artifact family.
- **Alternatives considered**: `contracts/subscriptions_registry.yaml` and JSON serialization were rejected because the artifact is governance-facing and YAML is easier to review and maintain alongside other docs.

## Decision 2: Minimum registry entry fields

- **Decision**: Each interface entry must include `interface_id`, `producer`, `consumer`, `schema_name` or `record_type`, `criticality`, and `dependency_type` or `directness`.
- **Rationale**: This is the smallest set that supports downstream consumer resolution, blast-radius tracing, and migration impact analysis without inference.
- **Alternatives considered**: A looser schema that inferred criticality or dependency type from lineage was rejected because it weakens registry authority.

## Decision 3: Numeric and embedding baseline formats

- **Decision**: Store numeric baselines in `schema_snapshots/baselines.json`; store embedding baselines in `schema_snapshots/ai/<surface_id>/baseline_token_hash_v1.json`.
- **Rationale**: Both paths are stable, discoverable, and already align with the feature’s existing snapshot storage model.
- **Alternatives considered**: A separate `data/` or `artifacts/` directory was rejected because the repository already uses `schema_snapshots/` as the canonical evidence store.

## Decision 4: Validation runner modes

- **Decision**: `AUDIT` records outcomes without escalation, `WARN` emits warnings for threshold breaches, and `ENFORCE` escalates breaches to failure while preserving full report construction.
- **Rationale**: The platform needs a non-destructive review mode, a monitoring mode, and a stricter enforcement mode without changing report completeness.
- **Alternatives considered**: Collapsing all behavior into a single mode was rejected because it would eliminate operational flexibility and make rollback testing harder.

## Decision 5: Drift and confidence formulas

- **Decision**: Use stddev-based numeric drift with WARN for values greater than 2 standard deviations and FAIL for values greater than 3 standard deviations; use `1.0 − (days_since_commit × 0.1) − (lineage_hops × 0.2)` for attribution confidence.
- **Rationale**: These rules are exact, measurable, and match the required platform semantics.
- **Alternatives considered**: Percentile-based or heuristic thresholds were rejected because they are less auditable and harder to reproduce.

## Decision 6: AI extension boundaries

- **Decision**: Governed AI surfaces are the prompt-input schema and structured output schema in `contracts/ai_extensions.py`; OpenRouter is the only optional LLM provider; all configuration comes from environment variables.
- **Rationale**: This keeps AI assistance optional, deterministic by default, and fully bounded by environment configuration.
- **Alternatives considered**: Adding alternate LLM providers or hardcoded model defaults was rejected because it would weaken reproducibility and violate the feature requirements.

## Decision 7: Report action extraction

- **Decision**: Recommended actions must pull the file path, field, and contract clause from the highest-priority evidence item and remain deterministic even when narrative enrichment is added.
- **Rationale**: Stakeholders need specific remediation guidance that maps directly back to evidence.
- **Alternatives considered**: Free-form remediation summaries were rejected because they are too vague for execution.

## Decision 8: Workflow documentation

- **Decision**: Update `README.md`, `.env.example`, and the runbooks to reflect the registry, the mode model, and optional LLM fallback behavior.
- **Rationale**: The feature changes the operating model and must be discoverable by reviewers and maintainers.
- **Alternatives considered**: Leaving workflow docs unchanged was rejected because the new registry and mode semantics would otherwise be opaque.
