"""Playwright E2E and visual acceptance tests for Inquest demo."""

from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest
import uvicorn
from playwright.sync_api import sync_playwright

from demo.api import app

PORT = 8124
BASE_URL = f"http://127.0.0.1:{PORT}"
SCREENSHOTS_DIR = Path(__file__).resolve().parents[1] / "docs" / "screenshots"


@pytest.fixture(scope="module", autouse=True)
def run_server():
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    server_started = threading.Event()

    config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="warning")
    server = uvicorn.Server(config)

    def _serve():
        server_started.set()
        server.run()

    t = threading.Thread(target=_serve, daemon=True)
    t.start()
    server_started.wait()

    # Wait for server ready
    import urllib.request
    ready = False
    for _ in range(50):
        try:
            with urllib.request.urlopen(f"{BASE_URL}/health", timeout=1) as resp:
                if resp.status == 200:
                    ready = True
                    break
        except Exception:
            time.sleep(0.1)

    assert ready, "Server failed to start for Playwright tests"
    yield
    server.should_exit = True


def test_hero_desktop_acceptance():
    """Assert hero acceptance check at 1440x900 by bounding boxes."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(f"{BASE_URL}/")
        page.wait_for_selector("#wordmark")
        page.wait_for_timeout(1000)  # let entrance animations finish

        # 1. Headline top-left
        hero_left = page.locator("#heroLeft").bounding_box()
        assert hero_left is not None
        assert hero_left["x"] <= 200, f"Headline x={hero_left['x']} expected <= 200"
        assert hero_left["y"] <= 260, f"Headline y={hero_left['y']} expected <= 260"

        # 2. First headline line ends before Benchmarking/Evaluation card
        first_line = page.locator(".headline-line").first.bounding_box()
        card_top = page.locator("#cardTop").bounding_box()
        assert first_line is not None and card_top is not None
        first_line_end = first_line["x"] + first_line["width"]
        assert first_line_end <= card_top["x"] + 50, f"First line end {first_line_end} exceeds card top x {card_top['x']}"

        # 3. Cards overlap the artwork
        artwork = page.locator("#artworkContainer").bounding_box()
        card_bottom = page.locator("#cardBottom").bounding_box()
        assert artwork is not None and card_bottom is not None

        # Check horizontal and vertical overlap with artwork
        def overlaps(box1, box2):
            return not (
                box1["x"] + box1["width"] < box2["x"] or
                box2["x"] + box2["width"] < box1["x"] or
                box1["y"] + box1["height"] < box2["y"] or
                box2["y"] + box2["height"] < box1["y"]
            )
        assert overlaps(card_top, artwork), "Card top should overlap artwork"
        assert overlaps(card_bottom, artwork), "Card bottom should overlap artwork"

        # 4. Logo row centered at the bottom
        logo_row = page.locator("#logoRow").bounding_box()
        assert logo_row is not None
        assert logo_row["y"] >= 750, f"Logo row y={logo_row['y']} expected >= 750"

        # 5. No horizontal scroll
        no_scroll = page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth")
        assert no_scroll, "Page has horizontal scroll"

        # Screenshot
        page.screenshot(path=str(SCREENSHOTS_DIR / "hero_desktop_1440x900.png"))
        browser.close()


def test_hero_mobile_responsive():
    """Assert 390x844 single column with no horizontal overflow and working menu button."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 390, "height": 844})
        page.goto(f"{BASE_URL}/")
        page.wait_for_selector("#wordmark")

        # 1. No horizontal overflow
        no_overflow = page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth")
        assert no_overflow, "Mobile view has horizontal overflow"

        # 2. Working menu button
        menu_btn = page.locator("#mobileMenuBtn")
        assert menu_btn.is_visible()
        dropdown = page.locator("#mobileDropdown")
        assert not dropdown.is_visible()

        # Toggle menu open
        menu_btn.click()
        assert dropdown.is_visible()

        # Toggle menu close
        menu_btn.click()
        assert not dropdown.is_visible()

        # Screenshot
        page.screenshot(path=str(SCREENSHOTS_DIR / "hero_mobile_390x844.png"))
        browser.close()


def test_prefers_reduced_motion():
    """Assert prefers-reduced-motion shows the still and disables video loop."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(reduced_motion="reduce", viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.goto(f"{BASE_URL}/")
        page.wait_for_selector("#wordmark")

        still = page.locator("#artworkStill")
        assert still.is_visible(), "Poster still should be visible under reduced motion"

        video = page.locator("#artworkVideo")
        assert not video.is_visible(), "Video loop should be hidden under reduced motion"

        page.screenshot(path=str(SCREENSHOTS_DIR / "hero_reduced_motion.png"))
        browser.close()


def test_demo_flow_end_to_end():
    """Assert demo flow end to end including investigation run and Reveal answer."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(f"{BASE_URL}/demo")
        page.wait_for_selector("#headlineTarget")
        page.wait_for_timeout(500)

        # 1. Verify headline text contains "Most likely"
        headline = page.locator("#headlineTarget").inner_text()
        assert "most likely" in headline.lower()

        # 2. Select preset for silent cause top-1 miss
        page.locator("button[data-family='silent_cause']").click()
        page.wait_for_timeout(600)

        # Verify flag badge
        badge = page.locator("#flagBadge").inner_text()
        assert "review" in badge.lower() or "recommended" in badge.lower()

        # 3. Click reveal button
        reveal_btn = page.locator("#revealBtn")
        assert reveal_btn.is_visible()
        reveal_btn.click()
        page.wait_for_timeout(600)

        # 4. Assert reveal box shows miss result
        reveal_box = page.locator("#revealBox")
        assert reveal_box.is_visible()
        truth_badge = page.locator("#truthBadge").inner_text()
        assert "miss" in truth_badge.lower() or "did not match" in truth_badge.lower()

        page.screenshot(path=str(SCREENSHOTS_DIR / "demo_flow_reveal.png"))
        browser.close()


def test_keyboard_navigation_and_contrast():
    """Assert basic keyboard tab navigation and color contrast check."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(f"{BASE_URL}/")
        page.wait_for_selector("#wordmark")

        # Tab through header elements
        page.keyboard.press("Tab")
        active_tag = page.evaluate("() => document.activeElement.tagName")
        assert active_tag.lower() in ("a", "button")

        # Basic contrast check: white text on dark background
        text_color = page.evaluate("() => window.getComputedStyle(document.body).color")
        bg_color = page.evaluate("() => window.getComputedStyle(document.body).backgroundColor")
        assert "255, 255, 255" in text_color or "#fff" in text_color
        assert "13, 12, 17" in bg_color or "#0d0c11" in bg_color

        browser.close()
