from modelcompass.normalize import fixed_scale


def test_fixed_scale_and_missing():
    assert fixed_scale(50, lower=0, upper=100) == 0.5
    assert fixed_scale(None) is None