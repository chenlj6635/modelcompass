# Data Contracts

The public scoring key is `model_variant_id`. `ModelVariant` represents a canonical model identity plus an explicit version and reasoning mode. `Deployment` is optional provider/channel metadata and is not the default scoring unit.

Required objects are defined in `src/modelcompass/schemas.py`:

- `ModelIdentity`: canonical family identity.
- `ModelVariant`: version, reasoning mode, modality, and context window.
- `Deployment`: optional channel and API metadata linked by `model_variant_id`.
- `BenchmarkObservation`: sourced score with benchmark, ability cluster, date, and variant.
- `PriceObservation`: sourced official pricing; unknown prices remain absent.
- `CapabilityObservation`: sourced product capabilities.
- `PublicTaskCostObservation`: public Cost per Task value with task definition and snapshot.
- `ScenarioProfile`: visible ability-cluster weights and hard constraints.
- `SourceSnapshot`: fetch time, URL, hash, parser version, and status.

Scoring accepts observation dictionaries or validated model dumps. It normalizes `score` into `normalized_score` before cluster aggregation, filters observations by the requested `model_variant_id`, and never treats missing values as zero. A strict Pareto front excludes rows with an unknown selected axis.