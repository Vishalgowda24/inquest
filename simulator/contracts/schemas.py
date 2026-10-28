"""Strict version-1 export schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExportModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal["1.0"] = "1.0"


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must include a timezone")
    return value


class MetricPoint(ExportModel):
    id: str = Field(min_length=1)
    timestamp: datetime
    service: str = Field(min_length=1)
    metric: Literal["request_rate", "latency_ms", "error_rate", "cpu_percent", "memory_mb"]
    value: float
    unit: str
    dimensions: dict[str, str] = Field(default_factory=dict)
    timestamp_uncertainty_ms: int = Field(ge=0)

    _timestamp_utc = field_validator("timestamp")(_utc)


class Span(ExportModel):
    trace_id: str = Field(min_length=1)
    span_id: str = Field(min_length=1)
    parent_span_id: str | None = None
    service: str = Field(min_length=1)
    operation: str = Field(min_length=1)
    start_time: datetime
    duration_ms: float = Field(ge=0)
    status: Literal["OK", "ERROR"]
    attributes: dict[str, str | float | int | bool] = Field(default_factory=dict)
    timestamp_uncertainty_ms: int = Field(ge=0)

    _timestamp_utc = field_validator("start_time")(_utc)


class LogEvent(ExportModel):
    id: str = Field(min_length=1)
    timestamp: datetime
    service: str = Field(min_length=1)
    level: Literal["DEBUG", "INFO", "WARN", "ERROR"]
    message: str = Field(min_length=1)
    trace_id: str | None = None
    attributes: dict[str, str | float | int | bool] = Field(default_factory=dict)
    timestamp_uncertainty_ms: int = Field(ge=0)

    _timestamp_utc = field_validator("timestamp")(_utc)


class ChangeEvent(ExportModel):
    id: str = Field(min_length=1)
    kind: Literal["deployment", "configuration_change", "restart"]
    timestamp: datetime
    service: str = Field(min_length=1)
    change_id: str = Field(min_length=1)
    details: dict[str, str | float | int | bool]
    timestamp_uncertainty_ms: int = Field(ge=0)

    _timestamp_utc = field_validator("timestamp")(_utc)


class DependencyEdge(ExportModel):
    id: str = Field(min_length=1)
    caller: str = Field(min_length=1)
    callee: str = Field(min_length=1)


class TimeRange(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    start: datetime
    end: datetime

    _timestamps_utc = field_validator("start", "end")(_utc)


class ScenarioManifest(ExportModel):
    scenario_id: str = Field(pattern=r"^scn_[a-f0-9]{12}$")
    seed: int = Field(ge=0)
    source: Literal["synthetic", "otel", "real"] = "synthetic"
    synthetic: Literal[True] = True
    time_range: TimeRange
    services: list[str] = Field(min_length=1)
    record_counts: dict[str, int]
    files: list[str]
