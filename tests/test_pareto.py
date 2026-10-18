from modelcompass.pareto import dominates, pareto_front


def test_two_axis_pareto():
    axes = [("quality", "max"), ("cost", "min")]
    a = {"model_variant_id": "a", "quality": 0.9, "cost": 2}
    b = {"model_variant_id": "b", "quality": 0.8, "cost": 3}
    assert dominates(a, b, axes)
    assert [x["model_variant_id"] for x in pareto_front([a, b], axes)] == ["a"]


def test_three_axis_pareto():
    axes = [("quality", "max"), ("cost", "min"), ("latency", "min")]
    a = {"model_variant_id": "a", "quality": 0.9, "cost": 2, "latency": 1}
    b = {"model_variant_id": "b", "quality": 0.9, "cost": 2, "latency": 2}
    c = {"model_variant_id": "c", "quality": 0.7, "cost": 5, "latency": 3}
    assert dominates(a, b, axes)
    assert dominates(a, c, axes)
    assert [x["model_variant_id"] for x in pareto_front([a, b, c], axes)] == ["a"]


def test_unknown_values_do_not_dominate_or_enter_front():
    unknown = {"model_variant_id": "unknown", "quality": 1, "cost": None}
    complete = {"model_variant_id": "complete", "quality": 0, "cost": 1}
    axes = [("quality", "max"), ("cost", "min")]
    assert not dominates(unknown, complete, axes)
    assert [x["model_variant_id"] for x in pareto_front([unknown, complete], axes)] == ["complete"]