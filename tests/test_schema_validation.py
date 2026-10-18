from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from modelcompass.schemas import (
    BenchmarkObservation,
    ModelVariant,
    PriceObservation,
    PublicTaskCostObservation,
    ScenarioProfile,
    SourceSnapshot,
)


BASE = {
    "model_variant_id": "openai/gpt-6.1-sol@2026-10-01/reasoning-max",
    "observed_at": date(2026, 10, 18),
    "source_url": "https://example.org/source",
}


def test_model_variant_keeps_version_and_reasoning_mode() -> None:
    variant = ModelVariant(
        variant_id=BASE["model_variant_id"],
        canonical_model_id="openai/gpt-6.1-sol",
        version="2026-10-01",
        reasoning_mode="max",
        modality="text",
        context_window=1_000_000,
    )
    assert variant.reasoning_mode == "max"


def test_benchmark_requires_source_and_date() -> None:
    with pytest.raises(ValidationError):
        BenchmarkObservation(
            model_variant_id=BASE["model_variant_id"],
            benchmark_id="gpqa",
            ability_cluster="science_reasoning",
            score=0.7,
            score_unit="accuracy",
            reported_at=date(2026, 10, 18),
        )


def test_price_does_not_accept_all_unknown_values() -> None:
    with pytest.raises(ValidationError):
        PriceObservation(**BASE)


def test_missing_task_cost_is_not_zero() -> None:
    cost = PublicTaskCostObservation(**BASE, task_definition="aa-v1", cost_usd=0.0, source_snapshot_id="aa-1")
    assert cost.cost_usd == 0.0


def test_scenario_weights_need_positive_sum() -> None:
    with pytest.raises(ValidationError):
        ScenarioProfile(id="x", name="x", weights={"reasoning": 0})


def test_snapshot_has_hash_and_parser_version() -> None:
    snapshot = SourceSnapshot(
        source_id="aa",
        fetched_at=datetime(2026, 10, 18, tzinfo=timezone.utc),
        source_url="https://example.org",
        content_hash="sha256:abc",
        parser_version="0.1.0",
        status="success",
    )
    assert snapshot.status == "success"