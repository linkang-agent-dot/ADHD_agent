#!/usr/bin/env python3
"""Fetch App Store data: version, rating, reviews via public APIs."""

import argparse
import json
import sys
from datetime import datetime
from urllib.request import Request, urlopen


def fetch_app_lookup(ios_id, country="us"):
    """Fetch app metadata from iTunes Lookup API."""
    url = f"https://itunes.apple.com/lookup?id={ios_id}&country={country}"
    with urlopen(url) as resp:
        data = json.loads(resp.read())
    
    if not data.get("results"):
        return {"error": "App not found"}
    
    app = data["results"][0]
    return {
        "name": app.get("trackName", ""),
        "version": app.get("version", ""),
        "rating": round(app.get("averageUserRating", 0), 1),
        "rating_count": app.get("userRatingCount", 0),
        "genre": app.get("primaryGenreName", ""),
        "release_date": app.get("currentVersionReleaseDate", ""),
        "description": app.get("description", "")[:500],
        "release_notes": app.get("releaseNotes", ""),
        "content_rating": app.get("contentAdvisoryRating", ""),
        "price": app.get("formattedPrice", "Free"),
        "seller": app.get("sellerName", ""),
        "bundle_id": app.get("bundleId", ""),
    }


def fetch_reviews_rss(ios_id, country="us", limit=50):
    """Fetch recent reviews from App Store RSS feed."""
    url = f"https://itunes.apple.com/{country}/rss/customerreviews/id={ios_id}/sortBy=mostRecent/json"
    req = Request(url, headers={"User-Agent": "NomiBot/1.0"})
    
    with urlopen(req) as resp:
        data = json.loads(resp.read())
    
    entries = data.get("feed", {}).get("entry", [])
    # First entry is usually the app metadata, skip it
    reviews = []
    for entry in entries:
        if "im:rating" not in entry:
            continue
        reviews.append({
            "title": entry.get("title", {}).get("label", ""),
            "content": entry.get("content", {}).get("label", "")[:300],
            "rating": int(entry.get("im:rating", {}).get("label", "0")),
            "author": entry.get("author", {}).get("name", {}).get("label", ""),
            "version": entry.get("im:version", {}).get("label", ""),
            "date": entry.get("updated", {}).get("label", ""),
        })
    
    return reviews[:limit]


def analyze_reviews(reviews):
    """Simple keyword extraction from reviews."""
    positive = []
    negative = []
    
    for r in reviews:
        text = f"{r['title']} {r['content']}".lower()
        if r["rating"] >= 4:
            positive.append(text)
        elif r["rating"] <= 2:
            negative.append(text)
    
    return {
        "total_reviews": len(reviews),
        "positive_count": len(positive),
        "negative_count": len(negative),
        "positive_samples": [r for r in reviews if r["rating"] >= 4][:5],
        "negative_samples": [r for r in reviews if r["rating"] <= 2][:5],
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch App Store data")
    parser.add_argument("--config", required=True, help="Path to game config JSON")
    parser.add_argument("--country", default="us", help="Country code")
    parser.add_argument("--reviews", action="store_true", help="Also fetch reviews")
    parser.add_argument("--review-limit", type=int, default=50)
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    ios_id = config["app_store"]["ios_id"]

    output = {"app_info": fetch_app_lookup(ios_id, args.country)}

    if args.reviews:
        reviews = fetch_reviews_rss(ios_id, args.country, args.review_limit)
        output["reviews"] = reviews
        output["review_analysis"] = analyze_reviews(reviews)

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
