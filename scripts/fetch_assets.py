"""Fetch static media assets for Inquest demo hero."""

from __future__ import annotations

import os
import urllib.request
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parents[1] / "demo" / "static" / "assets"

ASSETS = {
    "hero_loop.mp4": "https://d2ol7oe51mr4n9.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/435a4fe7-e43b-4e7c-af78-0be083e73569.mp4",
    "hero_poster.webp": "https://d2ol7oe51mr4n9.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/782a4a52-4c1e-4471-bb0c-aa232927f4a6.webp",
}


def fetch_assets() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for filename, url in ASSETS.items():
        dest = ASSETS_DIR / filename
        if dest.exists() and dest.stat().st_size > 0:
            print(f"Asset already present: {filename} ({dest.stat().st_size} bytes)")
            continue
        print(f"Downloading {filename} from {url}...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "InquestAssetFetcher/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp, open(dest, "wb") as f:
                f.write(resp.read())
            print(f"Downloaded {filename}: {dest.stat().st_size} bytes")
        except Exception as exc:
            print(f"Warning: failed to download {filename}: {exc}")


if __name__ == "__main__":
    fetch_assets()
