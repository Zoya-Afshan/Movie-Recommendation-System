import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import Dataset, Reader, SVD
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')
# ================= LOAD DATA =================
movies = pd.read_csv("data/movies.csv")
ratings = pd.read_csv("data/ratings.csv")
tags = pd.read_csv("data/tags.csv")

# ================= CONTENT BASED =================
tags_grouped = tags.groupby("movieId")["tag"].apply(" ".join).reset_index()

movies = movies.merge(tags_grouped, on="movieId", how="left")
movies["tag"] = movies["tag"].fillna("")
movies["genres"] = movies["genres"].str.replace("|", " ", regex=False)

movies["content"] = movies["genres"] + " " + movies["tag"]

# ================= BERT / AI PART (ADD HERE) =================

# 🔥 Combine text for AI (you can reuse content or create new)
movies["combined"] = movies["genres"] + " " + movies["tag"]+" "+movies["title"]

# 🔥 Create embeddings (AI vectors)
movie_embeddings = model.encode(
    movies["combined"].tolist(),
    show_progress_bar=True
)

# ================= EXISTING TF-IDF CODE =================
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(movies["content"])
cosine_sim = cosine_similarity(tfidf_matrix)

indices = pd.Series(movies.index, index=movies["title"])


def get_all_movie_titles():
    return movies["title"].values


# ================= COLLABORATIVE MODEL =================
@st.cache_resource
def load_model():
    reader = Reader(rating_scale=(0.5, 5))

    data = Dataset.load_from_df(
        ratings[["userId", "movieId", "rating"]],
        reader
    )

    trainset = data.build_full_trainset()

    model = SVD(n_factors=50, n_epochs=20, random_state=42)
    model.fit(trainset)

    return model


svd = load_model()


def collaborative_scores(movie_id):
    users = ratings["userId"].unique()[:50]

    scores = []

    for user in users:
        scores.append(svd.predict(user, movie_id).est)

    return sum(scores) / len(scores)


# ================= HYBRID RECOMMENDATION =================
def recommend_movies(movie_title, n=10):

    if movie_title not in indices:
        return pd.DataFrame()

    idx = indices[movie_title]

    content_scores = list(enumerate(cosine_sim[idx]))
    content_scores = sorted(content_scores, key=lambda x: x[1], reverse=True)

    hybrid_list = []

    for movie_idx, content_score in content_scores[1:50]:

        movie_id = movies.iloc[movie_idx]["movieId"]

        collab_score = collaborative_scores(movie_id)

        final_score = (0.7 * content_score) + (0.3 * collab_score)

        hybrid_list.append((movie_idx, final_score))

    hybrid_list.sort(key=lambda x: x[1], reverse=True)

    final_indices = [x[0] for x in hybrid_list[:n]]

    return movies.iloc[final_indices]


def bert_search(query, n=10):

    query_embedding = model.encode([query])

    similarity = cosine_similarity(query_embedding, movie_embeddings)

    scores = list(enumerate(similarity[0]))

    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    indices = [i[0] for i in scores[:n]]

    return movies.iloc[indices]

# # ================= BECAUSE YOU WATCHED =================
# def recommend_from_history(history, n=10):
#
#     if not history:
#         return pd.DataFrame()
#
#     last_movie = history[-1]
#
#     return recommend_movies(last_movie, n)