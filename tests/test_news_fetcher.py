import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import news_fetcher


class TestNewsFetcher(unittest.TestCase):
    def setUp(self):
        self.sources = [
            {
                "name": "Test News",
                "url": "https://example.com/feed.xml",
                "region": "Global",
                "category": "General",
            }
        ]

        self.source_patch = patch.object(
            news_fetcher, "NEWS_SOURCES", self.sources
        )
        self.source_patch.start()
        self.addCleanup(self.source_patch.stop)

        self.response = MagicMock()
        self.response.__enter__.return_value = self.response
        self.response.read.return_value = b"fake RSS data"

        self.urlopen_patch = patch.object(
            news_fetcher.urllib.request,
            "urlopen",
            return_value=self.response,
        )
        self.mock_urlopen = self.urlopen_patch.start()
        self.addCleanup(self.urlopen_patch.stop)

    @patch("news_fetcher.feedparser.parse")
    def test_fetches_and_converts_headline(self, mock_parse):
        mock_parse.return_value = SimpleNamespace(
            entries=[
                {
                    "title": "Example headline",
                    "link": "https://example.com/story",
                    "published": "Wed, 21 Oct 2026 10:00:00 GMT",
                }
            ]
        )

        stories = news_fetcher.fetch_headlines(5)

        self.assertEqual(len(stories), 1)
        self.assertEqual(stories[0]["source"], "Test News")
        self.assertEqual(stories[0]["title"], "Example headline")
        self.assertEqual(
            stories[0]["link"], "https://example.com/story"
        )
        self.assertEqual(
            stories[0]["published"],
            "Wed, 21 Oct 2026 10:00:00 GMT",
        )

        mock_parse.assert_called_once_with(b"fake RSS data")

    @patch("news_fetcher.feedparser.parse")
    def test_missing_fields_use_defaults(self, mock_parse):
        mock_parse.return_value = SimpleNamespace(
            entries=[{}]
        )

        stories = news_fetcher.fetch_headlines()

        self.assertEqual(stories[0]["title"], "No title")
        self.assertEqual(stories[0]["link"], "")
        self.assertEqual(stories[0]["published"], "")

    @patch("news_fetcher.feedparser.parse")
    def test_request_uses_timeout_and_user_agent(self, mock_parse):
        mock_parse.return_value = SimpleNamespace(entries=[])

        news_fetcher.fetch_headlines()

        self.mock_urlopen.assert_called_once()
        args, kwargs = self.mock_urlopen.call_args

        self.assertEqual(kwargs["timeout"], 20)
        self.assertEqual(
            args[0].get_header("User-agent"),
            "NewsResearcher/1.0",
        )


    @patch("news_fetcher.feedparser.parse")
    def test_one_failed_source_does_not_stop_the_next(self, mock_parse):
        import urllib.error

        self.sources[:] = [
            {
                "name": "Broken News",
                "url": "https://broken.example/feed.xml",
                "region": "Global",
                "category": "General",
            },
            {
                "name": "Working News",
                "url": "https://working.example/feed.xml",
                "region": "India",
                "category": "General",
            },
        ]

        self.mock_urlopen.side_effect = [
            urllib.error.URLError("Simulated network failure"),
            self.response,
        ]

        mock_parse.return_value = SimpleNamespace(
            entries=[
                {
                    "title": "Story from working source",
                    "link": "https://working.example/story",
                    "published": "2026-10-21",
                }
            ]
        )

        with patch("builtins.print") as mock_print:
            stories = news_fetcher.fetch_headlines()

        self.assertEqual(len(stories), 1)
        self.assertEqual(stories[0]["source"], "Working News")
        self.assertEqual(
            stories[0]["title"], "Story from working source"
        )
        mock_print.assert_called_once()


if __name__ == "__main__":
    unittest.main()
