
import argparse

from news_fetcher import fetch_headlines
from news_database import (
    save_stories,
    get_stories,
    print_source_health,
    cleanup_source_health_history,
)


def choose_mode():
    print("\nChoose what you want to do:")
    print("1. Get latest headlines")
    print("2. Browse previously saved stories")
    print("3. View news source health")

    while True:
        choice = input("Enter 1, 2, or 3 [1]: ").strip() or "1"

        if choice == "1":
            return "latest"
        if choice == "2":
            return "saved"
        if choice == "3":
            return "health"

        print("Please enter 1, 2, or 3.")

def choose_region():
    print("\nChoose news coverage:")
    print("1. India")
    print("2. US")
    print("3. Global")
    print("4. All regions")

    choices = {
        "1": "India",
        "2": "US",
        "3": "Global",
        "4": "All",
    }

    while True:
        choice = input("Enter 1-4 [4]: ").strip() or "4"
        if choice in choices:
            return choices[choice]
        print("Please enter 1, 2, 3, or 4.")


def choose_story_count():
    while True:
        answer = input(
            "\nHow many stories do you want to display? [10]: "
        ).strip()

        if not answer:
            return 10

        try:
            count = int(answer)
            if count > 0:
                return count
        except ValueError:
            pass

        print("Please enter a whole number greater than zero.")


def display_stories(stories):
    if not stories:
        print("\nNo matching stories were found.")
        return

    for number, story in enumerate(stories, start=1):
        print(f"\n{number}. {story['title']}")
        print(f"   Source: {story['source']}")
        print(f"   Region: {story.get('region') or 'Unknown'}")
        print(f"   Category: {story.get('category') or 'Uncategorised'}")
        print(f"   Published: {story.get('published') or 'Unknown date'}")
        print(f"   Link: {story.get('url') or story.get('link', '')}")


def main():
    parser = argparse.ArgumentParser(description="News Researcher")
    parser.add_argument(
        "--category",
        type=str,
        help="Show stories from a specific category",
    )
    args = parser.parse_args()

    print("\n=== News Researcher ===")
    deleted_count = cleanup_source_health_history(30)

    if deleted_count > 0:
        print(f"Cleaned up {deleted_count} old health-history records.")

    mode = choose_mode()

    if mode == "health":
        print_source_health()
        return

    region = choose_region()
    story_count = choose_story_count()


    print(f"\nMode: {'Latest headlines' if mode == 'latest' else 'Saved stories'}")
    print(f"Coverage: {region}")

    if mode == "latest":
        print("\nFetching headlines...\n")

        try:
            stories = fetch_headlines(story_count, region=region)
        except Exception as error:
            print(f"Could not fetch headlines: {error}")
            return

        fetched_count = len(stories)
        new_count = save_stories(stories)

        if args.category:
            stories = [
                story for story in stories
                if story.get("category") == args.category
            ]

        stories = stories[:story_count]

        print(f"Headlines fetched: {fetched_count}")
        print(f"New stories saved: {new_count}")
        print(f"Stories displayed: {len(stories)}")
        print("\n=== Latest Headlines ===")

        display_stories(stories)

    else:
        print("\nReading saved stories...\n")

        saved_stories = get_stories(500, category=args.category)

        if region != "All":
            saved_stories = [
                story for story in saved_stories
                if (story.get("region") or "").lower() == region.lower()
            ]

        saved_stories = saved_stories[:story_count]

        print(f"Stories displayed: {len(saved_stories)}")
        print("\n=== Previously Saved Stories ===")

        display_stories(saved_stories)


if __name__ == "__main__":
    main()

