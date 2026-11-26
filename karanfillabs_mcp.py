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


import json as _json
import re as _re
from typing import Optional as _Optional

_HEX_RE = _re.compile(r"^#?[0-9A-Fa-f]{6}$")


@mcp.tool()
def search_cinematography_palette(
    target_hex: _Optional[str] = None,
    color_tolerance: float = 22.0,
    lighting_style: _Optional[str] = None,
    shot_scale: _Optional[str] = None,
    color_harmony: _Optional[str] = None,
    min_symmetry: _Optional[float] = None,
    min_aspect_ratio: _Optional[float] = None,
    max_aspect_ratio: _Optional[float] = None,
    media_type: _Optional[str] = None,
    tmdb_id: _Optional[int] = None,
    top_k: int = 8,
) -> str:
    """Search B2B cinema & TV reference scenes by HEX color palette, lighting mood, harmony, camera shot scale, symmetry, and aspect ratio.

    Args:
        target_hex: Optional 6-digit HEX color (#RRGGBB, e.g. '#6EB4E1'). Matched perceptually across all 5 scene swatches.
        color_tolerance: Perceptual color distance tolerance from 2.0 to 50.0 (default 22.0).
        lighting_style: Optional lighting mood: 'low_key', 'high_key', 'chiaroscuro', 'silhouette', 'balanced'.
        shot_scale: Optional framing scale: 'extreme_close_up', 'close_up', 'medium_shot', 'wide_shot'.
        color_harmony: Optional harmony: 'teal_orange', 'cyberpunk_neon', 'warm_vintage', 'cool_noir', 'monochrome', 'natural_balanced'.
        min_symmetry: Optional minimum left-right symmetry score (0.0 to 1.0).
        min_aspect_ratio: Optional minimum active aspect ratio (e.g. 2.30).
        max_aspect_ratio: Optional maximum active aspect ratio.
        media_type: Optional filter: 'movie' or 'tv'.
        tmdb_id: Optional TMDB ID to inspect scenes inside one specific title.
        top_k: Maximum reference scenes to return (1 to 50, default 8).
    """
    api_key = _get_api_key()
    payload: dict = {
        "top_k": max(1, min(50, int(top_k))),
        "color_tolerance": max(2.0, min(50.0, float(color_tolerance))),
    }
    if target_hex:
        hx = target_hex.strip()
        if not _HEX_RE.match(hx):
            return "Error: target_hex must be a 6-character HEX color like '#6EB4E1'."
        payload["target_hex"] = hx if hx.startswith("#") else f"#{hx}"
    if lighting_style:
        payload["lighting_style"] = lighting_style.strip().lower()
    if shot_scale:
        payload["shot_scale"] = shot_scale.strip().lower()
    if color_harmony:
        payload["color_harmony"] = color_harmony.strip().lower()
    if min_symmetry is not None:
        payload["min_symmetry"] = max(0.0, min(1.0, float(min_symmetry)))
    if min_aspect_ratio is not None:
        payload["min_aspect_ratio"] = float(min_aspect_ratio)
    if max_aspect_ratio is not None:
        payload["max_aspect_ratio"] = float(max_aspect_ratio)
    if media_type:
        payload["media_type"] = media_type.strip().lower()
    if tmdb_id is not None:
        payload["tmdb_id"] = int(tmdb_id)

    with httpx.Client(timeout=30.0) as client:
        resp = client.post(
            f"{API_BASE}/v1/cinematography/search",
            headers={"X-API-Key": api_key, "Content-Type": "application/json"},
            json=payload,
        )
    if resp.status_code != 200:
        return f"API Error ({resp.status_code}): {resp.text}"

    data = resp.json()
    matches = data.get("matches") or []
    q = data.get("quota") or {}
    hdr = f"Cinematography Latency: {data.get('latency_ms')} ms | Plan: {q.get('plan')} | Remaining Quota: {q.get('remaining_quota')}"
    if not matches:
        return f"{hdr}\nNo scenes matched these filters. Try increasing color_tolerance or removing a filter."

    lines = [hdr, ""]
    for idx, m in enumerate(matches, start=1):
        yr = f" ({m['year']})" if m.get("year") else ""
        ep = f" • {m['episode']}" if m.get("episode") else ""
        tmdb = f" | TMDB #{m['tmdb_id']}" if m.get("tmdb_id") else ""
        dist = f" | Dist: {m['color_distance']}" if "color_distance" in m else ""
        sw = ", ".join(f"{s.get('hex')} ({float(s.get('ratio') or 0)*100:.0f}%)" for s in (m.get("palette") or []))
        lines.append(f"{idx}. {m.get('title')}{yr} [{m.get('media_type', 'movie')}{ep}] @ {m.get('timecode')} ({m.get('frame_sec')}s){tmdb}{dist}")
        lines.append(f"   Palette: {sw}")
        lines.append(f"   Light={m.get('lighting_style')} | Scale={m.get('shot_scale')} | Harmony={m.get('color_harmony')} | Aspect={m.get('aspect_ratio')}:1 | Sym={m.get('symmetry_score')}")
    return "\n".join(lines)


@mcp.tool()
def search_dialogue_timestamp(
    query: str,
    lang: _Optional[str] = None,
    media_type: _Optional[str] = None,
    tmdb_id: _Optional[int] = None,
    top_k: int = 5,
    min_score: float = 0.72,
) -> str:
    """Find the exact movie/series episode and HH:MM:SS scene timestamp from a remembered quote or dialogue topic across 24 languages.

    Args:
        query: Remembered quote or conversational topic in Turkish, English, or any of 24 languages (do NOT enter a movie title).
        lang: Optional ISO-639-1 subtitle language filter (e.g. 'tr', 'en', 'fr', 'ja'). Leave None for automatic 24-language search.
        media_type: Optional filter: 'movie' or 'tv'.
        tmdb_id: Optional TMDB ID to search inside one specific title.
        top_k: Number of matches to return (1 to 20, default 5).
        min_score: Minimum semantic similarity score (0.50 to 0.99, default 0.72).
    """
    api_key = _get_api_key()
    clean_q = query.strip()
    if len(clean_q) < 2:
        return "Error: Dialogue query must be at least 2 characters."

    payload: dict = {
        "query": clean_q,
        "top_k": max(1, min(20, int(top_k))),
        "min_score": max(0.50, min(0.99, float(min_score))),
    }
    if lang:
        payload["lang"] = lang.strip().lower()[:3]
    if media_type:
        payload["media_type"] = media_type.strip().lower()
    if tmdb_id is not None:
        payload["tmdb_id"] = int(tmdb_id)

    with httpx.Client(timeout=30.0) as client:
        resp = client.post(
            f"{API_BASE}/v1/dialogue/search",
            headers={"X-API-Key": api_key, "Content-Type": "application/json"},
            json=payload,
        )
    if resp.status_code != 200:
        return f"API Error ({resp.status_code}): {resp.text}"

    data = resp.json()
    matches = data.get("matches") or []
    q = data.get("quota") or {}
    hdr = f"Dialogue DNA Latency: {data.get('latency_ms')} ms | Plan: {q.get('plan')} | Remaining Quota: {q.get('remaining_quota')}"
    if not matches:
        return f"{hdr}\nNo dialogue match above threshold (archive harvesting continues 24/7)."

    lines = [hdr, ""]
    for idx, m in enumerate(matches, start=1):
        yr = f" ({m['year']})" if m.get("year") else ""
        ep = f" • {m['episode']}" if m.get("episode") else ""
        tmdb = f" | TMDB #{m['tmdb_id']}" if m.get("tmdb_id") else ""
        mlang = str(m.get("matched_lang") or "auto").upper()
        conf = float(m.get("confidence") or 0.0) * 100.0
        lines.append(f"{idx}. {m.get('title')}{yr} [{m.get('media_type', 'movie')}{ep}] @ {m.get('timecode')} ({m.get('start_sec')}s-{m.get('end_sec')}s) — {conf:.1f}% | Lang: {mlang}{tmdb}")
    return "\n".join(lines)


@mcp.tool()
def check_visual_dna_status() -> str:
    """Check Karanfil Labs API health plus live Visual DNA, Cinematography Color DNA, and 24-Language Dialogue DNA statistics (no API key required)."""
    out = {}
    with httpx.Client(timeout=15.0) as client:
        rh = client.get(f"{API_BASE}/health")
        out["visual_dna_health"] = rh.json() if rh.status_code == 200 else f"HTTP {rh.status_code}"
        rb = client.get(f"{API_BASE}/v1/cinematography/stats")
        if rb.status_code == 200:
            out["cinematography_and_dialogue_stats"] = rb.json()
    return _json.dumps(out, indent=2, ensure_ascii=False)

def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
