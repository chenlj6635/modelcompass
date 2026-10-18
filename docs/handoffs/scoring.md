# Scoring Handoff

Scoring exposes `fixed_scale`, `aggregate_clusters`, `score_scenario`, `confidence_score`, `freshness_score`, `dominates`, and `pareto_front`. Pareto axes are 2 or 3 `(name, direction)` pairs where direction is `max` or `min`; rows with unknown axis values cannot dominate or enter a strict complete-data front. The primary key is `model_variant_id`.

Tests: `python -m pytest`.