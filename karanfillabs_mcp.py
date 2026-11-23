#!/usr/bin/env python3
"""Official MCP Server for Karanfil Labs Visual DNA API (https://karanfillabs.com)."""

import mimetypes
import os
from pathlib import Path
from urllib.parse import urlparse

import httpx
from mcp.server.fastmcp import FastMCP

API_BASE = os.environ.get("KARANFIL_API_BASE", "https://api.karanfillabs.com").rstrip("/")
mcp = FastMCP("Karanfil Labs Visual DNA")


def _get_api_key() -> str:
    key = os.environ.get("KARANFIL_API_KEY", "").strip()
    if not key:
        raise ValueError(
            "KARANFIL_API_KEY environment variable is not set. "
            "Create a free account at https://karanfillabs.com/#portal to receive 50 free API test credits "
            "and your kl_live_... key."
        )
    return key


def _format_matches(data: dict, is_text_search: bool = False) -> str:
    matches = data.get("matches") or []
    latency = data.get("latency_ms", "N/A")
    quota_info = data.get("quota") or {}
    rem = quota_info.get("remaining_quota", "N/A")
    plan = quota_info.get("plan", "unknown")

    header = f"Engine Latency: {latency} ms | Plan: {plan} | Remaining Quota: {rem}"
    if not matches:
        return f"{header}\nNo matching scene found above the similarity threshold in the current indexed catalog."

    lines = [header, ""]
    top_conf = float(matches[0].get("confidence") or 0.0)
    if not is_text_search and top_conf < 0.80:
        lines.append(
            "NOTE: Top match confidence is below 80%. "
            "The exact movie or series may not be indexed in the catalog yet (closest visual neighbors shown)."
        )
        lines.append("")

    for idx, m in enumerate(matches, start=1):
        title = m.get("title", "Unknown")
        year = f" ({m['year']})" if m.get("year") else ""
        mtype = m.get("media_type", "movie")
        ep = f" • {m['episode']}" if m.get("episode") else ""
        tmdb = f" | TMDB #{m['tmdb_id']}" if m.get("tmdb_id") else ""
        conf = float(m.get("confidence") or 0.0) * 100.0
        lines.append(f"{idx}. {title}{year} [{mtype}{ep}] — {conf:.1f}%{tmdb}")

    return "\n".join(lines)


@mcp.tool()
def identify_scene_from_image(
    image_source: str,
    top_k: int = 3,
    min_score: float = 0.70,
) -> str:
    """Identify a movie or TV series episode from a local video frame file path or direct image URL.

    Args:
        image_source: Local image path (PNG, JPG, WEBP) or direct http/https image URL.
        top_k: Number of closest scene candidates to return (1 to 10, default 3).
        min_score: Minimum cosine similarity threshold between 0.0 and 1.0 (default 0.70; 0.82+ recommended for strict matching).
    """
    api_key = _get_api_key()
    top_k = max(1, min(10, int(top_k)))
    min_score = max(0.0, min(1.0, float(min_score)))

    src = image_source.strip()
    if src.startswith(("http://", "https://")):
        with httpx.Client(timeout=20.0, follow_redirects=True) as dl:
            img_resp = dl.get(src)
            img_resp.raise_for_status()
            raw_bytes = img_resp.content
            parsed_name = Path(urlparse(src).path).name or "frame.jpg"
            mime = img_resp.headers.get("content-type", "").split(";")[0].strip() or "image/jpeg"
    else:
        file_path = Path(src).expanduser().resolve()
        if not file_path.is_file():
            return f"Error: Image file not found at '{file_path}'."
        raw_bytes = file_path.read_bytes()
        parsed_name = file_path.name
        mime = mimetypes.guess_type(parsed_name)[0] or "image/jpeg"

    if len(raw_bytes) > 12 * 1024 * 1024:
        return "Error: Image exceeds 12 MB size limit. Please resize or compress the frame."

    with httpx.Client(timeout=30.0) as client:
        resp = client.post(
            f"{API_BASE}/v1/identify",
            headers={"X-API-Key": api_key},
            params={"top_k": top_k, "min_score": min_score},
            files={"file": (parsed_name, raw_bytes, mime)},
        )

    if resp.status_code != 200:
        return f"API Error ({resp.status_code}): {resp.text}"

    return _format_matches(resp.json(), is_text_search=False)


@mcp.tool()
def search_scenes_by_text(
    query: str,
    top_k: int = 5,
    min_score: float = 0.22,
) -> str:
    """Search millions of cinema and TV frames using an English natural-language scene description.

    Args:
        query: English scene description (e.g. 'car chase in rainy neon street'). Translate non-English prompts to English before calling.
        top_k: Number of closest matching scenes to return (1 to 10, default 5).
        min_score: Minimum text-to-image similarity threshold (0.0 to 1.0, default 0.22).
    """
    api_key = _get_api_key()
    clean_query = query.strip()
    if not clean_query:
        return "Error: Scene query cannot be empty."

    top_k = max(1, min(10, int(top_k)))
    min_score = max(0.0, min(1.0, float(min_score)))

    with httpx.Client(timeout=30.0) as client:
        resp = client.post(
            f"{API_BASE}/v1/search",
            headers={"X-API-Key": api_key, "Content-Type": "application/json"},
            json={"query": clean_query, "top_k": top_k, "min_score": min_score},
        )

    if resp.status_code != 200:
        return f"API Error ({resp.status_code}): {resp.text}"

    return _format_matches(resp.json(), is_text_search=True)


@mcp.tool()
def check_visual_dna_status() -> str:
    """Check Karanfil Labs Visual DNA API server health and live indexed 768-d frame vector count (no API key required)."""
    with httpx.Client(timeout=15.0) as client:
        resp = client.get(f"{API_BASE}/health")
    if resp.status_code != 200:
        return f"Health check returned HTTP {resp.status_code}: {resp.text}"
    return resp.text


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
