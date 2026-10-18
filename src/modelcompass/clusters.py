from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable


def aggregate_clusters(observations: Iterable[dict], *, weights: dict[str, float] | None = None) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    denominators: dict[str, float] = defaultdict(float)
    seen: set[tuple[str, str, str]] = set()
    weights = weights or {}
    for item in observations:
        score = item.get("normalized_score")
        if score is None and item.get("score") is not None:
            score = item["score"] / 100 if item.get("score_unit") in {"percent", "%"} else item["score"]
        cluster = item.get("ability_cluster")
        benchmark = item.get("benchmark_id")
        key = (str(item.get("model_variant_id", "")), str(benchmark), str(item.get("reported_at", item.get("observed_at", ""))))
        if score is None or not cluster or key in seen:
            continue
        seen.add(key)
        weight = float(weights.get(benchmark, 1.0))
        if weight <= 0:
            continue
        totals[cluster] += float(score) * weight
        denominators[cluster] += weight
    return {cluster: totals[cluster] / denominators[cluster] for cluster in totals}