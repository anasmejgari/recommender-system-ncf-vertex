"""Module for the frontend."""

import math

import streamlit as st

from rec_sys.app.movie import Movie
from rec_sys.app.utils import get_recommended_movies

# Top-centered title
st.markdown(
    "<h1 style='text-align: center;'>Welcome back 👋</h1>", unsafe_allow_html=True
)
watched_movies: list[Movie] = []

# Initialize session state counters if not already set.
if "rated_count" not in st.session_state:
    st.session_state.rated_count = 3
if "rec_count" not in st.session_state:
    st.session_state.rec_count = 3

# Sidebar inputs
user_profile = st.sidebar.text_input("Please provide a user profile ID:")
show_previously_watched = st.sidebar.checkbox("Show previously watched movies")

if user_profile:
    # Rated movies section (only if checkbox is checked)
    if show_previously_watched:
        st.subheader("Your Liked Movies")
        total_rated = min(len(watched_movies), st.session_state.rated_count)
        rows_rated = math.ceil(total_rated / 3)
        idx = 0
        # Display rated movies in rows of 3 columns
        for _ in range(rows_rated):
            cols = st.columns(3)
            for col in cols:
                if idx < total_rated:
                    with col:
                        st.image(watched_movies[idx].cover)
                        st.header(watched_movies[idx].title)
                    idx += 1
        # Button under the rated movies list.
        if (st.session_state.rated_count < len(watched_movies)) and (
            st.button("Show more rated movies", key="rated_more")
        ):
            st.session_state.rated_count += 3

        st.divider()

    recommended_movies = get_recommended_movies(user_profile)
    # Recommended movies section.
    st.subheader("Based on what you watched recently, we recommend you ")
    st.write("User Profile:", user_profile)
    total_rec = min(len(recommended_movies), st.session_state.rec_count)
    rows_rec = math.ceil(total_rec / 3)
    idx = 0
    # Display recommended movies in rows of 3 columns
    for _ in range(rows_rec):
        cols = st.columns(3)
        for col in cols:
            if idx < total_rec:
                with col:
                    st.image(recommended_movies[idx].cover, use_container_width=True)
                    st.subheader(recommended_movies[idx].title)
                    st.text(recommended_movies[idx].genres)
                    st.text(recommended_movies[idx].year)
                idx += 1
    # Button under the recommended movies list.
    if (st.session_state.rec_count < len(recommended_movies)) and (
        st.button("Show more recommended movies", key="rec_more")
    ):
        st.session_state.rec_count += 3
else:
    st.info("Please enter a User Profile ID in the sidebar.")
