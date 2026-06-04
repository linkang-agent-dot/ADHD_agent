#!/usr/bin/env python3
"""Fetch gift codes from PocketGamer page."""

import argparse
import json
import re
import sys
from urllib.request import Request, urlopen


def fetch_giftcodes(url):
    """Scrape gift codes from PocketGamer."""
    req = Request(url, headers={"User-Agent": "NomiBot/1.0"})

    with urlopen(req) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    # PocketGamer typically lists codes in <strong> or <code> tags, or in list items
    codes = []

    # Pattern 1: codes in bold/strong tags (common format)
    for m in re.finditer(r'<strong>([A-Z0-9]{4,30})</strong>', html):
        code = m.group(1)
        if len(code) >= 4 and code.isalnum():
            codes.append(code)

    # Pattern 2: codes in <code> tags
    for m in re.finditer(r'<code>([A-Z0-9]{4,30})</code>', html):
        code = m.group(1)
        if code not in codes:
            codes.append(code)

    # Pattern 3: look for typical gift code patterns in text
    for m in re.finditer(r'\b([A-Z][A-Z0-9]{5,25})\b', html):
        code = m.group(1)
        # Filter out common HTML/CSS words
        skip = {"DOCTYPE", "CHARSET", "HTTPS", "SCRIPT", "STYLE", "CLASS", "TITLE",
                "HEADER", "FOOTER", "SECTION", "ARTICLE", "BUTTON", "STRONG",
                "DISPLAY", "CONTENT", "RETURN", "FUNCTION", "WINDOW", "DOCUMENT"}
        if code not in skip and code not in codes and len(code) >= 6:
            codes.append(code)

    return list(dict.fromkeys(codes))  # dedupe preserving order


def main():
    parser = argparse.ArgumentParser(description="Fetch gift codes")
    parser.add_argument("--config", required=True, help="Path to game config JSON")
    parser.add_argument("--url", help="Override URL")
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    url = args.url or config.get("giftcode_url", "")
    if not url:
        print(json.dumps({"error": "No giftcode URL configured"}))
        sys.exit(1)

    codes = fetch_giftcodes(url)
    print(json.dumps({
        "source": url,
        "codes": codes,
        "count": len(codes),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
