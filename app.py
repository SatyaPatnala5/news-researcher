
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


def clear_filters():
    st.session_state["keyword"] = ""
    st.session_state["selected_region"] = "All"
    st.session_state["selected_category"] = "All"
    st.session_state["selected_source"] = "All"
    st.session_state["sort_order"] = "newest"
    st.session_state["date_range"] = ()


# Section 2: Browse saved stories
with saved_tab:
    st.header("Browse Saved Stories")
    st.write("Explore the stories collected in your database.")

    # Load all saved stories to populate filter choices
    all_stories = get_stories(limit=5000)

    st.button(
        "Clear All Filters",
        on_click=clear_filters,
    )

    # Search and filter controls
    keyword = st.text_input("Search headlines", key="keyword")

    regions = ["All"] + sorted({
        story.get("region")
        for story in all_stories
        if story.get("region")
    })

    categories = ["All"] + sorted({
        story.get("category")
        for story in all_stories
        if story.get("category")
    })

    sources = ["All"] + sorted({
        story.get("source")
        for story in all_stories
        if story.get("source")
    })

    col1, col2 = st.columns(2)

    with col1:
        selected_region = st.selectbox(
            "Region", regions, key="selected_region"
        )
        selected_category = st.selectbox(
            "Category", categories, key="selected_category"
        )
        selected_source = st.selectbox(
            "Source", sources, key="selected_source"
        )

    with col2:
        sort_order = st.selectbox(
            "Sort by",
            ["newest", "oldest"],
            format_func=lambda value: (
                "Newest first" if value == "newest" else "Oldest first"
            ),
            key="sort_order",
        )

        date_range = st.date_input(
            "Publication date range",
            value=(),
            key="date_range",
        )

    # Apply selected filters
    filter_options = {
        "limit": 5000,
        "keyword": keyword or None,
        "region": None if selected_region == "All" else selected_region,
        "category": None if selected_category == "All" else selected_category,
        "source": None if selected_source == "All" else selected_source,
        "sort_order": sort_order,
    }

    if len(date_range) == 2:
        filter_options["start_date"] = date_range[0].isoformat()
        filter_options["end_date"] = date_range[1].isoformat()

    stories = get_stories(**filter_options)

    st.write(f"Matching stories: {len(stories)}")

    
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
