from datetime import date
from modelcompass.confidence import confidence_score, freshness_score


def test_freshness_decays():
    assert freshness_score(date(2026, 10, 18), as_of=date(2026, 10, 18)) == 1
    assert 0 < freshness_score(date(2026, 4, 21), as_of=date(2026, 10, 18)) < 1


def test_confidence_is_independent_of_quality():
    assert confidence_score(source="official", freshness=1.0, version=1.0, coverage=1.0) == 1.0
    assert confidence_score(source="manual", freshness=1.0, version=1.0, coverage=1.0) < 1.0
    assert confidence_score(source="official", freshness=1.0, version=1.0, coverage=0.0) == 0.0