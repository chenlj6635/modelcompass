from modelcompass.scoring import score_scenario
from modelcompass.schemas import BenchmarkObservation, ScenarioConstraints


def test_schema_observation_scores_end_to_end():
    obs = BenchmarkObservation(
        model_variant_id="gpt-x/2026-01/reasoning",
        observed_at="2026-10-01",
        source_url="https://example.org/bench",
        benchmark_id="swe",
        ability_cluster="software_engineering",
        score=72.0,
        score_unit="percent",
        reported_at="2026-10-01",
    ).model_dump(mode="json")
    result = score_scenario("gpt-x/2026-01/reasoning", [obs], {"software_engineering": 1.0})
    assert result.quality == 0.72
    assert result.coverage == 1.0
    assert result.evidence[0]["source_url"] == "https://example.org/bench"


def test_constraints_reject_missing_capability():
    result = score_scenario("m", [], {"general": 1.0}, constraints=ScenarioConstraints(require_tool_calling=True))
    assert result.rejected_reason == "tool_calling required but not evidenced"