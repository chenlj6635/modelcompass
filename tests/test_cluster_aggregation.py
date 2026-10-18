from modelcompass.clusters import aggregate_clusters


def test_cluster_weighted_average():
    result = aggregate_clusters(
        [
            {"benchmark_id": "a", "ability_cluster": "reasoning", "normalized_score": 0.8},
            {"benchmark_id": "b", "ability_cluster": "reasoning", "normalized_score": 0.6},
        ],
        weights={"a": 2, "b": 1},
    )
    assert result["reasoning"] == 0.7333333333333334


def test_missing_scores_are_excluded_not_zero():
    result = aggregate_clusters(
        [
            {"benchmark_id": "a", "ability_cluster": "reasoning", "normalized_score": None},
            {"benchmark_id": "b", "ability_cluster": "reasoning", "normalized_score": 0.4},
        ]
    )
    assert result == {"reasoning": 0.4}


def test_zero_weight_benchmarks_are_excluded():
    result = aggregate_clusters(
        [
            {"benchmark_id": "a", "ability_cluster": "reasoning", "normalized_score": 1.0},
            {"benchmark_id": "b", "ability_cluster": "reasoning", "normalized_score": 0.0},
        ],
        weights={"a": 0, "b": 1},
    )
    assert result == {"reasoning": 0.0}