"""Schema inference helpers for nested field handling."""

from __future__ import annotations

from src.models.contract_models import ProfiledField


def infer_schema_map(profiled_fields: list[ProfiledField]) -> dict[str, dict[str, str | None]]:
    """Return a nested-path schema map preserving parent-child links."""

    return {
        field.field_path: {
            "parent": field.parent_path,
            "types": ",".join(field.observed_types) if field.observed_types else None,
        }
        for field in profiled_fields
    }


def flatten_for_dbt(profiled_fields: list[ProfiledField]) -> list[str]:
    """Return deterministic flattened paths for dbt-facing mapping."""

    return [field.field_path for field in sorted(profiled_fields, key=lambda f: f.field_path)]
