"""Robust baselines, optional seasonal normalization, CUSUM, and coverage gaps."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from statistics import median
from typing import Protocol

from inquest.contracts import CanonicalBundle, CoverageGap, MetricPoint, SignalAnalysis, SignalOnset


class ChangePointDetector(Protocol):
    name: str

    def detect(self, values: list[float], baseline_size: int, timestamps: list[datetime], start_index: int | None = None) -> int | None: ...


class CusumDetector:
    name = "cusum"

    def detect(self, values: list[float], baseline_size: int, timestamps: list[datetime], start_index: int | None = None) -> int | None:
        if len(values) < max(5, baseline_size + 2):
            return None
        differences = [right - left for left, right in zip(values, values[1:])]
        baseline = differences[:max(2, baseline_size - 1)]
        center = median(baseline)
        mad = median([abs(value - center) for value in baseline])
        level_scale = abs(median(values[:baseline_size])) * 0.02
        scale = max(1.4826 * mad, level_scale, 0.2)
        intervals = [(right - left).total_seconds() for left, right in zip(timestamps, timestamps[1:])]
        regular = [interval for interval in intervals if interval > 0]
        typical = median(regular) if regular else 0
        positive = negative = 0.0
        for index in range(max(baseline_size, start_index or baseline_size), len(values)):
            interval = intervals[index - 1]
            if typical and interval > typical * 1.5:
                positive = negative = 0.0
                elapsed_steps = max(1, round(interval / typical))
                residual = (differences[index - 1] - center * elapsed_steps) / (scale * elapsed_steps**0.5)
                if abs(residual) >= 5.0:
                    return index
                continue
            residual = (differences[index - 1] - center) / scale
            positive = max(0.0, positive + residual - 0.5)
            negative = min(0.0, negative + residual + 0.5)
            if positive >= 5.0 or negative <= -5.0:
                return index
        return None


def _detector() -> ChangePointDetector:
    try:
        import ruptures
    except ImportError:
        return CusumDetector()
    return _RupturesDetector(ruptures)


class _RupturesDetector:
    name = "ruptures"

    def __init__(self, module) -> None:
        self.module = module

    def detect(self, values: list[float], baseline_size: int, timestamps: list[datetime], start_index: int | None = None) -> int | None:
        if len(values) < 6:
            return None
        algorithm = self.module.Pelt(model="l2", min_size=3, jump=1).fit(values)
        floor = max(baseline_size, start_index or baseline_size)
        breaks = [point for point in algorithm.predict(pen=3) if floor <= point < len(values)]
        return min(breaks) if breaks else None


def analyze_signals(bundle: CanonicalBundle) -> SignalAnalysis:
    detector = _detector()
    groups = _group_metrics(bundle.metrics)
    onsets: list[SignalOnset] = []
    gaps: list[CoverageGap] = []
    warnings: list[str] = []
    seasonal_note_added = False
    for key, points in sorted(groups.items()):
        points.sort(key=lambda point: point.timestamp)
        gaps.extend(_coverage_gaps(key, points))
        values, seasonal = _normalized_values(points)
        if not seasonal and not seasonal_note_added:
            warnings.append("Seasonal normalization not applied: fewer than two complete daily cycles")
            seasonal_note_added = True
        onset = _onset(key, points, values, detector)
        if onset:
            onsets.append(onset)
    onsets.sort(key=lambda item: (item.onset_time, item.service, item.metric))
    service_order = _service_order(onsets)
    return SignalAnalysis(detector=detector.name, onsets=onsets, service_order=service_order, coverage_gaps=gaps, warnings=warnings)


def _group_metrics(metrics: list[MetricPoint]) -> dict[tuple[str, str], list[MetricPoint]]:
    groups: dict[tuple[str, str], list[MetricPoint]] = defaultdict(list)
    for point in metrics:
        groups[(point.service, point.metric)].append(point)
    return groups


def _normalized_values(points: list[MetricPoint]) -> tuple[list[float], bool]:
    values = [point.value for point in points]
    try:
        window_minutes = int(points[0].dimensions.get("window_minutes", "0"))
    except ValueError:
        return values, False
    period = 1440 // window_minutes if 0 < window_minutes <= 1440 else 0
    if period < 2 or len(values) < period * 2:
        return values, False
    phase_values: dict[int, list[float]] = defaultdict(list)
    window_seconds = window_minutes * 60
    elapsed = [(point.timestamp - points[0].timestamp).total_seconds() for point in points]
    if max(elapsed, default=0) + window_seconds < period * window_seconds * 2:
        return values, False
    for point, value in zip(points, values):
        phase = int(round((point.timestamp - points[0].timestamp).total_seconds() / window_seconds)) % period
        phase_values[phase].append(value)
    phases_with_two_cycles = sum(len(phase_values.get(phase, [])) >= 2 for phase in range(period))
    if phases_with_two_cycles < int(period * 0.9):
        return values, False
    center = median(values)
    seasonal = {phase: median(items) - center for phase, items in phase_values.items()}
    normalized = [value - seasonal[int(round((point.timestamp - points[0].timestamp).total_seconds() / window_seconds)) % period] for point, value in zip(points, values)]
    return normalized, True


def _onset(key: tuple[str, str], points: list[MetricPoint], values: list[float], detector: ChangePointDetector) -> SignalOnset | None:
    baseline_size = max(3, min(8, len(values) // 3))
    baseline = values[:baseline_size]
    center = median(baseline)
    mad = median([abs(value - center) for value in baseline])
    scale = max(1.4826 * mad, abs(center) * 0.005, 0.05)
    timestamps = [point.timestamp for point in points]
    start_index = baseline_size
    while start_index < len(values):
        index = detector.detect(values, baseline_size, timestamps, start_index)
        if index is None or index >= len(points):
            return None
        effect = abs(median(values[index:min(len(values), index + 3)]) - center)
        confidence = min(0.99, effect / (effect + 3.0 * scale))
        if confidence >= 0.5:
            point = points[index]
            uncertainty = _onset_uncertainty(points, index)
            return SignalOnset(service=key[0], metric=key[1], onset_time=point.timestamp, confidence=confidence, baseline_median=center, baseline_mad=mad, timestamp_uncertainty_ms=uncertainty, detector=detector.name)
        start_index = index + 1
    return None


def _onset_uncertainty(points: list[MetricPoint], index: int) -> int:
    uncertainty = points[index].timestamp_uncertainty_ms
    if index == 0 or len(points) < 3:
        return uncertainty
    intervals = [(right.timestamp - left.timestamp).total_seconds() for left, right in zip(points, points[1:])]
    typical = median([value for value in intervals if value > 0])
    gap_ms = max(0, int((intervals[index - 1] - typical) * 1000))
    return uncertainty + gap_ms


def _coverage_gaps(key: tuple[str, str], points: list[MetricPoint]) -> list[CoverageGap]:
    if len(points) < 3:
        return []
    deltas = [(right.timestamp - left.timestamp).total_seconds() for left, right in zip(points, points[1:])]
    typical = median([delta for delta in deltas if delta > 0])
    if typical <= 0:
        return []
    gaps: list[CoverageGap] = []
    for left, right, delta in zip(points, points[1:], deltas):
        missing = round(delta / typical) - 1
        if missing > 0 and delta >= typical * 1.5:
            gaps.append(CoverageGap(service=key[0], metric=key[1], missing_windows=missing, before=left.timestamp, after=right.timestamp))
    return gaps


def _service_order(onsets: list[SignalOnset]) -> list[str]:
    earliest: dict[str, datetime] = {}
    for onset in onsets:
        earliest.setdefault(onset.service, onset.onset_time)
    return sorted(earliest, key=lambda service: (earliest[service], service))
