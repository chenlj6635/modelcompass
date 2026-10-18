from modelcompass.pareto import dominates, pareto_front


def test_two_axis_pareto():
    axes = [("quality", "max"), ("cost", "min")]
    a = {"id": "a", "quality": 0.9, "cost": 2}
    b = {"id": "b", "quality": 0.8, "cost": 3}
    assert dominates(a, b, axes)
    assert [x["id"] for x in pareto_front([a, b], axes)] == ["a"]


def test_unknown_does_not_dominate():
    assert not dominates({"quality": 1, "cost": None}, {"quality": 0, "cost": 1}, [("quality", "max"), ("cost", "min")])