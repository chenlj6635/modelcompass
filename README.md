# ModelCompass

ModelCompass is a local Web tool for choosing models by personal task scenario. It combines public benchmark evidence, official model metadata, public Cost per Task observations, scenario weights, and user-selected 2D/3D Pareto views.

## Scope

The first milestone implements the M0/M1 foundation: data contracts, validation, scenario scoring, missing-data warnings, confidence, Pareto analysis, a localhost Web service, and JSON/CSV/HTML report export. Model versions and reasoning modes are separate `ModelVariant` objects. Provider deployments are optional attached metadata, not the default ranking unit.

The first release does not collect personal call logs, rank reliability, modify cc-switch, or submit a cc-switch PR.

## Development

```powershell
python -m pip install -e ".[test,web]"
python -m pytest
modelcompass serve --host 127.0.0.1 --port 8000
```

The design source is maintained in `docs/design.md`; contracts are frozen in `docs/contracts.md` after schema review.