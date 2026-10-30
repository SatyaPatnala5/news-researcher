
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from news_classifier import classify_headline


DB_PATH = Path(__file__).with_name("news.db")

MAX_STORIES = 5000
CLEANUP_BATCH_SIZE = 100
SAVED_BY = "news_researcher"


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
    """Create the fresh database schema if it does not exist."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                source TEXT NOT NULL,
                published TEXT,
                saved_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                saved_by TEXT NOT NULL DEFAULT 'news_researcher',
                region TEXT,
                category TEXT
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS source_health (
                source TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                headlines_count INTEGER NOT NULL DEFAULT 0,
                checked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                error_message TEXT
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS source_health_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                status TEXT NOT NULL,
                headlines_count INTEGER NOT NULL DEFAULT 0,
                checked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                error_message TEXT
            )
        """)


def enforce_retention(connection):
    """Delete oldest saved stories in batches until under the limit."""
    while True:
        count = connection.execute(
            "SELECT COUNT(*) FROM stories"
        ).fetchone()[0]

        if count <= MAX_STORIES:
            break

        connection.execute("""
            DELETE FROM stories
            WHERE id IN (
                SELECT id
                FROM stories
                ORDER BY saved_at ASC, id ASC
                LIMIT ?
            )
        """, (CLEANUP_BATCH_SIZE,))


def save_stories(stories):
    """Save new stories, prevent duplicates, and enforce retention."""
    initialize_database()
    saved_count = 0

    with get_connection() as connection:
        for story in stories:
            cursor = connection.execute("""
                INSERT OR IGNORE INTO stories
                    (url, title, source, published, saved_by, region, category)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                story["link"],
                story["title"],
                story["source"],
                story.get("published", ""),
                SAVED_BY,
                story.get("region"),
                story.get("category"),
            ))

            saved_count += cursor.rowcount

        enforce_retention(connection)

    return saved_count


def get_stories(limit=20, category=None):
    """Retrieve stories ordered by publication date, newest first."""
    from email.utils import parsedate_to_datetime

    initialize_database()

    with get_connection() as connection:
        if category is None:
            rows = connection.execute("""
                SELECT title, source, published, url, saved_at, saved_by,
                       region, category
                FROM stories
            """).fetchall()
        else:
            rows = connection.execute("""
                SELECT title, source, published, url, saved_at, saved_by,
                       region, category
                FROM stories
                WHERE category = ?
            """, (category,)).fetchall()

    stories = [dict(row) for row in rows]

    def publication_time(story):
        published = story.get("published") or ""

        try:
            parsed = parsedate_to_datetime(published)

            if parsed is None or parsed.tzinfo is None:
                return float("-inf")

            return parsed.timestamp()

        except (TypeError, ValueError, OverflowError):
            return float("-inf")

    stories.sort(key=publication_time, reverse=True)

    return stories[:limit]


def get_database_stats():
    """Return the current record count and oldest/newest save timestamps."""
    initialize_database()

    with get_connection() as connection:
        row = connection.execute("""
            SELECT
                COUNT(*) AS record_count,
                MIN(saved_at) AS oldest_saved_at,
                MAX(saved_at) AS newest_saved_at
            FROM stories
        """).fetchone()

    return dict(row)



def record_source_health(source, status, headlines_count=0, error_message=None):
    """Save a source check and update its latest health status."""
    if status not in {"OK", "EMPTY", "FAILED"}:
        raise ValueError("Status must be OK, EMPTY, or FAILED.")

    initialize_database()

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO source_health_history
                (source, status, headlines_count, error_message)
            VALUES (?, ?, ?, ?)
        """, (source, status, headlines_count, error_message))

        connection.execute("""
            INSERT INTO source_health
                (source, status, headlines_count, checked_at, error_message)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)
            ON CONFLICT(source) DO UPDATE SET
                status = excluded.status,
                headlines_count = excluded.headlines_count,
                checked_at = excluded.checked_at,
                error_message = excluded.error_message
        """, (source, status, headlines_count, error_message))


def get_source_health():
    """Return the latest recorded health check for each source."""
    initialize_database()

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT source, status, headlines_count, checked_at, error_message
            FROM source_health
            ORDER BY source
        """).fetchall()

    return [dict(row) for row in rows]

def cleanup_source_health_history(days=30):
    """Delete source health history older than the specified number of days."""
    if days <= 0:
        raise ValueError("Retention days must be greater than zero.")

    initialize_database()

    with get_connection() as connection:
        cursor = connection.execute("""
            DELETE FROM source_health_history
            WHERE checked_at < datetime('now', ?)
        """, (f"-{days} days",))

        deleted_count = cursor.rowcount

    return deleted_count

def print_source_health():
    """Display the latest health status of all news sources."""
    sources = get_source_health()

    print("\n=== News Source Health ===\n")

    if not sources:
        print("No source health records available yet.")
        return

    for source in sources:
        print(f"Source: {source['source']}")
        print(f"Status: {source['status']}")
        print(f"Headlines: {source['headlines_count']}")
        print(f"Last checked: {source['checked_at']}")

        if source["error_message"]:
            print(f"Error: {source['error_message']}")

        print("-" * 40)


def clear_stories():
    """Delete all stories. Call only when an intentional reset is needed."""
    initialize_database()

    with get_connection() as connection:
        connection.execute("DELETE FROM stories")


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
