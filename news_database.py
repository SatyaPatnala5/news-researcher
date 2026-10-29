
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from news_classifier import classify_headline



DB_PATH = Path(__file__).with_name("news.db")


@contextmanager
def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                source TEXT NOT NULL,
                published TEXT,
                first_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                region TEXT,
                category TEXT
            )
        """)

        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(stories)"
            ).fetchall()
        }

        if "region" not in columns:
            connection.execute(
                "ALTER TABLE stories ADD COLUMN region TEXT"
            )

        if "category" not in columns:
            connection.execute(
                "ALTER TABLE stories ADD COLUMN category TEXT"
            )


def save_stories(stories):
    initialize_database()
    saved_count = 0

    with get_connection() as connection:
        for story in stories:
            cursor = connection.execute("""
                INSERT OR IGNORE INTO stories
                    (url, title, source, published, region, category)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                story["link"],
                story["title"],
                story["source"],
                story.get("published", ""),
                story.get("region"),
                story.get("category"),
            ))
            saved_count += cursor.rowcount

    return saved_count






def get_stories(limit=20, category=None):
    """Retrieve stories ordered by publication date, newest first."""
    from email.utils import parsedate_to_datetime

    initialize_database()

    with get_connection() as connection:
        if category is None:
            rows = connection.execute("""
                SELECT title, source, published, url, first_seen,
                       region, category
                FROM stories
            """).fetchall()
        else:
            rows = connection.execute("""
                SELECT title, source, published, url, first_seen,
                       region, category
                FROM stories
                WHERE category = ?
            """, (category,)).fetchall()

    stories = [dict(row) for row in rows]

    def publication_time(story):
        published = story.get("published") or ""

        try:
            parsed = parsedate_to_datetime(published)

            if parsed is None:
                return float("-inf")

            if parsed.tzinfo is None:
                return float("-inf")

            return parsed.timestamp()

        except (TypeError, ValueError, OverflowError):
            return float("-inf")

    stories.sort(key=publication_time, reverse=True)

    return stories[:limit]




def reclassify_stories():
    """Recalculate categories for all stored stories."""
    initialize_database()

    with get_connection() as connection:
        stories = connection.execute(
            "SELECT id, title FROM stories"
        ).fetchall()

        updated_count = 0

        for story in stories:
            new_category = classify_headline(story["title"])

            connection.execute(
                "UPDATE stories SET category = ? WHERE id = ?",
                (new_category, story["id"]),
            )

            updated_count += 1

    return updated_count
