
import streamlit as st
import pandas as pd
from recommender import recommend_movies, get_all_movie_titles,bert_search
from tmdb import (get_movie_poster,
                  get_trailer_link,
                  get_bollywood_movies,
                  get_movies_by_language ,
                  get_watch_providers ,
                  get_movie_overview ,
                  get_cast_and_crew,
                  get_movie_details
                  )
from tmdb import search_movie_tmdb
from auth import login, signup
from database import (
    add_watch_history,
    get_watch_history,
    add_favorite,
    remove_favorite,
    get_favorites,
    is_favorite,
    clear_watch_history,
    delete_from_history
)


def favorite_toggle(movie):

    movie_name = movie[:-1] if movie[-1].isdigit() else movie

    unique_key = movie + "_" + str(hash(movie + st.session_state.username))

    if is_favorite(st.session_state.username, movie_name):

        if st.button("❤️", key=f"fav_remove_{unique_key}"):

            remove_favorite(st.session_state.username, movie_name)
            st.rerun()

    else:

        if st.button("🤍", key=f"fav_add_{unique_key}"):

            add_favorite(st.session_state.username, movie_name)
            st.rerun()


st.set_page_config(page_title="Movie Recommendation System", layout="wide")

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None


# ---------------- LOGIN ----------------
if not st.session_state.logged_in:

    st.title("🎬 Movie Recommendation System")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if login(u, p):
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")

        if st.button("Signup"):
            if signup(nu, np):
                st.success("Account created. Login now.")
            else:
                st.error("Username exists")

    st.stop()


# ---------------- LOAD DATA ----------------
movies_df = pd.read_csv("data/movies.csv")
ratings_df = pd.read_csv("data/ratings.csv")

ratings_avg = ratings_df.groupby("movieId")["rating"].mean().reset_index()

movies_df = movies_df.merge(ratings_avg, on="movieId", how="left")
movies_df["rating"] = movies_df["rating"].fillna(0)

# ---------------- GENRE LIST ----------------
all_genres = (
    movies_df["genres"]
    .str.split("|")
    .explode()
    .dropna()
)

all_genres = [g for g in all_genres.unique() if g != "(no genres listed)"]



# ---------------- NAVBAR STYLE ----------------
st.markdown("""
<style>
.navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 70px;
    background-color: #181818;
    border-bottom: 2px solid #2a2a2a;
    z-index: 999;
    padding: 10px 20px;
}

/* push content below navbar */
.main-content {
    margin-top: 90px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- NAVBAR ----------------
st.markdown('<div class="navbar">', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([2,5,1,2])

# 🎬 App Name
with col1:
    st.markdown("<h4 style='margin-top:8px;'>🎬 Movie Recommender</h4>", unsafe_allow_html=True)

# 🔍 Search
with col2:
    search_movie = st.selectbox(
        "",
        get_all_movie_titles(),
        index=None,
        placeholder="🔍 Search movies..."
    )
    # search_movie = st.text_input("🔍 Search any movie...")
# 🔘 Button
with col3:
    st.markdown("<div style='margin-top:8px;'>", unsafe_allow_html=True)
    search_clicked = st.button("Recommend")
    st.markdown("</div>", unsafe_allow_html=True)

# 👤 Profile
with col4:
    st.markdown(
        f"<h4 style='text-align:right; margin-top:10px;'>👤 Welcome {st.session_state.username}</h4>",
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- SPACE BELOW ----------------
st.markdown('<div class="main-content"></div>', unsafe_allow_html=True)

# ---------------- SEARCH ACTION ----------------
# if search_clicked and search_movie:
#     st.session_state.selected_movie = search_movie



if search_clicked and search_movie:

    all_movies = get_all_movie_titles()

    # ✅ Case 1: Movie exists in dataset
    if search_movie in all_movies:
        st.session_state.selected_movie = search_movie

    else:
        # ❌ Not in dataset → search TMDB
        tmdb_movie = search_movie_tmdb(search_movie)

        if tmdb_movie:
            st.session_state.selected_movie = tmdb_movie["title"]
            st.session_state.external_movie = tmdb_movie   # store API result
        else:
            st.error("Movie not found anywhere 😢")
# ---------------- SIDEBAR ----------------
st.sidebar.title("🎬 Navigation")

page = st.sidebar.radio(
    "Go to",
    # ["Home", "Recommend", "Top Rated", "Favorites","Watch History","🤖 Use AI"]
    ["Home", "Top Rated", "Favorites", "Watch History", "🤖 Use AI"]

)

st.sidebar.markdown("###  Filters")

# # 🎭 Multi Genre Filter
genre_choice = st.sidebar.multiselect(
    "🎭 Browse by Genre",
    sorted(all_genres)
)
# genre_choice = st.sidebar.selectbox(
#     "🎭 Browse by Genre",
#     ["None"] + sorted(all_genres)
# )
lang = st.sidebar.selectbox(
    "🌐 Select Language",
    ["None", "Hindi", "English", "Marathi", "Gujarati"]
)
# -------- YEAR COLUMN --------
movies_df["year"] = movies_df["title"].str.extract(r"\((\d{4})\)")
movies_df["year"] = pd.to_numeric(movies_df["year"], errors="coerce")

# -------- SLIDER --------
min_year = int(movies_df["year"].dropna().min())
max_year = int(movies_df["year"].dropna().max())

year_range = st.sidebar.slider(
    "📅 Year Range",
    min_year,
    max_year,
    (1995, 2026)
)
# ⭐ Rating filter
min_rating = float(movies_df["rating"].min())
max_rating = float(movies_df["rating"].max())

rating_range = st.sidebar.slider(
    "⭐ Rating Range",
    min_rating,
    max_rating,
    (0.0, 5.0)
)

st.sidebar.markdown("---")
st.sidebar.write("👤", st.session_state.username)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()



# ---------------- GLOBAL FILTER ----------------
filtered_movies_df = movies_df.copy()

# 🎭 Multi Genre filter
if genre_choice:

    pattern = "|".join(genre_choice)   # convert list → string

    filtered_movies_df = filtered_movies_df[
        filtered_movies_df["genres"].str.contains(pattern, case=False, na=False)
    ]

# 📅 Year filter
filtered_movies_df = filtered_movies_df[
    (filtered_movies_df["year"] >= year_range[0]) &
    (filtered_movies_df["year"] <= year_range[1])
]
filtered_movies_df = filtered_movies_df[
    (filtered_movies_df["rating"] >= rating_range[0]) &
    (filtered_movies_df["rating"] <= rating_range[1])
]
# ---------------- MOVIE DETAIL PAGE ----------------
if st.session_state.selected_movie:

    movie_title = st.session_state.selected_movie

    add_watch_history(
        st.session_state.username,
        movie_title
    )
    ## movie = filtered_movies_df[movies_df["title"] == movie_title].iloc[0]
    movie = None

    if movie_title in movies_df["title"].values:
        movie = filtered_movies_df[movies_df["title"] == movie_title].iloc[0]
    # st.title(movie_title)
    clean_title = movie_title.split("(")[0].strip()
    st.title(clean_title)

    if movie is None:
        st.warning("⚠️ This movie is not in dataset (limited features available)")
    col1, col2 = st.columns([1,2])

    with col1:
        # st.image(get_movie_poster(movie_title))
        poster = get_movie_poster(movie_title)
        st.image(poster)

    with col2:

        # -------- ROW 1 --------
        year = ""
        if "(" in movie_title:
            year = movie_title.split("(")[-1].replace(")", "")

        release_date, runtime = get_movie_details(movie_title)
        col1, col2 = st.columns(2)

        with col1:
            if movie is not None:
                st.markdown(f"⭐ **Rating:**  {round(movie['rating'], 2)} / 5")
            else:
                st.markdown("⭐ **Rating:** Not available")
            ## st.markdown(f"⭐ **Rating:**  {round(movie['rating'],2)} / 5")

        with col2:
            st.markdown(f"⏱ **Runtime:** {runtime} min")

        # -------- ROW 2 --------
        col3, col4 = st.columns(2)

        with col3:
            if movie is not None:
                st.markdown(f"🎭 **Genres:**  {movie['genres']}")
            else:
                st.markdown("🎭 **Genres:** Not available")
            ## st.markdown(f"🎭 **Genres:**  {movie['genres']}")

        with col4:
            st.markdown(f"📅 **Year:** {year}")
        trailer = get_trailer_link(movie_title)

        if trailer:
            # st.link_button("🎬 Watch Trailer",trailer)
            st.markdown(f"""
            <a href="{trailer}" target="_blank" style="text-decoration:none;">
                <div style="
                    display:inline-block;
                    background:#1f1f1f;
                    border:1px solid #333;
                    padding:10px 16px;
                    border-radius:10px;
                    color:white;
                    font-weight:500;
                ">
                    🎬 Watch Trailer
                </div>
            </a>
            """, unsafe_allow_html=True)
        else:
            st.write("Trailer not available")
        overview = get_movie_overview(movie_title)

        st.markdown("##### 📝 Overview")
        st.markdown(f"""
        <div style='
            background-color:#1e1e1e;
            padding:15px;
            border-radius:10px;
            line-height:1.6;
        '>
        {overview}
        </div>
        """, unsafe_allow_html=True)
        cast, crew = get_cast_and_crew(movie_title)

        # 🎭 CAST
        if cast:
            st.markdown("##### 🎭 Cast")
            st.write(", ".join(cast))

        # 🎬 CREW
        if crew:
            st.markdown("##### 🎬 Crew")
            for c in crew:
                st.write(c)

        providers = get_watch_providers(movie_title)

        if providers:
            st.markdown("#### 📺 Available on")
            st.write(", ".join(providers))
        st.markdown("---")
        # -------- FAVORITE BUTTON --------
        if is_favorite(st.session_state.username, movie_title):

            if st.button("💔 Remove from Favorites"):
                remove_favorite(st.session_state.username, movie_title)
                st.success("Removed from Favorites")
                st.rerun()

        else:

            if st.button("❤️ Add to Favorites"):
                add_favorite(st.session_state.username, movie_title)
                st.success("Added to Favorites")
                st.rerun()


    st.markdown("---")

    st.subheader("🍿 Recommended Movies")

    recs = recommend_movies(movie_title)

    cols = st.columns(5)

    for i, (_, row) in enumerate(recs.iterrows()):
        with cols[i % 5]:

            # st.image(get_movie_poster(row["title"]))
            poster = get_movie_poster(row["title"])
            st.image(poster)
            if st.button(row["title"], key=f"detail_{row['title']}"):

                st.session_state.selected_movie = row["title"]
                st.rerun()

    if st.button("⬅ Back"):
        st.session_state.selected_movie = None
        st.rerun()

    st.stop()

# ---------------- GENRE PAGE ----------------

if genre_choice:

    st.title(f"🎭 {' | '.join(genre_choice)} Movies")

    # 🔥 Create pattern (Action|Comedy)
    pattern = "|".join(genre_choice)

    genre_movies = filtered_movies_df[
        filtered_movies_df["genres"].str.contains(pattern, case=False, na=False)
    ]

    genre_movies = genre_movies.sort_values(
        by="rating",
        ascending=False
    ).head(20)

    cols = st.columns(5)

    for i, row in genre_movies.iterrows():

        with cols[i % 5]:

            poster = get_movie_poster(row["title"])
            st.image(poster)

            favorite_toggle(row["title"])

            if st.button(row["title"], key=f"genre_{row['title']}"):
                st.session_state.selected_movie = row["title"]
                st.rerun()

            st.write(f"⭐ {round(row['rating'],2)}")

    st.stop()


# ---------------- HOME PAGE ----------------
if page == "Home":

    st.title("🎬 Movie Explorer")
    st.caption("Discover movies based on popularity and hidden gems")

    st.subheader("🔥 Most Popular Movies")

    popularity = ratings_df.groupby("movieId").size().reset_index(name="count")

    popular_movies =filtered_movies_df.merge(popularity, on="movieId")

    popular_movies = popular_movies.sort_values(
        by="count",
        ascending=False
    ).head(10)

    cols = st.columns(5)

    for i, row in popular_movies.iterrows():

        with cols[i % 5]:

            # st.image(get_movie_poster(row["title"]))
            poster = get_movie_poster(row["title"])
            st.image(poster)
            favorite_toggle(row["title"])
            if st.button(row["title"], key=f"popular_{row['title']}"):
                st.session_state.selected_movie = row["title"]
                st.rerun()

            st.write(f"⭐ {round(row['rating'],2)}")


    st.markdown("---")
    st.subheader("💎 Hidden Gems")

    rating_count = ratings_df.groupby("movieId").size().reset_index(name="count")

    hidden = filtered_movies_df.merge(rating_count, on="movieId")

    hidden = hidden[
        (hidden["rating"] > 4) & (hidden["count"] < 50)
    ].head(10)

    cols = st.columns(5)

    for i, row in hidden.iterrows():

        with cols[i % 5]:

            # st.image(get_movie_poster(row["title"]))
            poster = get_movie_poster(row["title"])
            st.image(poster)

            favorite_toggle(row["title"])
            if st.button(row["title"], key=f"hidden_{row['title']}"):
                st.session_state.selected_movie = row["title"]
                st.rerun()

            st.write(f"⭐ {round(row['rating'],2)}")

    # ---------------- BOLLYWOOD MOVIES ---------------
    st.markdown("---")
    st.subheader("🇮🇳 Bollywood Movies")

    bolly = get_bollywood_movies()

    cols = st.columns(5)

    for i, movie in enumerate(bolly):
        with cols[i % 5]:
            poster = get_movie_poster(movie["title"])
            st.image(poster, width=200)
            st.write(movie["title"])
    st.markdown('</div>', unsafe_allow_html=True)


    st.markdown("---")
    st.subheader("🎲 Random Picks")

    random_movies = filtered_movies_df.sample(5)

    cols = st.columns(5)

    for i, row in random_movies.iterrows():

        with cols[i % 5]:

            # st.image(get_movie_poster(row["title"]))
            poster = get_movie_poster(row["title"])
            st.image(poster)

            favorite_toggle(row["title"])
            if st.button(row["title"], key=f"random_{row['title']}"):
                st.session_state.selected_movie = row["title"]
                st.rerun()

            st.write(f"⭐ {round(row['rating'],2)}")
    history = get_watch_history(st.session_state.username)

    if history:

        st.markdown("---")
        st.subheader("🎯 Because You Watched")

        recs_list = []

        for movie in history[-3:]:
            recs = recommend_movies(movie)
            recs_list.append(recs)

        import pandas as pd

        final_recs = pd.concat(recs_list)

        # ✅ REMOVE DUPLICATES (THIS LINE YOU ASKED ABOUT)
        final_recs = final_recs.drop_duplicates(subset="title")

        # ❗ Remove already watched movies (important)
        final_recs = final_recs[
            ~final_recs["title"].isin(history)
        ]

        # ✅ LIMIT RESULTS
        final_recs = final_recs.head(10)

        cols = st.columns(5)

        for i, (_, row) in enumerate(final_recs.iterrows()):

            with cols[i % 5]:

                poster = get_movie_poster(row["title"])
                st.image(poster)

                favorite_toggle(row["title"])

                if st.button(row["title"], key=f"bw_{row['title']}"):
                    st.session_state.selected_movie = row["title"]
                    st.rerun()

                # st.write(f"⭐ {round(row['rating'], 2)}")



# ---------------- RECOMMEND PAGE ----------------
elif page == "Recommend":

    st.title("🍿 Movie Recommendation")

    movie = st.selectbox(
        "Select a movie",
        get_all_movie_titles()
    )

    if "recommendations" not in st.session_state:
        st.session_state.recommendations = None

    if st.button("Recommend"):

        recs = recommend_movies(movie)

        st.session_state.recommendations = recs


    if st.session_state.recommendations is not None:

        recs = st.session_state.recommendations

        cols = st.columns(5)

        for i, (_, row) in enumerate(recs.iterrows()):

            with cols[i % 5]:

                # st.image(get_movie_poster(row["title"]))
                poster = get_movie_poster(row["title"])
                st.image(poster)
                favorite_toggle(row["title"])
                if st.button(row["title"], key=f"rec_{row['title']}"):

                    st.session_state.selected_movie = row["title"]
                    st.rerun()


# ---------------- TOP RATED PAGE ----------------
elif page == "Top Rated":

    st.title("⭐ Top Rated Movies")

    top_movies = filtered_movies_df.sort_values(
        by="rating",
        ascending=False
    ).head(20)

    cols = st.columns(5)

    for i, row in top_movies.iterrows():

        with cols[i % 5]:

            # st.image(get_movie_poster(row["title"]))
            poster = get_movie_poster(row["title"])
            st.image(poster)

            favorite_toggle(row["title"])
            if st.button(row["title"], key=f"top_{row['title']}"):

                st.session_state.selected_movie = row["title"]
                st.rerun()

            st.write(f"⭐ {round(row['rating'],2)}")


# ---------------- FAVORITES PAGE ----------------
elif page == "Favorites":

    st.title("❤️ Your Favorite Movies")

    favorites = get_favorites(st.session_state.username)

    if not favorites:
        st.info("No favorite movies yet")

    else:

        cols = st.columns(5)

        for i, movie in enumerate(favorites):

            with cols[i % 5]:

                st.image(get_movie_poster(movie))

                if st.button(movie, key=f"fav_{movie}"):

                    st.session_state.selected_movie = movie
                    st.rerun()
 #  ------language filter
if lang != "None":

    lang_map = {
        "Hindi": "hi",
        "English": "en",
        "Marathi": "mr",
        "Gujarati": "gu"
    }

    movies = get_movies_by_language(lang_map[lang])

    st.subheader(f"🎬 {lang} Movies")

    cols = st.columns(5)

    for i, movie in enumerate(movies):
        with cols[i % 5]:
            poster = get_movie_poster(movie["title"])
            st.image(poster, width=200)
            st.write(movie["title"])



elif page == "Watch History":

    st.title("🕘 Watch History")



    # ✅ FETCH DATA AFTER BUTTON
    history = get_watch_history(st.session_state.username)

    if not history:
        st.info("No watch history yet")

    else:

        cols = st.columns(5)

        for i, movie in enumerate(history):

            with cols[i % 5]:

                poster = get_movie_poster(movie)
                st.image(poster, width=180)

                st.markdown(
                    f"<div style='height:50px; overflow:hidden'>{movie}</div>",
                    unsafe_allow_html=True
                )

                # 👇 buttons in one row
                col_btn1, col_btn2 = st.columns(2)

                with col_btn1:
                    if st.button("View", key=f"view_{i}"):
                        st.session_state.selected_movie = movie
                        st.rerun()

                with col_btn2:
                    if st.button("🗑", key=f"delete_{i}"):
                        delete_from_history(st.session_state.username, movie)
                        st.rerun()

    st.markdown("""
    <style>
    button[kind="secondary"][data-testid="baseButton-clear_btn"] {
        background-color: #e50914;
        color: white;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    if st.button("🗑 Clear All History", key="clear_btn", type="secondary"):
        clear_watch_history(st.session_state.username)
        st.success("History cleared")
        st.rerun()


elif page == "🤖 Use AI":

    st.title("🤖 AI Movie Search (BERT)")
    st.caption("Try: 'space adventure', 'sad love story', 'dark thriller'")

    query = st.text_input("💬 Describe what you want to watch")

    if query:

        with st.spinner("AI is thinking... 🤖"):

            df = bert_search(query)

            # merge rating
            df = df.merge(
                movies_df[["title", "rating"]],
                on="title",
                how="left"
            )

            df["rating"] = df["rating"].fillna(0)

        st.markdown("### 🎬 AI Recommendations")

        cols = st.columns(5)

        for i, (_, row) in enumerate(df.iterrows()):
            with cols[i % 5]:

                poster = get_movie_poster(row["title"])
                st.image(poster)

                if st.button(row["title"], key=f"bert_{i}"):
                    st.session_state.selected_movie = row["title"]
                    st.rerun()

                st.write(f"⭐ {round(row['rating'],2)}")



# elif page == "🤖 Use AI":
#
#     st.title("🤖 AI Movie Assistant")
#     st.caption("Chat with AI and get recommendations 🎬")
#
#     # ---------------- SESSION ----------------
#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = []
#
#     if "chat_stage" not in st.session_state:
#         st.session_state.chat_stage = "start"
#
#     if "preferences" not in st.session_state:
#         st.session_state.preferences = {}
#
#     # ---------------- SHOW CHAT ----------------
#     for role, msg in st.session_state.chat_history:
#         with st.chat_message(role):
#             st.markdown(msg)
#
#     # ---------------- INPUT ----------------
#     user_input = st.chat_input("💬 Tell me how you feel...")
#
#     if user_input:
#
#         st.session_state.chat_history.append(("user", user_input))
#         text = user_input.lower()
#
#         # ---------------- INTENT DETECTION ----------------
#         mood = None
#         genre = None
#
#         if any(w in text for w in ["bored", "nothing", "idle"]):
#             mood = "bored"
#         if any(w in text for w in ["sad", "cry", "emotional"]):
#             mood = "sad"
#         if any(w in text for w in ["happy", "fun"]):
#             mood = "happy"
#
#         if any(w in text for w in ["funny", "comedy"]):
#             genre = "Comedy"
#         if any(w in text for w in ["romantic", "love"]):
#             genre = "Romance"
#         if any(w in text for w in ["horror", "scary"]):
#             genre = "Horror"
#         if any(w in text for w in ["action"]):
#             genre = "Action"
#
#         # ---------------- STORE ----------------
#         if mood:
#             st.session_state.preferences["mood"] = mood
#
#         if genre:
#             st.session_state.preferences["genre"] = genre
#
#         import random
#
#         # ---------------- CHAT LOGIC ----------------
#         reply = "🤔 I'm not sure, can you tell me more?"
#         if st.session_state.chat_stage == "start":
#
#             if mood == "bored":
#                 reply = "😄 You seem bored! Do you want something funny, adventurous, or relaxing?"
#                 st.session_state.chat_stage = "genre"
#
#             elif mood == "sad":
#                 reply = "💙 Feeling sad? Do you want emotional or uplifting movies?"
#                 st.session_state.chat_stage = "genre"
#
#             elif mood == "happy":
#                 reply = "😊 Nice mood! Want something fun or romantic?"
#                 st.session_state.chat_stage = "genre"
#
#
#             elif genre:
#                 # 🔥 DIRECT RECOMMEND (IMPORTANT FIX)
#                 reply = f"🎬 Got it! Showing {genre} movies for you 👇"
#                 st.session_state.chat_stage = "recommend"
#
#             else:
#                 reply = "🤔 Tell me your mood like bored, sad, or happy."
#
#         elif st.session_state.chat_stage == "genre":
#
#             if genre:
#                 reply = random.choice([
#                     f"🎬 Great! I’ll find some {genre} movies for you.",
#                     f"Nice choice 😄! Showing best {genre} movies.",
#                     f"You might enjoy these {genre} movies 👇"
#                 ])
#                 st.session_state.chat_stage = "recommend"
#
#             else:
#                 reply = "😅 Tell me a type like comedy, horror, romance, action."
#
#         st.session_state.chat_history.append(("assistant", reply))
#
#     # ---------------- SHOW MOVIES ----------------
#     if st.session_state.get("chat_stage") == "recommend":
#
#         query = ""
#
#         if "genre" in st.session_state.preferences:
#             query += st.session_state.preferences["genre"] + " "
#
#         if "mood" in st.session_state.preferences:
#             query += st.session_state.preferences["mood"]
#
#         df = bert_search(query)
#
#         df = df.merge(
#             movies_df[["title", "rating"]],
#             on="title",
#             how="left"
#         )
#
#         st.markdown("### 🎬 Recommended for you")
#
#         cols = st.columns(5)
#
#         for i, (_, row) in enumerate(df.iterrows()):
#             with cols[i % 5]:
#
#                 poster = get_movie_poster(row["title"])
#                 st.image(poster)
#
#                 if st.button(row["title"], key=f"chat_{i}"):
#                     st.session_state.selected_movie = row["title"]
#                     st.rerun()
#
#                 st.write(f"⭐ {round(row['rating'],2)}")
