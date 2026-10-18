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
    evidence: tuple[dict, ...] = ()
    rejected_reason: str | None = None


def score_scenario(model_variant_id: str, observations: list[dict], scenario_weights: dict[str, float], *, source: str = "third_party", freshness: float = 1.0, version: float = 1.0, constraints=None) -> ScenarioScore:
    if not model_variant_id:
        raise ValueError("model_variant_id is required")
    if not scenario_weights or any(weight < 0 for weight in scenario_weights.values()) or sum(scenario_weights.values()) <= 0:
        raise ValueError("scenario_weights must be non-empty, non-negative, and have a positive sum")
    has_variant_ids = any(item.get("model_variant_id") for item in observations)
    relevant = [item for item in observations if item.get("model_variant_id") == model_variant_id] if has_variant_ids else observations
    rejected_reason = None
    if constraints is not None and getattr(constraints, "require_tool_calling", False) and not any(item.get("tool_calling") is True for item in relevant):
        rejected_reason = "tool_calling required but not evidenced"
    clusters = aggregate_clusters(relevant)
    total_weight = sum(scenario_weights.values())
    present_weight = sum(scenario_weights.get(cluster, 0.0) for cluster in clusters)
    quality = None if present_weight == 0 else sum(scenario_weights[cluster] * score for cluster, score in clusters.items() if cluster in scenario_weights) / present_weight
    coverage = present_weight / total_weight
    scored = [item for item in relevant if item.get("normalized_score", item.get("score")) is not None]
    confidence_values = {"high": 1.0, "medium": 0.75, "low": 0.5}
    mean_confidence = sum(confidence_values.get(str(item.get("confidence", "medium")), 0.5) for item in scored) / len(scored) if scored else 0.0
    confidence = confidence_score(source=source, freshness=freshness, version=version, coverage=coverage * mean_confidence)
    missing = tuple(cluster for cluster in scenario_weights if cluster not in clusters)
    evidence = tuple({"model_variant_id": item.get("model_variant_id", model_variant_id), "benchmark_id": item.get("benchmark_id"), "ability_cluster": item.get("ability_cluster"), "score": item.get("score", item.get("normalized_score")), "score_unit": item.get("score_unit"), "source_url": item.get("source_url"), "observed_at": str(item.get("observed_at") or item.get("reported_at") or "")} for item in scored)
    return ScenarioScore(model_variant_id, quality, coverage, confidence, clusters, missing, evidence, rejected_reason)