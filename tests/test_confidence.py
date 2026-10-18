from datetime import date
from modelcompass.confidence import freshness_score


def test_freshness_decays():
    assert freshness_score(date(2026, 10, 18), as_of=date(2026, 10, 18)) == 1