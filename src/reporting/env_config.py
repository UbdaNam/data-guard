"""Environment configuration helpers for optional OpenRouter enrichment."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class EnrichmentConfig:
    api_key: str | None
    base_url: str | None
    model: str | None

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.base_url and self.model)

    @property
    def provider_valid(self) -> bool:
        if not self.base_url:
            return False
        normalized = self.base_url.lower()
        return "openrouter" in normalized


def load_enrichment_config() -> EnrichmentConfig:
    return EnrichmentConfig(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url=os.getenv("OPENROUTER_BASE_URL"),
        model=os.getenv("OPENROUTER_MODEL"),
    )
