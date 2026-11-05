#!/usr/bin/env python3
"""x-search — search X (Twitter) via xAI Grok Live Search.

Backed by xAI's built-in ``x_search`` tool on the Responses API
(``https://api.x.ai/v1/responses``): Grok runs the X search server-side and
returns a synthesized answer plus citations to the source posts. No cookies,
no scraping, no MCP. The credential is read from env ``XAI_API_KEY`` or from a
key file (``~/.config/x-research/xai.key``, override with ``XAI_KEY_FILE``).

Usage:
    x_search.py "что нового по AI agents" --handles karpathy,simonw --from 2026-06-03
    x_search.py "Claude Code skills" --json

The bearer token is NEVER printed. Only the synthesized
result + source URLs are shown.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_KEY_FILE = Path.home() / ".config" / "x-research" / "xai.key"
API_BASE = "https://api.x.ai/v1"
DEFAULT_MODEL = os.environ.get("XAI_MODEL", "").strip() or "grok-4.20-reasoning"
TIMEOUT = 200


def resolve_bearer() -> str:
    """XAI_API_KEY env -> key file (XAI_KEY_FILE or the default path)."""
    key = os.environ.get("XAI_API_KEY", "").strip()
    if key:
        return key
    path = Path(os.environ.get("XAI_KEY_FILE") or DEFAULT_KEY_FILE).expanduser()
    try:
        key = path.read_text(encoding="utf-8").strip()
    except OSError:
        key = ""
    if key:
        return key
    sys.exit("ERR: no xAI credential — set XAI_API_KEY (or XAI_KEY_FILE)")


def _split_handles(raw: str) -> List[str]:
    return [h.strip().lstrip("@") for h in (raw or "").split(",") if h.strip()]


def build_payload(args: argparse.Namespace) -> Dict[str, Any]:
    tool: Dict[str, Any] = {"type": "x_search"}
    if args.handles:
        tool["allowed_x_handles"] = _split_handles(args.handles)
    if args.exclude:
        tool["excluded_x_handles"] = _split_handles(args.exclude)
    if args.from_date:
        tool["from_date"] = args.from_date.strip()
    if args.to_date:
        tool["to_date"] = args.to_date.strip()
    if args.images:
        tool["enable_image_understanding"] = True
    if args.videos:
        tool["enable_video_understanding"] = True
    return {
        "model": args.model,
        "input": [{"role": "user", "content": args.query}],
        "tools": [tool],
        "store": False,
    }


def _post(payload: Dict[str, Any], bearer: str) -> Dict[str, Any]:
    req = urllib.request.Request(
        f"{API_BASE}/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {bearer}",
            "Content-Type": "application/json",
            "User-Agent": "x-research-skill/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_text(payload: Dict[str, Any]) -> str:
    txt = str(payload.get("output_text") or "").strip()
    if txt:
        return txt
    parts: List[str] = []
    for item in payload.get("output", []) or []:
        if item.get("type") != "message":
            continue
        for content in item.get("content", []) or []:
            if content.get("type") in {"output_text", "text"}:
                t = str(content.get("text") or "").strip()
                if t:
                    parts.append(t)
    return "\n\n".join(parts).strip()


def extract_citations(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    seen = set()

    def add(url: str, title: str = "") -> None:
        url = (url or "").strip()
        if url and url not in seen:
            seen.add(url)
            out.append({"url": url, "title": (title or "").strip()})

    for c in payload.get("citations", []) or []:
        if isinstance(c, str):
            add(c)
        elif isinstance(c, dict):
            add(c.get("url", ""), c.get("title", ""))
    for item in payload.get("output", []) or []:
        if item.get("type") != "message":
            continue
        for content in item.get("content", []) or []:
            for ann in content.get("annotations", []) or []:
                if ann.get("type") == "url_citation":
                    add(ann.get("url", ""), ann.get("title", ""))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="x-search",
        description="Search X (Twitter) via xAI Grok Live Search (x_search tool of the xAI Responses API).",
    )
    ap.add_argument("query", help="natural-language search query (RU/EN)")
    ap.add_argument("--handles", help="comma-separated X handles to restrict to (allowed_x_handles)")
    ap.add_argument("--exclude", help="comma-separated X handles to exclude")
    ap.add_argument("--from", dest="from_date", default="", help="from_date YYYY-MM-DD")
    ap.add_argument("--to", dest="to_date", default="", help="to_date YYYY-MM-DD")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"xAI model (default {DEFAULT_MODEL})")
    ap.add_argument("--images", action="store_true", help="enable image understanding")
    ap.add_argument("--videos", action="store_true", help="enable video understanding")
    ap.add_argument("--json", action="store_true", help="print raw JSON response")
    args = ap.parse_args()

    payload = build_payload(args)
    bearer = resolve_bearer()
    try:
        data = _post(payload, bearer)
    except urllib.error.HTTPError as e:
        sys.exit(f"ERR HTTP {e.code}: {e.read().decode(errors='replace')[:400]}")
    except Exception as e:  # noqa: BLE001
        sys.exit(f"ERR: {type(e).__name__}: {e}")

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    print(extract_text(data) or "(пустой ответ — нет синтеза)")
    cites = extract_citations(data)
    if cites:
        print("\n--- Источники (X) ---")
        for c in cites:
            print(f"- {c['url']}" + (f"  — {c['title']}" if c["title"] else ""))


if __name__ == "__main__":
    main()
