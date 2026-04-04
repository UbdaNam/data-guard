# data-guard Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-05

## Active Technologies
- Python 3.11+ + `pydantic` (typed models), `PyYAML` (YAML rendering), standard library (`json`, `pathlib`, `statistics`, `logging`, `hashlib`, `datetime`) (002-contract-generation-engine)
- File-based artifacts (JSONL/YAML/JSON/Markdown/Mermaid) in canonical repository paths (002-contract-generation-engine)
- Python 3.11+ + `PyYAML` (contract parsing), `pydantic` (typed models), standard library (`json`, `pathlib`, `re`, `statistics`, `datetime`, `hashlib`) (003-validation-drift-engine)
- File-based artifacts (`generated_contracts/*.yaml`, `outputs/**/*.jsonl`, `schema_snapshots/baselines.json`, `validation_reports/*.json`) (003-validation-drift-engine)
- Python 3.11+ + `pydantic` (typed models), `PyYAML` (Feature 1/2 artifacts), standard library (`json`, `pathlib`, `subprocess`, `datetime`, `hashlib`, `collections`) (004-violation-attribution)
- File-based artifacts (`validation_reports/*.json`, `outputs/week4/lineage_snapshots.jsonl`, `contracts/*.yaml|json`, `generated_contracts/*.yaml`, `violation_log/violations.jsonl`) (004-violation-attribution)
- Python 3.11+ + `pydantic` (typed models), `PyYAML` (contract/metadata loading), standard library (`json`, `pathlib`, `hashlib`, `datetime`, `dataclasses`, `re`) (005-schema-evolution-intelligence)
- File-based artifacts (`generated_contracts/*.yaml`, `schema_snapshots/{contract_id}/`, `contracts/*.yaml|json`, `validation_reports/*.json`, `violation_log/violations.jsonl`) (005-schema-evolution-intelligence)
- Python 3.11+ + `pydantic`, `PyYAML`, Python standard library (`json`, `pathlib`, `hashlib`, `datetime`, `statistics`, `math`, `typing`) (006-ai-contract-enforcement)
- File-based artifact storage in canonical repository paths (`outputs/`, `validation_reports/`, `violation_log/`, `schema_snapshots/`, `generated_contracts/`, `contracts/`) (006-ai-contract-enforcement)
- Python 3.11+ + Standard library (`json`, `pathlib`, `datetime`, `statistics`, `os`, `hashlib`, `urllib.request`), `pydantic>=2.6`, `PyYAML>=6.0` (007-operational-report-generation)
- File-based artifacts in repository paths (read-only upstream inputs + generated report outputs) (007-operational-report-generation)
- [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION] + [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION] (008-create-feature-8)
- [if applicable, e.g., PostgreSQL, CoreData, files or N/A] (008-create-feature-8)
- Python 3.11+ for the platform; Markdown for operational documentation + `uv` lockfile-based environment sync, `pydantic>=2.6`, `PyYAML>=6.0`, Python standard library for existing CLI tools; no new runtime dependency is introduced by this feature (008-create-feature-8)
- File-based repository artifacts only (`README.md`, `.env.example`, optional `docs/runbooks/*.md`, and the existing CLI-generated JSON/YAML/Markdown outputs) (008-create-feature-8)
- Python 3.11+ + `uv`, `pydantic>=2.6`, `PyYAML>=6.0` (008-create-feature-8)
- File-based artifacts in canonical repository paths (008-create-feature-8)

- Python 3.11+ + `pydantic` (typed models), `PyYAML` (YAML metadata), (001-platform-data-surface)

## Project Structure

```text
src/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

Python 3.11+: Follow standard conventions

## Recent Changes
- 008-create-feature-8: Added Python 3.11+ + `uv`, `pydantic>=2.6`, `PyYAML>=6.0`
- 008-create-feature-8: Added Python 3.11+ for the platform; Markdown for operational documentation + `uv` lockfile-based environment sync, `pydantic>=2.6`, `PyYAML>=6.0`, Python standard library for existing CLI tools; no new runtime dependency is introduced by this feature
- 008-create-feature-8: Added [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION] + [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
