# Architecture

ModelCompass is a localhost-first Web application with explicit data snapshots:

```text
source adapters -> snapshots -> validation -> normalization -> scenario scoring
                                      -> Pareto selection -> Web/JSON/CSV/HTML outputs
```

The scoring unit is `ModelVariant` (model identity + version + reasoning mode). `Deployment` records provider/channel metadata separately. The first release uses public benchmark evidence and public Cost per Task observations; personal measurements and reliability are outside M0/M1.