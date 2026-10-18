from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SourceType(StrEnum):
    OFFICIAL = "official"
    THIRD_PARTY = "third_party"
    MANUAL = "manual"


class ConfidenceLevel(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ModelIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    canonical_id: str = Field(min_length=1)
    provider_family: str = Field(min_length=1)
    model_name: str = Field(min_length=1)


class ModelVariant(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    variant_id: str = Field(min_length=1)
    canonical_model_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    reasoning_mode: str = Field(min_length=1)
    modality: str = Field(min_length=1)
    context_window: int | None = Field(default=None, gt=0)


class Deployment(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    deployment_id: str = Field(min_length=1)
    model_variant_id: str = Field(min_length=1)
    channel: str = Field(min_length=1)
    api_format: str = Field(min_length=1)
    availability: str = Field(min_length=1)


class SourcedObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    model_variant_id: str = Field(min_length=1)
    observed_at: date
    source_url: str
    source_type: SourceType = SourceType.THIRD_PARTY
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM

    @field_validator("source_url")
    @classmethod
    def valid_http_url(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("source_url must be an absolute http(s) URL")
        return value


class BenchmarkObservation(SourcedObservation):
    benchmark_id: str = Field(min_length=1)
    ability_cluster: str = Field(min_length=1)
    score: float
    score_unit: str = Field(min_length=1)
    reported_at: date
    reproducibility: ConfidenceLevel = ConfidenceLevel.MEDIUM
    notes: str | None = None


class PriceObservation(SourcedObservation):
    input_price_usd_per_million: float | None = Field(default=None, ge=0)
    output_price_usd_per_million: float | None = Field(default=None, ge=0)
    cached_input_price_usd_per_million: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def has_a_price(self) -> "PriceObservation":
        if all(value is None for value in (self.input_price_usd_per_million, self.output_price_usd_per_million, self.cached_input_price_usd_per_million)):
            raise ValueError("at least one price must be supplied")
        return self


class CapabilityObservation(SourcedObservation):
    context_window: int | None = Field(default=None, gt=0)
    tool_calling: bool | None = None
    web_search: bool | None = None
    mcp: bool | None = None
    vision: bool | None = None
    structured_output: bool | None = None


class PublicTaskCostObservation(SourcedObservation):
    task_definition: str = Field(min_length=1)
    cost_usd: float = Field(ge=0)
    source_snapshot_id: str = Field(min_length=1)


class ScenarioConstraints(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    min_confidence: float = Field(default=0.55, ge=0, le=1)
    require_tool_calling: bool = False
    require_vision: bool = False
    min_context_window: int | None = Field(default=None, gt=0)


class ScenarioProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    weights: dict[str, float]
    constraints: ScenarioConstraints = Field(default_factory=ScenarioConstraints)

    @field_validator("weights")
    @classmethod
    def valid_weights(cls, value: dict[str, float]) -> dict[str, float]:
        if not value or any(weight < 0 for weight in value.values()) or sum(value.values()) <= 0:
            raise ValueError("weights must be non-empty, non-negative, and have a positive sum")
        return value


class SourceSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    source_id: str = Field(min_length=1)
    fetched_at: datetime
    source_url: str
    content_hash: str = Field(min_length=1)
    parser_version: str = Field(min_length=1)
    status: str = Field(min_length=1)
    issues: list[str] = Field(default_factory=list)

    @field_validator("source_url")
    @classmethod
    def valid_http_url(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("source_url must be an absolute http(s) URL")
        return value