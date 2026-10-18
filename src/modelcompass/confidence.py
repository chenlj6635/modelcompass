from __future__ import annotations

from datetime import date
import math


def _unit_interval(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return max(0.0, min(1.0, value))


def confidence_score(*, source: str, freshness: float, version: float, coverage: float) -> float:
    """Combine evidence dimensions; quality values are deliberately not an input."""
    source_weight = {"official": 1.0, "third_party": 0.85, "manual": 0.70}.get(source, 0.5)
    return source_weight * _unit_interval(freshness, "freshness") * _unit_interval(version, "version") * _unit_interval(coverage, "coverage")


def freshness_score(observed_at: date, *, as_of: date, half_life_days: float = 180.0) -> float:
    if half_life_days <= 0:
        raise ValueError("half_life_days must be greater than zero")
    age = max(0, (as_of - observed_at).days)
    return 0.5 ** (age / half_life_days)