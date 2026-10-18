from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .clusters import aggregate_clusters
from .confidence import confidence_score
from .schemas import ScenarioConstraints


@dataclass(frozen=True)
class ScenarioScore:
    model_variant_id: str
    quality: float | None
    coverage: float
    confidence: float
    cluster_scores: dict[str, float]
    missing_clusters: tuple[str, ...]
    rejected_reason: str | None = None
    evidence: tuple[dict, ...] = ()


def enforce_constraints(constraints: ScenarioConstraints, capabilities: list[dict]) -> str | None:
    rows = [item for item in capabilities if item.get("tool_calling") is not None or item.get("vision") is not None or item.get("context_window") is not None]
    if constraints.require_tool_calling and not any(item.get("tool_calling") is True for item in rows):
        return "tool_calling required but not evidenced"
    if constraints.require_vision and not any(item.get("vision") is True for item in rows):
        return "vision required but not evidenced"
    if constraints.min_context_window is not None and not any((item.get("context_window") or 0) >= constraints.min_context_window for item in rows):
        return f"context window >= {constraints.min_context_window} required but not evidenced"
    return None


def score_scenario(model_variant_id: str, observations: list[dict], scenario_weights: dict[str, float], *, constraints: ScenarioConstraints | None = None) -> ScenarioScore:
    has_variant_ids = any(item.get("model_variant_id") for item in observations)
    relevant = [item for item in observations if item.get("model_variant_id") == model_variant_id] if has_variant_ids else observations
    capabilities = [item for item in relevant if "tool_calling" in item or "vision" in item or "context_window" in item]
    rejected = enforce_constraints(constraints, capabilities) if constraints else None
    clusters = aggregate_clusters(relevant)
    total_weight = sum(scenario_weights.values())
    present_weight = sum(scenario_weights.get(k, 0.0) for k in clusters)
    quality = None if present_weight == 0 else sum(scenario_weights[k] * clusters[k] for k in clusters if k in scenario_weights) / present_weight
    coverage = 0.0 if total_weight == 0 else present_weight / total_weight
    scored = [item for item in relevant if item.get("normalized_score", item.get("score")) is not None]
    confidence_values = {"high": 1.0, "medium": 0.75, "low": 0.5}
    mean_confidence = sum(confidence_values.get(str(item.get("confidence", "medium")), float(item.get("confidence", 0.5)) if isinstance(item.get("confidence"), (int, float)) else 0.5) for item in scored) / len(scored) if scored else 0.0
    confidence = confidence_score(source="third_party", freshness=1.0, version=1.0, coverage=coverage * mean_confidence)
    evidence = tuple({
        "model_variant_id": item.get("model_variant_id"),
        "benchmark_id": item.get("benchmark_id"),
        "ability_cluster": item.get("ability_cluster"),
        "score": item.get("score", item.get("normalized_score")),
        "score_unit": item.get("score_unit"),
        "source_url": item.get("source_url"),
        "observed_at": str(item.get("observed_at") or item.get("reported_at") or ""),
    } for item in scored)
    missing = tuple(k for k in scenario_weights if k not in clusters)
    return ScenarioScore(model_variant_id, quality, coverage, confidence, clusters, missing, rejected, evidence)