# News Researcher

A personal news research application built with Python, RSS feeds, SQLite, and Streamlit.

The application collects news headlines from configured sources, classifies them, stores them locally, and provides a browser-based dashboard to retrieve and browse previously collected stories.

The project is also an exercise in practical software engineering: source traceability, duplicate prevention, publication-date ordering, local persistence, source monitoring, and automated testing.

## Features

### News collection
- Fetch headlines from 11 configured RSS sources.
- Sources are grouped under India, US, and Global regions.
- Fetch sources individually and continue when a source fails.
- Record the latest health status of each source.

### Classification and storage
- Classify headlines using a keyword-based classifier.
- Store stories in a local SQLite database.
- Prevent duplicate stories using their article URLs.
- Order stories by publication date.
- Retain up to 5,000 stories, removing older records in batches.

### Browser dashboard

The application includes a Streamlit dashboard with three sections:

1. **Get Latest Headlines** — fetch fresh headlines from configured sources and save new stories.
2. **Browse Saved Stories** — browse previously collected headlines, including their source, region, category, publication date, and original article link.
3. **Source Health** — view the latest recorded status of configured RSS sources.

The saved-story archive supports:
- Keyword search across headlines.
- Filtering by region, category, and source.
- Filtering by publication date range.
- Sorting by newest or oldest first.
- A **Clear All Filters** option to restore the default view.

### Terminal application

The original interactive Python application is retained and can still be run from Terminal.

### Testing
- Automated unit tests for classification, database operations, and RSS fetching.
- Tests can be run locally using Python's `unittest` framework.

## Technology

- Python
- Streamlit — browser-based user interface
- SQLite — local story database
- Feedparser — RSS feed parsing
- Certifi — trusted SSL certificates
- Unittest — automated testing

## Requirements

- Python 3 installed on macOS.
- Internet access for retrieving RSS feeds.
- macOS for the supplied double-click launcher.

The setup script checks for Python 3 and creates the application's virtual environment. It does not install Python itself.

## Installation on macOS

### Step 1: Download the application

Open Terminal and run:

```bash
cd ~
git clone https://github.com/SatyaPatnala5/news-researcher.git
cd news-researcher
```

### Step 2: Install the application

Open the `news-researcher` folder in Finder.

Double-click:

`setup_news.command`

The setup script will:
- Check whether Python 3 is installed.
- Create the application's virtual environment if it does not already exist.
- Install the required application dependencies.

Wait until the setup displays:

`SETUP COMPLETED SUCCESSFULLY`

If Python 3 is not installed, install it and run the setup script again.

### Step 3: Start the application

Double-click:

`start_news.command`

Your browser should open the News Researcher dashboard automatically.

If macOS displays a security warning, check the file and its origin before allowing it to run.

## Running the browser dashboard

### Option 1: Double-click launcher

Open the `news-researcher` folder in Finder and double-click:

`start_news.command`

The launcher activates the project's virtual environment and starts Streamlit. Your browser should open the dashboard automatically.

### Option 2: Run from Terminal

From the project folder, activate the virtual environment and start the dashboard:

```bash
source .venv/bin/activate
streamlit run app.py
```

Open the local URL displayed by Streamlit, usually:

`http://localhost:8501`

Keep the Terminal process running while using the dashboard.

To stop the application, return to the Terminal window running Streamlit and press:

`Control + C`

Closing the browser tab alone does not stop the Streamlit server.

## Running the original Terminal application

The original interactive application is still available:

```bash
source .venv/bin/activate
python run_researcher.py
```

Follow the prompts to retrieve headlines or browse previously saved stories.

## Data storage

Stories are stored in a local SQLite database named `news.db`, created beside the application files.

The database is local to each installation and is intentionally excluded from version control. It is not automatically shared or synchronised between computers.

The application retains up to 5,000 stories. Older stories are removed in batches when the retention limit is exceeded.

Source-health history is retained for 30 days. The latest health status for each source is maintained separately.

## Classification

The default classifier uses keyword rules. It is lightweight and easy to inspect, but its results depend on the configured keywords and their order. Ambiguous headlines may be misclassified.

An optional experimental classifier uses Hugging Face Transformers with the `facebook/bart-large-mnli` model. Its dependencies are listed separately in `requirements-ai.txt`.

To install the optional experimental dependencies:

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
- A source's configured region is its assigned label; it does not guarantee that every story concerns that region.
- Headline categories are estimates, not verified labels.
- Publication-date ordering depends on parseable feed timestamps.
- The application does not verify the factual accuracy of news articles.
- The dashboard is a local application, not a hosted multi-user service.
- The project is an evolving personal engineering project, not a production news-verification system.

## Future improvements

Potential future enhancements include:

- More flexible source management.
- Improved headline classification.
- Optional AI-assisted research capabilities.
- Easier installation and distribution for other Mac users.
