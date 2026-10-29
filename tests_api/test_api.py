"""Comprehensive API and Security Test Suite for Inquest Demo."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from demo.api import ALLOWED_FAMILIES, RUN_STORE, app

client = TestClient(app)
ROOT_DIR = Path(__file__).resolve().parents[1]


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_families_endpoint():
    resp = client.get("/api/families")
    assert resp.status_code == 200
    families = resp.json().get("families", [])
    assert len(families) == 14
    assert families == ALLOWED_FAMILIES
    assert "clean_bad_deploy" in families
    assert "silent_cause" in families


def test_stats_matches_files():
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    stats = resp.json()

    # 1. Families count
    assert stats["families"] == len(ALLOWED_FAMILIES)

    # 2. Confirmation cases from eval/p9_confirmation_cases.json
    confirm_file = ROOT_DIR / "eval" / "p9_confirmation_cases.json"
    if confirm_file.exists():
        data = json.loads(confirm_file.read_text(encoding="utf-8"))
        assert stats["confirmation_cases"] == len(data.get("cases", []))

    # 3. Passing tests count >= 84
    assert stats["passing_tests"] >= 84


def test_results_endpoint():
    resp = client.get("/api/results")
    assert resp.status_code == 200
    data = resp.json()
    assert "results_md" in data
    assert "limitations_md" in data
    assert "948" in data["results_md"]
    assert "silent_cause" in data["limitations_md"]


def test_allow_list_rejection():
    # Attempt unknown / disallowed family
    resp = client.post("/api/run", json={"family": "unapproved_scenario", "seed": 1})
    assert resp.status_code == 400
    assert "allow-list" in resp.json().get("detail", "")


def test_seed_range_rejection():
    # Seed < 1
    resp = client.post("/api/run", json={"family": "clean_bad_deploy", "seed": 0})
    assert resp.status_code in (400, 422)

    # Negative seed
    resp = client.post("/api/run", json={"family": "clean_bad_deploy", "seed": -5})
    assert resp.status_code in (400, 422)

    # Seed > 10000
    resp = client.post("/api/run", json={"family": "clean_bad_deploy", "seed": 999999})
    assert resp.status_code in (400, 422)


def test_path_traversal_and_injection_attempts():
    # Path traversal in report URL
    resp = client.get("/api/report/../../etc/passwd")
    assert resp.status_code in (400, 404)

    # Injection string in family
    resp = client.post("/api/run", json={"family": "../clean_bad_deploy", "seed": 1})
    assert resp.status_code == 400

    resp = client.post("/api/run", json={"family": "clean_bad_deploy; cat /etc/passwd", "seed": 1})
    assert resp.status_code == 400

    resp = client.post("/api/run", json={"family": "<script>alert(1)</script>", "seed": 1})
    assert resp.status_code == 400


def test_oversize_body():
    # Create body larger than 1 MB (1,048,576 bytes)
    huge_payload = "a" * (1048576 + 1024)
    resp = client.post("/api/run", content=huge_payload, headers={"Content-Type": "application/json"})
    assert resp.status_code == 413
    assert "limit" in resp.json().get("error", "").lower()


def test_rate_limit_429():
    from demo.api import IP_REQUESTS
    IP_REQUESTS.clear()
    # Use x-test-rate-limit header to set limit to 3 for deterministic testing
    headers = {"X-Test-Rate-Limit": "3"}
    # First 3 should succeed
    for _ in range(3):
        r = client.get("/health", headers=headers)
        assert r.status_code == 200

    # 4th should return 429
    r = client.get("/health", headers=headers)
    assert r.status_code == 429
    assert "Retry-After" in r.headers
    assert "Rate limit exceeded" in r.json().get("error", "")


def test_security_headers_and_strict_csp():
    resp = client.get("/health")
    assert resp.status_code == 200
    headers = resp.headers

    # Strict CSP
    csp = headers.get("Content-Security-Policy", "")
    assert "default-src 'self'" in csp
    assert "media-src 'self' https://d2ol7oe51mr4n9.cloudfront.net" in csp
    assert "frame-ancestors 'none'" in csp

    # Security headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    # CORS off
    assert "Access-Control-Allow-Origin" not in headers


def test_basic_auth_protection(monkeypatch):
    # Enable basic auth via env
    monkeypatch.setenv("DEMO_BASIC_AUTH_USERNAME", "admin")
    monkeypatch.setenv("DEMO_BASIC_AUTH_PASSWORD", "secret123")

    # Unauthorized request to /api/families
    resp = client.get("/api/families")
    assert resp.status_code == 401
    assert "Basic" in resp.headers.get("WWW-Authenticate", "")

    # Authorized request with valid credentials
    resp = client.get("/api/families", auth=("admin", "secret123"))
    assert resp.status_code == 200
    assert len(resp.json()["families"]) == 14

    # /health remains accessible without auth
    resp = client.get("/health")
    assert resp.status_code == 200


def test_reveal_only_after_run():
    # Attempt reveal for nonexistent run
    resp = client.post("/api/reveal/nonexistent_run_id_99999")
    assert resp.status_code == 404
    assert "not found" in resp.json().get("detail", "").lower()

    # Precomputed run can be revealed
    r_run = client.post("/api/run", json={"family": "clean_bad_deploy", "seed": 1})
    assert r_run.status_code == 200
    run_id = r_run.json()["run_id"]

    resp = client.post(f"/api/reveal/{run_id}")
    assert resp.status_code == 200
    rev = resp.json()
    assert rev["true_cause"] == ["database"]
    assert rev["top_1_candidate"] == "database"
    assert rev["top_1_correct"] is True


def test_cached_vs_live_ranking_consistency():
    # 1. Fetch precomputed/cached result for clean_bad_deploy seed 1
    resp_cached = client.post("/api/run", json={"family": "clean_bad_deploy", "seed": 1})
    assert resp_cached.status_code == 200
    cached_data = resp_cached.json()
    assert cached_data["cached"] is True
    cached_top1 = cached_data["report"]["top_candidates"][0]["target"]

    # 2. Execute live pipeline for clean_bad_deploy seed 1
    from demo.api import _execute_pipeline_live
    live_result = _execute_pipeline_live("clean_bad_deploy", 1)
    live_top1 = live_result["report_json"]["top_candidates"][0]["target"]

    # Compare top-1 target
    assert cached_top1 == live_top1 == "database"
    assert cached_data["report"]["headline"]["confidence"]["level"] == live_result["report_json"]["headline"]["confidence"]["level"]


def test_timeout_handling():
    # Test timeout handling in POST /api/run when pipeline exceeds 60s
    async def fake_slow_execute(*args, **kwargs):
        await asyncio.sleep(0.2)

    with patch("demo.api._execute_pipeline_live", side_effect=asyncio.TimeoutError()):
        # Mock wait_for to raise TimeoutError
        with patch("asyncio.wait_for", side_effect=asyncio.TimeoutError()):
            # Use non-cached seed so it hits the live path
            resp = client.post("/api/run", json={"family": "clean_bad_deploy", "seed": 999})
            assert resp.status_code == 504
            assert "timed out" in resp.json().get("detail", "").lower()


def test_wording_lint():
    # Check that report headlines say 'Most likely', never 'caused by' or 'proves'
    resp = client.post("/api/run", json={"family": "clean_bad_deploy", "seed": 1})
    assert resp.status_code == 200
    report_md = resp.json().get("report_md", "")
    report_json = resp.json().get("report", {})

    headline_text = report_json.get("headline", {}).get("reason", "") + report_md
    assert "caused by" not in headline_text.lower()
    assert "proves" not in headline_text.lower()
    assert "most likely" in report_md.lower()

    # Footer verification
    footer_text = report_json.get("footer", {}).get("text", "")
    assert "synthetic scenarios only" in footer_text.lower() or "simulated incidents only" in footer_text.lower()


def test_concurrent_load_test():
    # 20 concurrent requests to cached endpoints without error
    import concurrent.futures
    from demo.api import IP_REQUESTS
    IP_REQUESTS.clear()

    def fetch(_):
        headers = {"X-Test-Rate-Limit": "100"}
        r = client.post("/api/run", json={"family": "clean_bad_deploy", "seed": 1}, headers=headers)
        return r.status_code == 200 and r.json().get("cached") is True

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(fetch, range(20)))

    assert all(results)
    assert len(results) == 20

