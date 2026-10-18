from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable


def aggregate_clusters(observations: Iterable[dict], *, weights: dict[str, float] | None = None) -> dict[str, float | None]:
    totals: dict[str, float] = defaultdict(float)
    denominators: dict[str, float] = defaultdict(float)
    weights = weights or {}
    for item in observations:
        score = item.get("normalized_score")
        cluster = item.get("ability_cluster")
        if score is None or not cluster:
            continue
        weight = float(weights.get(item.get("benchmark_id"), 1.0))
        if weight <= 0:
            continue
        totals[cluster] += float(score) * weight
        denominators[cluster] += weight
    return {cluster: totals[cluster] / denominators[cluster] for cluster in totals}