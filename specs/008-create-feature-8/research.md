# Research: Developer Workflow and End-to-End Runbook

## Decision 1: Canonical setup uses Python 3.11+ with lockfile-based dependency sync

- **Decision**: The runbook will document Python 3.11+ and recommend `uv sync --extra dev` as the canonical setup path because the repository already ships `uv.lock`.
- **Rationale**: The repository has a lockfile and a modern `pyproject.toml`, so a lockfile-driven install is the most reproducible and reviewer-friendly baseline.
- **Alternatives considered**: `requirements.txt` + `pip install`, Poetry, or a generic manual environment setup. These were rejected because they do not align with the repo’s current lockfile-based workflow.

## Decision 2: Environment variables are read from the process environment only

- **Decision**: `.env.example` will remain a placeholder-only template, and the platform documentation will state that runtime configuration is loaded from environment variables.
- **Rationale**: This preserves a no-secrets policy, avoids hidden configuration state, and keeps the baseline deterministic when OpenRouter is not configured.
- **Alternatives considered**: Auto-loading `.env` in the application or committing real secrets. Both were rejected because they weaken operability and violate the no-secrets requirement.

## Decision 3: README is the quick-start index; deep guidance lives in optional runbooks

- **Decision**: `README.md` will stay concise and reviewer-oriented, while `docs/runbooks/end_to_end.md` and `docs/runbooks/troubleshooting.md` remain optional deep-dive documents.
- **Rationale**: Reviewers need a fast path to verify the platform, while maintainers need deeper recovery and artifact indexing guidance without overwhelming first-time users.
- **Alternatives considered**: A monolithic README or only separate runbooks. The monolithic README was rejected because it becomes hard to scan; runbooks-only was rejected because it hides the quick-start path.

## Decision 4: Canonical workflow order is fixed from generation through reporting

- **Decision**: The documented order is generator -> runner -> attributor -> schema_analyzer -> ai_extensions -> report_generator.
- **Rationale**: This sequence matches the actual CLI entry points and preserves the dependency chain from contract generation through stakeholder reporting.
- **Alternatives considered**: Starting from report generation or allowing ad hoc reordering. Those were rejected because they break the reproducible baseline and make recovery ambiguous.

## Decision 5: OpenRouter is optional and never required for the baseline

- **Decision**: OpenRouter-backed enrichment is documented as optional only; the baseline workflow must succeed deterministically when those environment variables are absent.
- **Rationale**: The feature goal is operability, not dependence on external LLM services.
- **Alternatives considered**: Making AI enrichment a required workflow step or the default report-generation path. Both were rejected because they would make the platform non-deterministic and less reviewable.

## Decision 6: Troubleshooting recovers from the earliest missing prerequisite first

- **Decision**: The troubleshooting guide will instruct users to rerun from the earliest missing prerequisite through the dependent outputs instead of rerunning only the failing step.
- **Rationale**: That approach avoids partial-state confusion and aligns with the artifact dependency graph.
- **Alternatives considered**: One-line error messages only, or ad hoc rerun instructions. Both were rejected because they do not support reliable recovery.

## Decision 7: The runbook documents real CLI entry points and canonical outputs

- **Decision**: The documentation will reference the existing scripts under `contracts/` and their generated outputs under the canonical artifact directories.
- **Rationale**: The feature must reflect real platform behavior rather than inventing new entry points or artifact names.
- **Alternatives considered**: Abstract command names or placeholder outputs. Those were rejected because the runbook would not be directly executable.
