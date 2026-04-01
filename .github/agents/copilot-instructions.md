# data-guard Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-02

## Active Technologies
- Python 3.11+ + `pydantic` (typed models), `PyYAML` (YAML rendering), standard library (`json`, `pathlib`, `statistics`, `logging`, `hashlib`, `datetime`) (002-contract-generation-engine)
- File-based artifacts (JSONL/YAML/JSON/Markdown/Mermaid) in canonical repository paths (002-contract-generation-engine)
- Python 3.11+ + `PyYAML` (contract parsing), `pydantic` (typed models), standard library (`json`, `pathlib`, `re`, `statistics`, `datetime`, `hashlib`) (003-validation-drift-engine)
- File-based artifacts (`generated_contracts/*.yaml`, `outputs/**/*.jsonl`, `schema_snapshots/baselines.json`, `validation_reports/*.json`) (003-validation-drift-engine)

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
- 003-validation-drift-engine: Added Python 3.11+ + `PyYAML` (contract parsing), `pydantic` (typed models), standard library (`json`, `pathlib`, `re`, `statistics`, `datetime`, `hashlib`)
- 002-contract-generation-engine: Added Python 3.11+ + `pydantic` (typed models), `PyYAML` (YAML rendering), standard library (`json`, `pathlib`, `statistics`, `logging`, `hashlib`, `datetime`)

- 001-platform-data-surface: Added Python 3.11+ + `pydantic` (typed models), `PyYAML` (YAML metadata),

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
