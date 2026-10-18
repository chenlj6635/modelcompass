# Schemas Handoff

## Completed

Implemented Pydantic contracts for model identity, model variants, optional deployments, sourced benchmark/price/capability observations, public Cost per Task, scenario profiles, and source snapshots. Model version and reasoning mode are explicit fields on `ModelVariant`; missing observations remain absent rather than becoming zero.

## Files

- `src/modelcompass/schemas.py`
- `tests/test_schema_validation.py`
- `docs/handoffs/schemas.md`

## Public Interfaces

Scoring and report agents should import the named classes from `modelcompass.schemas`. Use `model_variant_id` as the primary scoring key. `Deployment` is auxiliary metadata.

## Verification

`python -m pytest` -> 7 passed.

## Risks and Dependencies

External-source parsers and final AA field mappings remain source-specific and require license review.

## Do Not Modify

Do not modify scoring, report, CLI, templates, or `docs/contracts.md` without the coordinating agent.