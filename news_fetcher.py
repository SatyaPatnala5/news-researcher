
import ssl
import urllib.error
import urllib.request

import certifi
import feedparser

from news_sources import NEWS_SOURCES
from news_classifier import classify_headline
from news_database import record_source_health


def fetch_headlines(limit=10, region=None):
    """Fetch headlines from configured sources and mix their results."""
    source_headlines = []

    selected_sources = NEWS_SOURCES
    if region is not None and region.lower() != "all":
        selected_sources = [
            source for source in NEWS_SOURCES
            if source["region"].lower() == region.lower()
        ]

    for source in selected_sources:
        headlines = []

        try:
            request = urllib.request.Request(
                source["url"],
                headers={"User-Agent": "NewsResearcher/1.0"},
            )

            context = ssl.create_default_context(cafile=certifi.where())

            with urllib.request.urlopen(
                request, timeout=20, context=context
            ) as response:
                feed = feedparser.parse(response.read())

            for entry in feed.entries[:limit]:
                headlines.append({
                    "source": source["name"],
                    "region": source["region"],
                    "category": classify_headline(
                        entry.get("title", "No title")
                    ),
                    "title": entry.get("title", "No title"),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                })

        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as error:
            record_source_health(
                source["name"],
                "FAILED",
                error_message=str(error),
            )
            print(f"Warning: Could not fetch {source['name']}: {error}")
            continue

        status = "OK" if headlines else "EMPTY"
        record_source_health(
            source["name"],
            status,
            headlines_count=len(headlines),
        )

        source_headlines.append(headlines)

    # Take one headline from each source in turn.
    mixed_headlines = []
    max_headlines = max(
        (len(headlines) for headlines in source_headlines),
        default=0,
    )

    for index in range(max_headlines):
        for headlines in source_headlines:
            if index < len(headlines):
                mixed_headlines.append(headlines[index])

    # Sort headlines by publication time, newest first.
    from email.utils import parsedate_to_datetime

    def publication_time(story):
        try:
            published = parsedate_to_datetime(story.get("published", ""))
            if published is None or published.tzinfo is None:
                return float("-inf")
            return published.timestamp()
        except (TypeError, ValueError, OverflowError):
            return float("-inf")

    mixed_headlines.sort(key=publication_time, reverse=True)
    return mixed_headlines

