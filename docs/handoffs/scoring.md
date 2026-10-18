# Scoring Handoff

## Interfaces

- `fixed_scale(value, lower, upper)` and `normalize_many(...)` use an explicit fixed scale, clamp finite values to `[0, 1]`, and preserve `None` as missing.
- `aggregate_clusters(observations, weights=...)` computes weighted means by `ability_cluster`; missing scores and non-positive benchmark weights are excluded.
- `score_scenario(model_variant_id, observations, scenario_weights, source=..., freshness=..., version=...)` returns `ScenarioScore`. Quality is renormalized over observed scenario clusters, `coverage` is the observed scenario weight fraction, and `model_variant_id` is the primary key.
- `confidence_score(...)` combines source, freshness, version, and evidence coverage independently of quality. `freshness_score(...)` applies exponential half-life decay.
- `dominates(row_a, row_b, axes)` and `pareto_front(rows, axes)` support exactly 2 or 3 explicit `(name, max|min)` axes. Rows missing any selected axis are excluded from the front and cannot dominate.

## Tests

Run `python -m pytest`; the scoring suite covers fixed-scale normalization, missing values, cluster weighting, scenario reweighting and coverage, independent confidence, and 2D/3D Pareto behavior.

## Risks and dependencies

The scoring layer expects upstream observations to use normalized scores and the frozen schemas contract to use `model_variant_id`. Source freshness, version compatibility, and benchmark scale metadata must be supplied by ingestion; this layer does not infer them.

## Do not modify

Do not modify `src/modelcompass/schemas.py`, `config.py`, `cli.py`, `report.py`, templates, or `docs/contracts.md`.