from news_classifier import classify_headline
from news_ai_classifier import classify_headline_ai


TEST_HEADLINES = [
    ("OpenAI announces a new AI model", "AI"),
    ("Cyber-security flaw found in computer systems", "Technology"),
    ("Gold prices rise as investors react to markets", "Business"),
    ("PM Modi addresses Parliament", "Politics"),
    ("Food testing results released", "Science & Health"),
    ("India wins cricket match", "Sports"),
    ("A quiet day in the countryside", "General"),
]


def main():
    print("\n=== Classifier Comparison ===\n")

    keyword_correct = 0
    ai_correct = 0

    for headline, expected in TEST_HEADLINES:
        keyword_prediction = classify_headline(headline)
        ai_prediction, ai_score = classify_headline_ai(headline)

        if keyword_prediction == expected:
            keyword_correct += 1

        if ai_prediction == expected:
            ai_correct += 1

        print(f"Headline: {headline}")
        print(f"  Expected: {expected}")
        print(f"  Keywords: {keyword_prediction}")
        print(f"  Local AI: {ai_prediction} (score: {ai_score:.3f})")
        print()

    total = len(TEST_HEADLINES)

    print("=== Results ===")
    print(f"Keyword classifier: {keyword_correct}/{total} correct")
    print(f"Local AI classifier: {ai_correct}/{total} correct")


if __name__ == "__main__":
    main()
