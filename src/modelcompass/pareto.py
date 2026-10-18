from __future__ import annotations

from collections.abc import Mapping


def _validate_axes(axes: list[tuple[str, str]]) -> None:
    if len(axes) not in {2, 3}:
        raise ValueError("axes must contain 2 or 3 dimensions")
    if len({name for name, _ in axes}) != len(axes):
        raise ValueError("axes must use distinct names")
    if any(direction not in {"max", "min"} for _, direction in axes):
        raise ValueError("axis direction must be 'max' or 'min'")


def _complete(row: Mapping, axes: list[tuple[str, str]]) -> bool:
    return all(row.get(name) is not None for name, _ in axes)


def dominates(a: Mapping, b: Mapping, axes: list[tuple[str, str]]) -> bool:
    _validate_axes(axes)
    if not _complete(a, axes) or not _complete(b, axes):
        return False
    no_worse = all(
        (a[name] >= b[name]) if direction == "max" else (a[name] <= b[name])
        for name, direction in axes
    )
    strictly_better = any(
        (a[name] > b[name]) if direction == "max" else (a[name] < b[name])
        for name, direction in axes
    )
    return no_worse and strictly_better


def pareto_front(rows: list[dict], axes: list[tuple[str, str]]) -> list[dict]:
    _validate_axes(axes)
    return [
        row
        for index, row in enumerate(rows)
        if _complete(row, axes)
        and not any(index != other_index and dominates(other, row, axes) for other_index, other in enumerate(rows))
    ]