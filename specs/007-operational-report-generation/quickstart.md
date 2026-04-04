# Quickstart: Operational Report Generation

## Prerequisites

- Python 3.11+
- Repository root as current working directory
- Upstream evidence artifacts available:
  - `validation_reports/*.json` (Feature 3)
  - `violation_log/violations.jsonl` (Feature 4)
  - schema evolution outputs (Feature 5)
  - `validation_reports/ai_metrics.json` (Feature 6)
  - Feature 1 metadata artifacts in `contracts/`

## 1) Run deterministic report generation (default, no LLM)

```bash
python -m contracts.report_generator
```

Expected outputs:

- `enforcer_report/report_data.json`
- `enforcer_report/report_{date}.md`

## 2) Run with explicit reporting window

```bash
python -m contracts.report_generator \
  --report-start 2026-04-01T00:00:00Z \
  --report-end 2026-04-04T23:59:59Z
```

## 3) Optional OpenRouter enrichment (must remain non-blocking)

Set environment variables first:

- `OPENROUTER_API_KEY`
- `OPENROUTER_BASE_URL`
- `OPENROUTER_MODEL`

Then run:

```bash
python -m contracts.report_generator --enable-llm-enrichment
```

If configuration is missing/invalid or provider call fails, generation still succeeds with deterministic fallback narrative and enrichment status recorded in `generation_metadata`.

## 4) Determinism checks

- Re-run with unchanged inputs and compare `report_data.json` ignoring allowed variable metadata fields (`report_id`, `generated_at`, duration).
- Confirm ordered sections and ordered ranked lists remain stable.
- Confirm markdown section order is fixed:
  1. Data Health Score
  2. Violations this period
  3. Schema changes detected
  4. AI system risk assessment
  5. Recommended actions
  6. Evidence traceability notes

## 5) Partial/missing input behavior checks

- Remove one artifact family (e.g., schema evolution outputs) and re-run.
- Confirm both outputs are still generated.
- Confirm affected section is present with `insufficient_evidence` and explicit `missing_sources` references.

## 6) Minimum smoke checklist

- `data_health_score` follows FR-032 formula and FR-033 null behavior.
- Every top violation and recommended action includes evidence references.
- Recommended actions include target, location, owner context, and verification step.
- Enrichment cannot add unsupported incidents/actions.
