from modelcompass.scoring import score_scenario


def test_score_renormalizes_present_weights():
    result = score_scenario("m", [{"ability_cluster": "reasoning", "normalized_score": 0.8}], {"reasoning": 0.5, "math": 0.5})
    assert result.quality == 0.8
    assert result.coverage == 0.5
    assert result.missing_clusters == ("math",)