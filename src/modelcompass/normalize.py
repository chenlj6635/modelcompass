from __future__ import annotations

from collections.abc import Iterable


def fixed_scale(value: float | None, *, lower: float = 0.0, upper: float = 1.0) -> float | None:
    if value is None:
        return None
    if upper <= lower:
        raise ValueError("upper must be greater than lower")
    return max(0.0, min(1.0, (value - lower) / (upper - lower)))


def normalize_many(values: Iterable[float | None], *, lower: float = 0.0, upper: float = 1.0) -> list[float | None]:
    return [fixed_scale(v, lower=lower, upper=upper) for v in values]