from modelcompass.normalize import fixed_scale, normalize_many


def test_fixed_scale_maps_bounds():
    assert fixed_scale(0, lower=0, upper=100) == 0.0
    assert fixed_scale(50, lower=0, upper=100) == 0.5
    assert fixed_scale(100, lower=0, upper=100) == 1.0


def test_fixed_scale_clamps_out_of_range():
    assert fixed_scale(-10, lower=0, upper=100) == 0.0
    assert fixed_scale(110, lower=0, upper=100) == 1.0


def test_missing_is_not_filled_with_zero():
    assert fixed_scale(None, lower=0, upper=100) is None
    assert normalize_many([0, None, 100], lower=0, upper=100) == [0.0, None, 1.0]