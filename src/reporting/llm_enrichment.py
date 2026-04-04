"""Optional OpenRouter narrative enrichment with deterministic fallback."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

from src.reporting.env_config import EnrichmentConfig


@dataclass(slots=True)
class EnrichmentResult:
    narratives: dict[str, str]
    status: str
    fallback_used: bool


def _numbers(text: str) -> set[str]:
    return set(re.findall(r"\b\d+(?:\.\d+)?\b", text))


def _validate_grounding(*, baseline: dict[str, str], candidate: dict[str, str]) -> bool:
    for key, baseline_text in baseline.items():
        proposed = candidate.get(key, "")
        if not proposed.strip():
            return False
        if not _numbers(proposed).issubset(_numbers(baseline_text) | {"0"}):
            return False
    return True


def _request_openrouter(*, config: EnrichmentConfig, baseline: dict[str, str], timeout_seconds: int = 10) -> dict[str, str] | None:
    if not (config.is_configured and config.provider_valid and config.api_key and config.base_url and config.model):
        return None

    payload = {
        "model": config.model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You rewrite deterministic operational report section summaries. "
                    "Do not introduce new incidents, claims, recommendations, or numbers."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "instruction": "Rewrite each section value for readability while preserving exact factual content.",
                        "sections": baseline,
                        "required_format": "JSON object with exactly the same top-level keys.",
                    },
                    ensure_ascii=False,
                ),
            },
        ],
        "temperature": 0,
    }

    request = urllib.request.Request(
        url=config.base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:  # noqa: S310
            body = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return None

    choices = body.get("choices") if isinstance(body, dict) else None
    if not isinstance(choices, list) or not choices:
        return None
    content = (((choices[0] or {}).get("message") or {}).get("content"))
    if not isinstance(content, str):
        return None

    try:
        candidate = json.loads(content)
    except json.JSONDecodeError:
        return None

    if not isinstance(candidate, dict):
        return None

    if set(candidate.keys()) != set(baseline.keys()):
        return None

    return {str(k): str(v) for k, v in candidate.items()}


def maybe_enrich_narratives(
    *,
    enabled: bool,
    config: EnrichmentConfig,
    fallback_narratives: dict[str, str],
) -> EnrichmentResult:
    if not enabled:
        return EnrichmentResult(
            narratives=fallback_narratives,
            status="disabled",
            fallback_used=True,
        )

    if not config.is_configured or not config.provider_valid:
        return EnrichmentResult(
            narratives=fallback_narratives,
            status="missing_config",
            fallback_used=True,
        )

    candidate = _request_openrouter(config=config, baseline=fallback_narratives)
    if not candidate:
        return EnrichmentResult(
            narratives=fallback_narratives,
            status="failed",
            fallback_used=True,
        )

    if not _validate_grounding(baseline=fallback_narratives, candidate=candidate):
        return EnrichmentResult(
            narratives=fallback_narratives,
            status="failed",
            fallback_used=True,
        )

    return EnrichmentResult(
        narratives=candidate,
        status="applied",
        fallback_used=False,
    )
