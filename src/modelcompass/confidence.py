from __future__ import annotations

from datetime import date


def confidence_score(*, source: str, freshness: float, version: float, coverage: float) -> float:
    source_weight = {"official": 1.0, "third_party": 0.85, "manual": 0.70}.get(source, 0.5)
    return max(0.0, min(1.0, source_weight * freshness * version * coverage))


def freshness_score(observed_at: date, *, as_of: date, half_life_days: float = 180.0) -> float:
    age = max(0, (as_of - observed_at).days)
    return 0.5 ** (age / half_life_days)