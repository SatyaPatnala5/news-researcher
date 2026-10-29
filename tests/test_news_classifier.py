
import unittest

from news_classifier import classify_headline


class TestNewsClassifier(unittest.TestCase):
    def test_ai_headline(self):
        self.assertEqual(
            classify_headline("OpenAI announces a new AI model"),
            "AI",
        )

    def test_technology_headline(self):
        self.assertEqual(
            classify_headline("Cyber-security flaw found in computer systems"),
            "Technology",
        )

    def test_sports_headline(self):
        self.assertEqual(
            classify_headline("India wins cricket match"),
            "Sports",
        )

    def test_science_and_health_headline(self):
        self.assertEqual(
            classify_headline("Food testing results released"),
            "Science & Health",
        )

    def test_unknown_headline_defaults_to_general(self):
        self.assertEqual(
            classify_headline("A quiet day in the countryside"),
            "General",
        )

    def test_ai_takes_precedence_over_business(self):
        self.assertEqual(
            classify_headline("Company announces a new AI product"),
            "AI",
        )

if __name__ == "__main__":
    unittest.main()

