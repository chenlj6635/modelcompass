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


def score_scenario(model_variant_id: str, observations: list[dict], scenario_weights: dict[str, float]) -> ScenarioScore:
    clusters = aggregate_clusters(observations)
    total_weight = sum(scenario_weights.values())
    present_weight = sum(scenario_weights.get(k, 0.0) for k in clusters)
    quality = None if present_weight == 0 else sum(scenario_weights[k] * clusters[k] for k in clusters if k in scenario_weights) / present_weight
    coverage = 0.0 if total_weight == 0 else present_weight / total_weight
    confidences = [float(x.get("confidence_score", 1.0)) for x in observations if x.get("normalized_score") is not None]
    confidence = confidence_score(source="third_party", freshness=1.0, version=1.0, coverage=(sum(confidences) / len(confidences) if confidences else 0.0))
    missing = tuple(k for k in scenario_weights if k not in clusters)
    return ScenarioScore(model_variant_id, quality, coverage, confidence, clusters, missing)