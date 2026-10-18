# Contributing to ModelCompass

Keep changes focused and preserve the public data contracts. Do not add benchmark values without a source URL, observation date, model variant, and license/reproducibility notes.

Run the focused tests before submitting a change:

```text
python -m pytest
```

Do not modify cc-switch in this repository during M0/M1. Changes to shared contracts require an explicit update to `docs/contracts.md` and a handoff note.