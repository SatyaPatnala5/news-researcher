
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import news_database


class TestNewsDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_db = Path(self.temp_dir.name) / "test_news.db"

        self.database_patch = patch.object(
            news_database, "DB_PATH", self.test_db
        )
        self.database_patch.start()

        # Keep retention tests small and fast.
        self.retention_limit_patch = patch.object(
            news_database, "MAX_STORIES", 5
        )
        self.retention_limit_patch.start()

        self.batch_size_patch = patch.object(
            news_database, "CLEANUP_BATCH_SIZE", 2
        )
        self.batch_size_patch.start()

        news_database.initialize_database()

        self.story = {
            "link": "https://example.com/story-1",
            "title": "Example news story",
            "source": "Example News",
            "published": "Wed, 21 Oct 2026 10:00:00 +0000",
        }

    def tearDown(self):
        self.batch_size_patch.stop()
        self.retention_limit_patch.stop()
        self.database_patch.stop()
        self.temp_dir.cleanup()

    def test_save_story(self):
        saved_count = news_database.save_stories([self.story])
        self.assertEqual(saved_count, 1)

    def test_duplicate_story_is_not_saved_twice(self):
        news_database.save_stories([self.story])
        saved_count = news_database.save_stories([self.story])

        self.assertEqual(saved_count, 0)
        self.assertEqual(len(news_database.get_stories(100)), 1)

    def test_saved_story_can_be_retrieved(self):
        news_database.save_stories([self.story])
        stories = news_database.get_stories(10)

        self.assertEqual(len(stories), 1)
        self.assertEqual(stories[0]["title"], "Example news story")
        self.assertEqual(stories[0]["source"], "Example News")
        self.assertEqual(
            stories[0]["url"], "https://example.com/story-1"
        )

    def test_region_and_category_are_saved(self):
        story = {
            **self.story,
            "region": "India",
            "category": "Technology",
        }

        news_database.save_stories([story])
        stories = news_database.get_stories(10)

        self.assertEqual(len(stories), 1)
        self.assertEqual(stories[0]["region"], "India")
        self.assertEqual(stories[0]["category"], "Technology")

    def test_stories_can_be_filtered_by_category(self):
        stories = [
            {
                **self.story,
                "link": "https://example.com/tech",
                "title": "Cybersecurity update",
                "category": "Technology",
            },
            {
                **self.story,
                "link": "https://example.com/politics",
                "title": "Election results",
                "category": "Politics",
            },
            {
                **self.story,
                "link": "https://example.com/ai",
                "title": "New AI model",
                "category": "AI",
            },
        ]

        news_database.save_stories(stories)

        technology_stories = news_database.get_stories(
            10, category="Technology"
        )

        self.assertEqual(len(technology_stories), 1)
        self.assertEqual(
            technology_stories[0]["title"], "Cybersecurity update"
        )
        self.assertEqual(
            technology_stories[0]["category"], "Technology"
        )

    def test_stories_are_ordered_by_publication_date_across_timezones(self):
        older_story = {
            **self.story,
            "link": "https://example.com/older",
            "title": "Older story",
            "published": "Wed, 21 Oct 2026 14:00:00 +0530",
        }
        newer_story = {
            **self.story,
            "link": "https://example.com/newer",
            "title": "Newer story",
            "published": "Wed, 21 Oct 2026 10:00:00 +0000",
        }

        news_database.save_stories([older_story, newer_story])
        stories = news_database.get_stories(10)

        self.assertEqual(stories[0]["title"], "Newer story")
        self.assertEqual(stories[1]["title"], "Older story")

    def test_saved_at_and_saved_by_are_recorded(self):
        news_database.save_stories([self.story])
        stories = news_database.get_stories(10)

        self.assertTrue(stories[0]["saved_at"])
        self.assertEqual(stories[0]["saved_by"], "news_researcher")

    def test_database_stats_report_record_count(self):
        news_database.save_stories([self.story])

        stats = news_database.get_database_stats()

        self.assertEqual(stats["record_count"], 1)
        self.assertTrue(stats["oldest_saved_at"])
        self.assertTrue(stats["newest_saved_at"])

    def test_retention_removes_oldest_saved_stories(self):
        stories = [
            {
                **self.story,
                "link": f"https://example.com/story-{number}",
                "title": f"Story {number}",
                "published": f"Wed, 21 Oct 2026 10:{number:02d}:00 +0000",
            }
            for number in range(1, 8)
        ]

        news_database.save_stories(stories)

        stats = news_database.get_database_stats()
        self.assertEqual(stats["record_count"], 5)

        with news_database.get_connection() as connection:
            saved_urls = {
                row["url"]
                for row in connection.execute(
                    "SELECT url FROM stories"
                ).fetchall()
            }

        self.assertNotIn("https://example.com/story-1", saved_urls)
        self.assertNotIn("https://example.com/story-2", saved_urls)
        self.assertTrue(
            "https://example.com/story-7" in saved_urls
        )

    def test_clear_stories_removes_all_records(self):
        news_database.save_stories([self.story])

        news_database.clear_stories()

        self.assertEqual(
            news_database.get_database_stats()["record_count"], 0
        )


if __name__ == "__main__":
    unittest.main()
