
import streamlit as st

from news_fetcher import fetch_headlines
from news_database import (
    save_stories,
    get_stories,
    get_database_stats,
    get_source_health,
    cleanup_source_health_history,
)


# Page setup
st.set_page_config(
    page_title="News Researcher",
    page_icon="📰",
    layout="wide",
)

st.title("📰 News Researcher")
st.caption("Your personal news collection and research dashboard")


# Prepare the database
cleanup_source_health_history(days=30)

# Show database statistics
stats = get_database_stats()

col1, col2 = st.columns(2)

col1.metric("Saved Stories", stats["record_count"])
col2.metric("Maximum Storage", "5,000 stories")


# Main sections
latest_tab, saved_tab, health_tab = st.tabs([
    "Get Latest Headlines",
    "Browse Saved Stories",
    "Source Health",
])


# Section 1: Fetch latest headlines
with latest_tab:
    st.header("Get Latest Headlines")
    st.write("Fetch fresh headlines from your configured news sources.")

    if st.button("Fetch Latest Headlines", type="primary"):
        with st.spinner("Fetching headlines from news sources..."):
            headlines = fetch_headlines()
            saved_count = save_stories(headlines)

        st.success(
            f"Fetched {len(headlines)} headlines. "
            f"Saved {saved_count} new stories."
        )

        if headlines:
            st.subheader("Recently fetched headlines")

            for story in headlines:
                st.write(f"**{story['title']}**")
                st.caption(
                    f"{story['source']} | "
                    f"{story.get('region', 'Unknown')} | "
                    f"{story.get('published', 'Date unavailable')}"
                )
                st.link_button("Read original article", story["link"])
                st.divider()


# Section 2: Browse saved stories
with saved_tab:
    st.header("Browse Saved Stories")
    st.write("Explore the stories collected in your database.")

    stories = get_stories(limit=5000)

    st.write(f"Total stories available: {len(stories)}")

    if stories:
        for story in stories:
            st.subheader(story["title"])

            st.caption(
                f"Source: {story['source']} | "
                f"Region: {story.get('region') or 'Unknown'} | "
                f"Category: {story.get('category') or 'Unclassified'}"
            )

            st.caption(
                f"Published: {story.get('published') or 'Date unavailable'}"
            )

            st.link_button("Read original article", story["url"])
            st.divider()
    else:
        st.info("No saved stories yet. Fetch the latest headlines first.")


# Section 3: Source health
with health_tab:
    st.header("News Source Health")

    sources = get_source_health()

    if sources:
        for source in sources:
            st.write(f"**{source['source']}**")

            st.write(
                f"Status: {source['status']} | "
                f"Headlines: {source['headlines_count']} | "
                f"Last checked: {source['checked_at']}"
            )

            if source["error_message"]:
                st.warning(source["error_message"])

            st.divider()
    else:
        st.info("No source health records available yet.")
