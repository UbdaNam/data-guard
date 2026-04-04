"""Field matching and rename detection."""

from __future__ import annotations

from difflib import SequenceMatcher

from src.models.schema_evolution_models import FieldMatch, MatchType, NormalizedField


def _leaf(path: str) -> str:
    return path.rsplit(".", maxsplit=1)[-1]


def _heuristic_confidence(source: NormalizedField, target: NormalizedField) -> float:
    name_similarity = SequenceMatcher(a=_leaf(source.path), b=_leaf(target.path)).ratio()
    type_score = 1.0 if source.type == target.type else 0.5
    required_score = 1.0 if source.required == target.required else 0.7
    return round((name_similarity * 0.6) + (type_score * 0.3) + (required_score * 0.1), 4)


def match_fields(
    from_fields: list[NormalizedField],
    to_fields: list[NormalizedField],
    explicit_renames: dict[str, str] | None = None,
    heuristic_threshold: float = 0.85,
) -> tuple[list[FieldMatch], set[str], set[str]]:
    explicit_renames = explicit_renames or {}
    from_by_path = {field.path: field for field in from_fields}
    to_by_path = {field.path: field for field in to_fields}

    matches: list[FieldMatch] = []
    matched_from: set[str] = set()
    matched_to: set[str] = set()

    # 1) exact path match
    for path in sorted(from_by_path):
        if path in to_by_path:
            matches.append(
                FieldMatch(
                    from_path=path,
                    to_path=path,
                    match_type=MatchType.exact,
                    confidence=1.0,
                    evidence=["exact_path"],
                )
            )
            matched_from.add(path)
            matched_to.add(path)

    # 2) explicit rename map
    for source_path, target_path in sorted(explicit_renames.items()):
        if source_path in matched_from or target_path in matched_to:
            continue
        if source_path not in from_by_path or target_path not in to_by_path:
            continue
        matches.append(
            FieldMatch(
                from_path=source_path,
                to_path=target_path,
                match_type=MatchType.explicit_rename,
                confidence=1.0,
                evidence=["explicit_mapping"],
            )
        )
        matched_from.add(source_path)
        matched_to.add(target_path)

    # 3) heuristic rename candidates
    unmatched_from = [from_by_path[path] for path in sorted(set(from_by_path) - matched_from)]
    unmatched_to = [to_by_path[path] for path in sorted(set(to_by_path) - matched_to)]
    candidates: list[tuple[float, str, str]] = []
    for source in unmatched_from:
        for target in unmatched_to:
            confidence = _heuristic_confidence(source, target)
            if confidence >= heuristic_threshold:
                candidates.append((confidence, source.path, target.path))

    for confidence, source_path, target_path in sorted(candidates, key=lambda item: (-item[0], item[1], item[2])):
        if source_path in matched_from or target_path in matched_to:
            continue
        matches.append(
            FieldMatch(
                from_path=source_path,
                to_path=target_path,
                match_type=MatchType.heuristic_rename,
                confidence=confidence,
                evidence=["heuristic_name_similarity", "heuristic_type_family"],
            )
        )
        matched_from.add(source_path)
        matched_to.add(target_path)

    return sorted(matches, key=lambda item: ((item.from_path or ""), (item.to_path or ""))), set(from_by_path) - matched_from, set(to_by_path) - matched_to
