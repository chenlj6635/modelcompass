# Report Handoff

Implemented report serialization and a minimal CLI. `write_report` emits self-contained HTML, JSON, and CSV; `render_html` renders the core summary fields. `modelcompass report --format html --output report.html` is the current command. `serve` is a placeholder pending Web integration.

Tests: `python -m pytest`.

Known limitation: report currently accepts rows directly and does not yet load full profile/snapshot files. The coordinating agent should integrate this with the frozen schemas and scoring APIs.