#!/usr/bin/env python3
"""Fetch public Facebook page posts via web scraping (best-effort)."""

import argparse
import json
import re
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def fetch_facebook_page(page_url):
    """Attempt to scrape public Facebook page posts.
    
    Note: Facebook has aggressive anti-scraping. This is best-effort.
    Returns whatever we can extract; may return empty on some runs.
    """
    req = Request(page_url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    })

    try:
        with urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        return {"error": f"HTTP {e.code}", "posts": []}
    except Exception as e:
        return {"error": str(e), "posts": []}

    # Try to extract post text from meta tags and structured data
    posts = []

    # Method 1: og:description often has latest post summary
    og_desc = re.findall(r'<meta property="og:description" content="([^"]*)"', html)
    if og_desc:
        posts.append({"source": "og:description", "text": og_desc[0][:500]})

    # Method 2: Look for post-like content in JSON-LD or embedded data
    for m in re.finditer(r'"message":\s*\{"text":\s*"([^"]{10,500})"', html):
        text = m.group(1).encode().decode("unicode_escape", errors="replace")
        posts.append({"source": "embedded_data", "text": text[:500]})

    return {
        "page_url": page_url,
        "posts_found": len(posts),
        "posts": posts[:10],
        "note": "Facebook anti-scraping may limit results. Use web_fetch as fallback."
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch Facebook page posts (best-effort)")
    parser.add_argument("--config", required=True, help="Path to game config JSON")
    parser.add_argument("--url", help="Override URL")
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    url = args.url or config.get("facebook", {}).get("page_url", "")
    if not url:
        print(json.dumps({"error": "No Facebook URL configured"}))
        sys.exit(1)

    result = fetch_facebook_page(url)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
