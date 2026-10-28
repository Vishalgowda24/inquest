"""Pydantic contracts for canonical data and stage boundaries."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: Literal["1.0"] = "1.0"


def _aware(value: datetime | None) -> datetime | None:
    if value is not None and (value.tzinfo is None or value.utcoffset() is None):
        raise ValueError("timestamp must include a timezone")
    return value


class MetricPoint(ContractModel):
    id: str = Field(min_length=1)
    timestamp: datetime
    service: str = Field(min_length=1)
    metric: str = Field(min_length=1)
    value: float
    unit: str
    dimensions: dict[str, str] = Field(default_factory=dict)
    timestamp_uncertainty_ms: int = Field(ge=0)
    source: str = "unknown"
    source_metadata: dict[str, object] = Field(default_factory=dict)

    _timestamp_aware = field_validator("timestamp")(_aware)


class Span(ContractModel):
    trace_id: str = Field(min_length=1)
    span_id: str = Field(min_length=1)
    parent_span_id: str | None = None
    service: str = Field(min_length=1)
    operation: str
    start_time: datetime
    duration_ms: float = Field(ge=0)
    status: str
    attributes: dict[str, object] = Field(default_factory=dict)
    timestamp_uncertainty_ms: int = Field(ge=0)
    source: str = "unknown"
    source_metadata: dict[str, object] = Field(default_factory=dict)

    _timestamp_aware = field_validator("start_time")(_aware)


class LogEvent(ContractModel):
    id: str = Field(min_length=1)
    timestamp: datetime | None
    service: str | None
    level: str
    message: str
    trace_id: str | None = None
    attributes: dict[str, object] = Field(default_factory=dict)
    timestamp_uncertainty_ms: int = Field(ge=0)
    source: str = "unknown"
    source_metadata: dict[str, object] = Field(default_factory=dict)

    _timestamp_aware = field_validator("timestamp")(_aware)


class ChangeEvent(ContractModel):
    id: str = Field(min_length=1)
    kind: str
    timestamp: datetime | None
    service: str | None
    change_id: str | None = None
    details: dict[str, object] = Field(default_factory=dict)
    timestamp_uncertainty_ms: int = Field(ge=0)
    source: str = "unknown"
    source_metadata: dict[str, object] = Field(default_factory=dict)

    _timestamp_aware = field_validator("timestamp")(_aware)


class DependencyEdge(ContractModel):
    id: str = Field(min_length=1)
    caller: str = Field(min_length=1)
    callee: str = Field(min_length=1)
    source: str = "unknown"
    source_metadata: dict[str, object] = Field(default_factory=dict)


class CanonicalTimeRange(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    start: datetime
    end: datetime

    _timestamps_aware = field_validator("start", "end")(_aware)


class ScenarioManifest(ContractModel):
    scenario_id: str = Field(pattern=r"^scn_[a-f0-9]{12}$")
    seed: int = Field(ge=0)
    source: Literal["synthetic", "otel", "real"]
    synthetic: bool
    time_range: CanonicalTimeRange
    services: list[str]
    record_counts: dict[str, int]
    files: list[str]
    source_metadata: dict[str, object] = Field(default_factory=dict)


class Evidence(ContractModel):
    id: str = Field(min_length=1)
    source: str
    timestamp: datetime | None
    timestamp_uncertainty_ms: int = Field(ge=0)
    payload: dict[str, object]
    source_reference: str | None = None
    quality_warnings: list[str] = Field(default_factory=list)

    _timestamp_aware = field_validator("timestamp")(_aware)


class Candidate(ContractModel):
    id: str
    target: str
    target_type: Literal["service", "change"]
    service: str | None = None
    method: str
    score: float = Field(ge=0)
    rationale: str = Field(min_length=1, max_length=240)
    evidence_ids: list[str] = Field(default_factory=list)
    method_scores: dict[str, float] = Field(default_factory=dict)


class CandidateMethodResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    method: str
    status: Literal["OK", "DEGRADED", "DISABLED"]
    candidates: list[Candidate] = Field(default_factory=list)
    note: str | None = None


class CandidateAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    candidates: list[Candidate] = Field(default_factory=list)
    per_method: dict[str, list[Candidate]] = Field(default_factory=dict)
    method_results: list[CandidateMethodResult] = Field(default_factory=list)
    disabled_methods: list[str] = Field(default_factory=list)
    disagreement: float = Field(ge=0, le=1)


class VerificationFinding(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    candidate_id: str
    target: str
    verdict: Literal["supports", "contradicts", "inconclusive"]
    effect_size: float = Field(ge=0, le=1)
    rationale: str = Field(min_length=1, max_length=240)
    evidence_ids: list[str] = Field(default_factory=list)


class VerificationMethodResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    method: str
    status: Literal["OK", "DEGRADED", "DISABLED"]
    findings: list[VerificationFinding] = Field(default_factory=list)
    note: str | None = None


class VerificationDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    candidate_id: str
    target: str
    status: Literal["verified", "contested", "insufficient_evidence", "unsupported"]
    confidence: float = Field(ge=0, le=1)
    s03_rank: int = Field(ge=1)
    s03_score: float
    method_scores: dict[str, float] = Field(default_factory=dict)
    s03_disagreement: float = Field(ge=0, le=1)
    rationale: str = Field(min_length=1, max_length=240)
    evidence_ids: list[str] = Field(default_factory=list)


class VerificationAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    decisions: list[VerificationDecision] = Field(default_factory=list)
    per_method: dict[str, list[VerificationFinding]] = Field(default_factory=dict)
    method_results: list[VerificationMethodResult] = Field(default_factory=list)
    disabled_methods: list[str] = Field(default_factory=list)
    disagreement: float = Field(ge=0, le=1)
    original_order: list[VerificationDecision] = Field(default_factory=list)
    reranked_order: list[VerificationDecision] = Field(default_factory=list)
    reranking_enabled: bool = False


class Hypothesis(ContractModel):
    id: str
    description: str
    verification_state: Literal["suspected", "supported", "confirmed"]
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contradicting_evidence_ids: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    verification_record_id: str | None = None


class QuarantinedRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    file_path: str
    record_index: int
    error: str
    raw_record: dict[str, object]


class IngestDiagnostics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    accepted_counts: dict[str, int] = Field(default_factory=dict)
    rejected_counts: dict[str, int] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    quarantined: list[QuarantinedRecord] = Field(default_factory=list)
    input_files: list[str] = Field(default_factory=list)


class CanonicalBundle(ContractModel):
    manifest: ScenarioManifest
    metrics: list[MetricPoint] = Field(default_factory=list)
    spans: list[Span] = Field(default_factory=list)
    logs: list[LogEvent] = Field(default_factory=list)
    changes: list[ChangeEvent] = Field(default_factory=list)
    dependencies: list[DependencyEdge] = Field(default_factory=list)
    diagnostics: IngestDiagnostics = Field(default_factory=IngestDiagnostics)


class CoverageGap(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    service: str
    metric: str
    missing_windows: int = Field(ge=1)
    before: datetime
    after: datetime


class SignalOnset(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    service: str
    metric: str
    onset_time: datetime
    confidence: float = Field(ge=0, le=1)
    baseline_median: float
    baseline_mad: float
    timestamp_uncertainty_ms: int = Field(ge=0)
    detector: str


class SignalAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    detector: str
    onsets: list[SignalOnset]
    service_order: list[str]
    coverage_gaps: list[CoverageGap]
    warnings: list[str]


class VaultEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str
    source: str
    ts: datetime | None
    ts_uncertainty_ms: int = Field(ge=0)
    payload: dict[str, object]
    prev_hash: str
    hash: str


class VaultVerification(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    valid: bool
    items_checked: int
    item_id: str | None = None
    error: str | None = None


class StageStatus(StrEnum):
    OK = "OK"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"


class MissingInput(ContractModel):
    stage: str
    reason: str


class StageInput(ContractModel):
    stage: str
    payload: dict[str, object] = Field(default_factory=dict)
    missing_inputs: list[MissingInput] = Field(default_factory=list)


class StageResult(ContractModel):
    stage: str
    status: StageStatus
    output: dict[str, object] = Field(default_factory=dict)
    evidence_ids: list[str] = Field(default_factory=list)
    elapsed_ms: float = Field(ge=0)
    error_type: str | None = None
    error: str | None = None
    traceback: str | None = None


class Report(ContractModel):
    run_id: str
    scenario_id: str
    source: Literal["synthetic", "otel", "real"] = "real"
    synthetic: bool = False
    status: StageStatus
    stages: list[StageResult]
    failed_stages: list[str]
    degraded_stages: list[str]
    summary: str
