import torch
from transformers import pipeline

MODEL_NAME = "facebook/bart-large-mnli"

CATEGORY_DESCRIPTIONS = {
    "AI": "artificial intelligence, machine learning, ChatGPT, OpenAI, and AI models",
    "Technology": "technology, software, computers, internet, and cybersecurity",
    "Business": "business, finance, markets, company earnings, stocks, and prices",
    "Politics": "politics, government, elections, politicians, and parliament",
    "Science & Health": "science, medical research, hospitals, diseases, and health",
    "Sports": "sports, cricket, football, tennis, and sporting competitions",
    "General": "general news that does not primarily fit the other categories",
}

_classifier = None


def get_classifier():
    global _classifier

    if _classifier is None:
        device = "mps" if torch.backends.mps.is_available() else "cpu"

        _classifier = pipeline(
            "zero-shot-classification",
            model=MODEL_NAME,
            device=device,
        )

    return _classifier


def classify_headline_ai(title):
    result = get_classifier()(
        title,
        candidate_labels=list(CATEGORY_DESCRIPTIONS.values()),
        hypothesis_template="This news headline is about {}.",
    )

    best_description = result["labels"][0]

    category = next(
        name
        for name, description in CATEGORY_DESCRIPTIONS.items()
        if description == best_description
    )

    score = result["scores"][0]

    return category, float(score)
