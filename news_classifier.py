
def classify_headline(title):
    """Assign a category using simple headline keywords."""
    text = title.lower()

    rules = [
        ("AI", ["artificial intelligence", " ai ", "chatgpt", "openai",
                "machine learning", "generative ai", "llm"]),
        ("Technology", ["technology", "cyber", "software", "computer",
                        "digital", "internet", "smartphone", "security flaw"]),
        ("Business", ["business", "company", "companies", "stock market",
                      "shares", "profit", "earnings", "startup", "economy"]),
        ("Politics", ["prime minister", "pm modi", "government", "election",
                      "parliament", "congress", "minister", "president",
                      "trump", "rahul gandhi", "jaishankar", "modi",
                      "political", "politics", "lawsuit"]),
        ("Science & Health", ["health", "hospital", "medical", "science",
                              "research study", "disease", "food testing",
                              "food sample", "testing triples", "failure rate"]),
        ("Sports", ["cricket", "football", "olympics", "tournament",
                    "championship", "match", "tennis"]),
    ]

    for category, keywords in rules:
        if any(keyword in text for keyword in keywords):
            return category

    return "General"

