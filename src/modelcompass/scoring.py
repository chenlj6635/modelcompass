from __future__ import annotations

from dataclasses import dataclass

from .clusters import aggregate_clusters
from .confidence import confidence_score


@dataclass(frozen=True)
class ScenarioScore:
    model_variant_id: str
    quality: float | None
    coverage: float
    confidence: float
    cluster_scores: dict[str, float]
    missing_clusters: tuple[str, ...]


def score_scenario(
    model_variant_id: str,
    observations: list[dict],
    scenario_weights: dict[str, float],
    *,
    source: str = "third_party",
    freshness: float = 1.0,
    version: float = 1.0,
) -> ScenarioScore:
    """Score one model variant while renormalizing only over observed clusters."""
    if not model_variant_id:
        raise ValueError("model_variant_id is required")
    if not scenario_weights or any(weight < 0 for weight in scenario_weights.values()):
        raise ValueError("scenario_weights must be non-empty and non-negative")
    total_weight = sum(scenario_weights.values())
    if total_weight <= 0:
        raise ValueError("scenario_weights must have a positive sum")

    clusters = aggregate_clusters(observations)
    present_weight = sum(scenario_weights.get(cluster, 0.0) for cluster in clusters)
    quality = (
        None
        if present_weight == 0
        else sum(scenario_weights[cluster] * score for cluster, score in clusters.items() if cluster in scenario_weights)
        / present_weight
    )
    coverage = present_weight / total_weight
    evidence_scores = [
        float(item["confidence_score"])
        for item in observations
        if item.get("normalized_score") is not None and item.get("confidence_score") is not None
    ]
    evidence_coverage = sum(evidence_scores) / len(evidence_scores) if evidence_scores else 0.0
    confidence = confidence_score(
        source=source,
        freshness=freshness,
        version=version,
        coverage=evidence_coverage if evidence_scores else coverage,
    )
    missing = tuple(cluster for cluster in scenario_weights if cluster not in clusters)
    return ScenarioScore(model_variant_id, quality, coverage, confidence, clusters, missing)