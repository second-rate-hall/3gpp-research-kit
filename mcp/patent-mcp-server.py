#!/usr/bin/env python3
"""Lightweight patent background MCP-style server.

This is intentionally small and dependency-free. It speaks a minimal JSON-lines
protocol compatible with simple local tool wrappers:

Input:
  {"method":"tools/list"}
  {"method":"tools/call","params":{"name":"search_patents","arguments":{"query":"RedCap 3GPP"}}}
  {"method":"tools/call","params":{"name":"fetch_patent_background","arguments":{"url":"https://patents.google.com/patent/..."}}}

Output:
  one JSON object per line.

Patent background is auxiliary evidence only. It can explain commercial or
technical pain points, but it cannot confirm a 3GPP standard claim.
"""

from __future__ import annotations

import html
import json
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass


USER_AGENT = "3gpp-research-kit-patent-mcp/0.1"


@dataclass
class PatentHit:
    title: str
    url: str
    snippet: str


def fetch_url(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def strip_tags(text: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def search_patents(query: str, limit: int = 5) -> list[dict[str, str]]:
    xhr = "https://patents.google.com/xhr/query?url=q%3D" + urllib.parse.quote(query)
    try:
        data = json.loads(fetch_url(xhr))
        results: list[PatentHit] = []
        for cluster in data.get("results", {}).get("cluster", []):
            for item in cluster.get("result", []):
                patent = item.get("patent", {})
                patent_id = item.get("id", "")
                if not patent_id:
                    continue
                url = urllib.parse.urljoin("https://patents.google.com/", patent_id)
                results.append(
                    PatentHit(
                        title=strip_tags(patent.get("title", "")),
                        url=url,
                        snippet=strip_tags(patent.get("snippet", "")),
                    )
                )
                if len(results) >= limit:
                    return [asdict(hit) for hit in results]
    except Exception:
        pass

    page = fetch_url("https://patents.google.com/?q=" + urllib.parse.quote(query))
    hits: list[PatentHit] = []
    for match in re.finditer(r'<a[^>]+href="(/patent/[^"]+)"[^>]*>(.*?)</a>', page, flags=re.I | re.S):
        href, title_html = match.groups()
        title = strip_tags(title_html)
        if not title or len(title) < 8:
            continue
        patent_url = urllib.parse.urljoin("https://patents.google.com", href)
        if any(hit.url == patent_url for hit in hits):
            continue
        hits.append(PatentHit(title=title, url=patent_url, snippet=""))
        if len(hits) >= limit:
            break
    return [asdict(hit) for hit in hits]


def extract_background(page: str) -> str:
    patterns = [
        r'<section[^>]+itemprop="description"[^>]*>(.*?)</section>',
        r'<heading[^>]*>\s*Background\s*</heading>(.*?)(?:<heading|</section>)',
        r'BACKGROUND(?: OF THE INVENTION)?(.*?)(?:SUMMARY|BRIEF DESCRIPTION|DETAILED DESCRIPTION)',
    ]
    for pattern in patterns:
        match = re.search(pattern, page, flags=re.I | re.S)
        if match:
            text = strip_tags(match.group(1))
            if len(text) > 120:
                return text[:5000]
    text = strip_tags(page)
    idx = text.lower().find("background")
    if idx >= 0:
        return text[idx : idx + 5000]
    return text[:3000]


def fetch_patent_background(url: str) -> dict[str, str]:
    page = fetch_url(url)
    title_match = re.search(r"<title[^>]*>(.*?)</title>", page, flags=re.I | re.S)
    title = strip_tags(title_match.group(1)) if title_match else url
    return {
        "url": url,
        "title": title,
        "background": extract_background(page),
        "evidence_status": "auxiliary_background_not_3gpp_standard_evidence",
    }


def handle(request: dict) -> dict:
    method = request.get("method")
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "search_patents",
                    "description": "Search Google Patents for feature-related patents.",
                    "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer"}}},
                },
                {
                    "name": "fetch_patent_background",
                    "description": "Fetch a patent page and extract Background/description text.",
                    "inputSchema": {"type": "object", "properties": {"url": {"type": "string"}}},
                },
            ]
        }
    if method == "tools/call":
        params = request.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        if name == "search_patents":
            return {"content": search_patents(str(args.get("query", "")), int(args.get("limit", 5)))}
        if name == "fetch_patent_background":
            return {"content": fetch_patent_background(str(args.get("url", "")))}
        return {"error": f"unknown tool: {name}"}
    return {"error": f"unknown method: {method}"}


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            response = handle(json.loads(line))
        except Exception as exc:
            response = {"error": str(exc)}
        print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
