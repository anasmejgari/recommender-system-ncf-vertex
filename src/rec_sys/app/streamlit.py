import streamlit as st

user_profile = st.sidebar.text_input("Please provide a user profile ID: ")
show_previously_watched = st.sidebar.checkbox(
    "Show previously watched movies", key="disabled"
)

watched_movies = [
    (
        "Movie 1",
        "https://www.themoviedb.org/t/p/w1280/7nHl3OHUSTHgslQxJUzNSy9vxqo.jpg",
        4,
    ),
    (
        "Movie 2",
        "https://www.themoviedb.org/t/p/w1280/7nHl3OHUSTHgslQxJUzNSy9vxqo.jpg",
        2,
    ),
    (
        "Movie 3",
        "https://www.themoviedb.org/t/p/w1280/7nHl3OHUSTHgslQxJUzNSy9vxqo.jpg",
        3,
    ),
    (
        "Movie 4",
        "https://www.themoviedb.org/t/p/w1280/7nHl3OHUSTHgslQxJUzNSy9vxqo.jpg",
        4,
    ),
    (
        "Movie 5",
        "https://www.themoviedb.org/t/p/w1280/7nHl3OHUSTHgslQxJUzNSy9vxqo.jpg",
        1,
    ),
]

if "last_movie_showed_rated" not in st.session_state:
    st.session_state.last_movie_showed_rated = -1

if user_profile:
    if show_previously_watched:
        st.title("You previously watched ..")
        st.write("I will show recommended movies")

        # st.session_state.last_movie_showed_rated += 3
        n = min(len(watched_movies) - 1, st.session_state.last_movie_showed_rated + 3)

        for row in range(1 + n // 3):
            columns = st.columns(3)

            for idx, col in enumerate(columns):
                movie = row * 3 + idx

                if movie < len(watched_movies):
                    with col:
                        st.image(watched_movies[movie][1])
                        st.header(f"{watched_movies[movie][0]}")
                        st.write(f"Your rating: {watched_movies[movie][2]} / 5")

        if n != len(watched_movies):
            _, c1 = st.columns([5, 1])
            c1.button("Show more")
            st.session_state.last_movie_showed_rated += 3

        st.divider()

    st.title("Our recommendations: ")
    st.write("You entered: ", user_profile)
