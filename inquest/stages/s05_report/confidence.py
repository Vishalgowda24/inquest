"""Read-only confidence model scoring for S05."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

FEATURE_NAMES = (
    "v3_top1_top2_margin",
    "methods_top1_count",
    "s03_disagreement",
    "s04_verified",
    "s04_contested",
    "s04_insufficient_evidence",
    "s04_unsupported",
    "telemetry_gap",
)
LEVEL_CUTOFFS = {"high": 0.80, "medium": 0.60}


def canonical_target(candidate: dict[str, Any]) -> str:
    return str((candidate.get("service") or candidate.get("target")) if candidate.get("target_type") == "change" else candidate.get("target", ""))


def extract_features(s03: dict[str, Any], s04: dict[str, Any], s02: dict[str, Any], vault_ids: set[str]) -> tuple[list[float], dict[str, Any]]:
    """Return preregistered feature vector and its human-readable ingredients."""
    candidates = list(s03.get("candidates", []))
    top = candidates[0] if candidates else None
    target = canonical_target(top) if top else None
    top2_score = float(candidates[1].get("score", 0.0)) if len(candidates) > 1 else None
    top_score = float(top.get("score", 0.0)) if top else 0.0
    margin = max(0.0, top_score - top2_score) if top2_score is not None else 0.0
    method_results = list(s03.get("method_results", []))
    active_with_candidate: list[tuple[str, list[dict[str, Any]]]] = []
    first_place_count = 0
    for method in method_results:
        if method.get("status") == "DISABLED":
            continue
        ranked = [item for item in method.get("candidates", []) if item.get("evidence_ids") and set(item.get("evidence_ids", [])) <= vault_ids]
        ranked.sort(key=lambda item: (-float(item.get("score", 0.0)), item.get("target_type", "service"), item.get("target", "")))
        if ranked:
            active_with_candidate.append((str(method.get("method", "")), ranked))
            if target is not None and canonical_target(ranked[0]) == target:
                first_place_count += 1
    decisions = list(s04.get("decisions", []))
    decision = next((item for item in decisions if item.get("target") == target), None)
    status = decision.get("status") if decision else None
    status_features = [float(status == value) for value in ("verified", "contested", "insufficient_evidence", "unsupported")]
    context = s03.get("verification_context", {})
    gap_services = {str(item.get("service")) for item in context.get("coverage_gaps", []) if item.get("service")}
    gap_services.update(str(item) for item in context.get("telemetry_gaps", []))
    gap_services.update(str(item.get("service")) for item in s02.get("coverage_gaps", []) if item.get("service"))
    gap = bool(target and target in gap_services)
    features = [margin, float(first_place_count), float(s03.get("disagreement", 0.0)), *status_features, float(gap)]
    details = {"target": target, "margin": margin, "first_place_method_count": first_place_count,
               "methods_with_candidates": len(active_with_candidate), "disagreement": float(s03.get("disagreement", 0.0)),
               "s04_status": status, "telemetry_gap": gap, "status_features": status_features}
    return features, details


def load_model(path: Path, expected_sha256: str) -> tuple[dict[str, Any], str]:
    data = path.read_bytes()
    # Git may check out the JSON with CRLF on Windows although the committed
    # canonical JSON hash was computed over LF. Normalize only line endings;
    # whitespace/content changes still fail the pinned integrity check.
    canonical_data = data.replace(b"\r\n", b"\n")
    digest = hashlib.sha256(canonical_data).hexdigest()
    if not expected_sha256 or digest != expected_sha256:
        raise ValueError(f"Confidence model SHA-256 mismatch: expected {expected_sha256 or '<unset>'}, found {digest}")
    model = json.loads(canonical_data.decode("utf-8"))
    if model.get("version") != "confidence_logistic_v1" or tuple(model.get("feature_names", ())) != FEATURE_NAMES:
        raise ValueError("Confidence model version or feature order does not match this S05 implementation")
    if len(model.get("coefficients", [])) != len(FEATURE_NAMES) or len(model.get("mean", [])) != len(FEATURE_NAMES) or len(model.get("scale", [])) != len(FEATURE_NAMES):
        raise ValueError("Confidence model has an invalid coefficient or standardization vector")
    return model, digest


def _sigmoid(value: float) -> float:
    if value >= 0:
        return 1.0 / (1.0 + math.exp(-min(value, 700.0)))
    exp_value = math.exp(max(value, -700.0))
    return exp_value / (1.0 + exp_value)


def predict_probability(model: dict[str, Any], features: list[float], *, margin_only: bool = False) -> float:
    if margin_only:
        baseline = model["margin_baseline"]
        z = baseline["intercept"] + (features[0] - baseline["mean"]) / baseline["scale"] * baseline["coefficient"]
    else:
        z = float(model["intercept"])
        z += sum(((value - mean) / scale) * coefficient for value, mean, scale, coefficient in zip(features, model["mean"], model["scale"], model["coefficients"]))
    return _sigmoid(z)


def confidence_level(probability: float, *, telemetry_gap: bool, methods_with_candidates: int) -> str:
    if telemetry_gap or methods_with_candidates < 2:
        return "insufficient_evidence"
    if probability >= LEVEL_CUTOFFS["high"]:
        return "high"
    if probability >= LEVEL_CUTOFFS["medium"]:
        return "medium"
    return "low"
