# Report Handoff

## Interfaces

- `modelcompass data validate --input bundle.json` validates known snapshot collections against the frozen Pydantic contracts.
- `modelcompass score --input bundle.json --scenario ID --output score.json` calls the existing `score_scenario` interface and emits quality, coverage, confidence, sources, costs, and warnings.
- `modelcompass pareto --input score.json --axes quality max --axes public_task_cost min --output pareto.json` calls the existing `pareto_front` interface.
- `modelcompass report --input rows.json --format json|csv|html --output report.*` exports rows; HTML is self-contained and offline-openable.
- `modelcompass serve --host 127.0.0.1 --port 8000` serves a localhost HTML report.

## Tests

Run `python -m pytest`. Coverage includes CLI validation, offline HTML, source and warning display, and JSON/CSV export.

## Risks and dependencies

The adapter expects the existing scoring and Pareto modules from the scoring worktree. Benchmark score units are only normalized for `accuracy`, `fraction`, `percent`, and `percentage`; unknown units remain excluded and produce warnings. Missing clusters and costs remain unknown; no missing value is converted to zero. `serve` uses the Python standard library.

## Prohibited changes

Do not modify `src/modelcompass/schemas.py`, `src/modelcompass/config.py`, the scoring kernel, or `docs/contracts.md`. This branch changes only the requested report files.