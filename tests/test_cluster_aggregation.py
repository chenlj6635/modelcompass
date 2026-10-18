from modelcompass.clusters import aggregate_clusters


def test_cluster_weighted_average():
    result = aggregate_clusters([{"benchmark_id": "a", "ability_cluster": "reasoning", "normalized_score": 0.8}, {"benchmark_id": "b", "ability_cluster": "reasoning", "normalized_score": 0.6}], weights={"a": 2, "b": 1})
    assert result["reasoning"] == 0.7333333333333334