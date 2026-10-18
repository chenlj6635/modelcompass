from __future__ import annotations


def dominates(a: dict, b: dict, axes: list[tuple[str, str]]) -> bool:
    if not axes or len(axes) not in {2, 3}:
        raise ValueError("axes must contain 2 or 3 dimensions")
    if any(direction not in {"min", "max"} for _, direction in axes):
        raise ValueError("axis direction must be min or max")
    if any(a.get(name) is None or b.get(name) is None for name, _ in axes):
        return False
    no_worse = all((a[name] >= b[name]) if direction == "max" else (a[name] <= b[name]) for name, direction in axes)
    strictly_better = any((a[name] > b[name]) if direction == "max" else (a[name] < b[name]) for name, direction in axes)
    return no_worse and strictly_better


def pareto_front(rows: list[dict], axes: list[tuple[str, str]]) -> list[dict]:
    complete = [row for row in rows if all(row.get(name) is not None for name, _ in axes)]
    return [row for i, row in enumerate(complete) if not any(j != i and dominates(other, row, axes) for j, other in enumerate(complete))]