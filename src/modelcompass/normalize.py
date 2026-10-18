from __future__ import annotations

from collections.abc import Iterable
import math


def fixed_scale(value: float | None, *, lower: float = 0.0, upper: float = 1.0) -> float | None:
    """Map a value to a fixed [0, 1] scale without imputing missing values."""
    if upper <= lower:
        raise ValueError("upper must be greater than lower")
    if value is None:
        return None
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("value must be finite")
    return max(0.0, min(1.0, (value - lower) / (upper - lower)))


def normalize_many(
    values: Iterable[float | None], *, lower: float = 0.0, upper: float = 1.0
) -> list[float | None]:
    return [fixed_scale(value, lower=lower, upper=upper) for value in values]