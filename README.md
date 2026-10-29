# News Researcher

A Python project for collecting, classifying, storing, and retrieving news headlines from RSS feeds.

The project explores practical engineering concepts including source traceability, duplicate prevention, publication-date ordering, local persistence, and automated testing.

## Features

- Fetch headlines from configured RSS feeds.
- Filter sources using configured India, US, and Global labels.
- Classify headlines using a keyword-based classifier.
- Store stories locally in SQLite and avoid duplicate URLs.
- Browse previously saved stories.
- Filter stories by category.
- Run automated unit tests.
- Experiment with an optional zero-shot machine-learning classifier.

## Requirements

- Python 3
- Internet access to retrieve RSS feeds

The core application uses `feedparser` and `certifi`, listed in `requirements.txt`.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the core dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run the application

```bash
python run_researcher.py
```

Follow the prompts to select latest headlines or previously saved stories, choose a source region, and select how many stories to display.

To filter by category, for example:

```bash
python run_researcher.py --category Technology
```

Category names must match the classifier's output, such as `AI`, `Technology`, `Business`, `Politics`, `Science & Health`, `Sports`, or `General`.

## Data storage

Stories are stored in a local SQLite database named `news.db`, created beside the application files. The database is intentionally excluded from version control.

The configured source region describes the source's assigned label; it does not guarantee that every story concerns that geographic region.

## Classification

The default classifier uses keyword rules. It is lightweight and easy to inspect, but its results depend on the configured keywords and their order. It can misclassify ambiguous headlines.

An optional experimental classifier uses the Hugging Face Transformers pipeline with the `facebook/bart-large-mnli` model. Its dependencies are listed in `requirements-ai.txt`.

To install the optional dependencies:

```bash
python -m pip install -r requirements-ai.txt
```

The experimental classifier and comparison script are separate from the default application workflow. Model scores are not necessarily calibrated probabilities, and the small sample in `compare_classifiers.py` is a demonstration, not a rigorous benchmark.

## Tests

Run the automated tests with:

```bash
python -m unittest discover -s tests -v
```

## Limitations

- Feed availability and published fields vary by source.
- Headline categories are estimates, not verified labels.
- Publication-date ordering depends on parseable feed timestamps.
- The application does not verify the factual accuracy of news articles.
- The project is an evolving personal engineering project, not a production news-verification system.
