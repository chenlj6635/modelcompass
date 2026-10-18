from modelcompass.scoring import score_scenario


def test_score_renormalizes_present_weights():
    result = score_scenario(
        "model-a", [{"ability_cluster": "reasoning", "normalized_score": 0.8}],
        {"reasoning": 0.5, "math": 0.5},
    )
    assert result.model_variant_id == "model-a"
    assert result.quality == 0.8
    assert result.coverage == 0.5
    assert result.missing_clusters == ("math",)


def test_score_without_any_cluster_has_no_quality():
    result = score_scenario("model-b", [], {"reasoning": 1.0})
    assert result.model_variant_id == "model-b"
    assert result.quality is None
    assert result.coverage == 0.0
    assert result.missing_clusters == ("reasoning",)


def test_scenario_weights_define_coverage():
    result = score_scenario(
        "model-c",
        [
            {"ability_cluster": "reasoning", "normalized_score": 0.6},
            {"ability_cluster": "math", "normalized_score": 0.8},
        ],
        {"reasoning": 0.25, "math": 0.25, "coding": 0.5},
    )
    assert result.quality == 0.7
    assert result.coverage == 0.5
    assert result.missing_clusters == ("coding",)