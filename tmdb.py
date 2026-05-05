import requests
import streamlit as st

API_KEY = "a2e02779d65925a649c2e422a44819b6"
PLACEHOLDER = "https://via.placeholder.com/300x450.png?text=Poster+Not+Available"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


@st.cache_data(show_spinner=False)
def get_movie_poster(title):

    title = title.split("(")[0].strip()

    try:
        url = "https://api.themoviedb.org/3/search/movie"

        params = {
            "api_key": API_KEY,
            "query": title
        }

        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=1
        )

        data = response.json()

        if data.get("results"):
            poster_path = data["results"][0].get("poster_path")

            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path


    except Exception:
        pass

    #PLACEHOLDER
    return "https://dummyimage.com/300x450/222/fff&text=Poster+Not+Available"
    # return f"https://via.placeholder.com/300x450?text={title}"


import urllib.parse

def get_trailer_link(title):

    title = title.split("(")[0].strip()

    # ✅ encode properly
    query = urllib.parse.quote(f"{title} trailer")

    return f"https://www.youtube.com/results?search_query={query}"


def search_movie_tmdb(query):
    import requests

    url = "https://api.themoviedb.org/3/search/movie"

    params = {
        "api_key": API_KEY,
        "query": query
    }

    try:
        res = requests.get(url, params=params, timeout=5).json()

        if res.get("results"):
            return res["results"][0]   # return best match

    except:
        pass

    return None
# import requests
#
# def get_trailer_link(title):
#
#     try:
#         # 🔍 search movie
#         search_url = "https://api.themoviedb.org/3/search/movie"
#         params = {"api_key": API_KEY, "query": title}
#
#         res = requests.get(search_url, params=params).json()
#
#         if res.get("results"):
#             movie_id = res["results"][0]["id"]
#
#             # 🎬 get videos
#             video_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos"
#             videos = requests.get(video_url, params={"api_key": API_KEY}).json()
#
#             for v in videos.get("results", []):
#                 if v["type"] == "Trailer" and v["site"] == "YouTube":
#                     return f"https://www.youtube.com/watch?v={v['key']}"
#
#     except:
#         pass
#
#     return None

@st.cache_data(show_spinner=False)


def get_watch_providers(title):

    import requests

    try:
        # 🔍 search movie
        search_url = "https://api.themoviedb.org/3/search/movie"
        params = {"api_key": API_KEY, "query": title}

        res = requests.get(search_url, params=params).json()

        if res.get("results"):
            movie_id = res["results"][0]["id"]

            # 🎬 providers API
            provider_url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers"
            data = requests.get(provider_url, params={"api_key": API_KEY}).json()

            results = data.get("results", {})

            # ✅ Try India first
            providers = results.get("IN")

            # 🔥 fallback to US if IN not found
            if not providers:
                providers = results.get("US")

            if not providers:
                return []

            names = []

            for key in ["flatrate", "rent", "buy"]:
                if key in providers:
                    for p in providers[key]:
                        names.append(p["provider_name"])

            return list(set(names))

    except:
        pass

    return []
def get_bollywood_movies(limit=10):

    url = "https://api.themoviedb.org/3/discover/movie"

    params = {
        "api_key": API_KEY,
        "with_original_language": "hi",   # Hindi
        "sort_by": "popularity.desc"
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=15
        )

        data = response.json()

        return data.get("results", [])[:limit]

    except:
        return []

@st.cache_data(show_spinner=False)
def get_movies_by_language(lang_code="hi", limit=10):

    url = "https://api.themoviedb.org/3/discover/movie"

    params = {
        "api_key": API_KEY,
        "with_original_language": lang_code,
        "sort_by": "popularity.desc"
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=15
        )

        data = response.json()

        return data.get("results", [])[:limit]

    except:
        return []


@st.cache_data(show_spinner=False)
def get_trending_bollywood_movies(limit=10):

    url = "https://api.themoviedb.org/3/discover/movie"

    params = {
        "api_key": API_KEY,
        "language": "en-US",
        "sort_by": "popularity.desc",
        "with_original_language": "hi",
        "region": "IN",
        "release_date.gte": "2023-01-01"
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=2
        )

        if response.status_code != 200:
            return []

        data = response.json()

        return data.get("results", [])[:limit]

    except requests.exceptions.RequestException:
        return []

def get_movie_overview(title):

    import requests

    try:
        title = title.split("(")[0].strip()

        url = "https://api.themoviedb.org/3/search/movie"

        params = {
            "api_key": API_KEY,
            "query": title
        }

        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if data.get("results"):
            overview = data["results"][0].get("overview")

            if overview:
                return overview

    except:
        pass

    return "No description available."


def get_cast_and_crew(title):

    import requests

    try:
        title = title.split("(")[0].strip()

        # 🔍 Search movie
        search_url = "https://api.themoviedb.org/3/search/movie"
        params = {"api_key": API_KEY, "query": title}

        res = requests.get(search_url, params=params, timeout=5).json()

        if res.get("results"):
            movie_id = res["results"][0]["id"]

            # 🎭 Credits API
            credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
            credits = requests.get(credits_url, params={"api_key": API_KEY}).json()

            cast_list = []
            crew_list = []

            # 🎭 Top Cast (first 5)
            for c in credits.get("cast", [])[:5]:
                cast_list.append(c["name"])

            # 🎬 Crew (Director + Writer)
            for c in credits.get("crew", []):
                if c["job"] in ["Director", "Writer", "Screenplay"]:
                    crew_list.append(f"{c['job']}: {c['name']}")

            return cast_list, list(set(crew_list))

    except:
        pass

    return [], []



def get_movie_details(title):

    import requests

    try:
        title = title.split("(")[0].strip()

        url = "https://api.themoviedb.org/3/search/movie"
        params = {"api_key": API_KEY, "query": title}

        res = requests.get(url, params=params, timeout=5).json()

        if res.get("results"):
            movie_id = res["results"][0]["id"]

            # 🔥 get full details
            details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
            data = requests.get(details_url, params={"api_key": API_KEY}).json()

            release_date = data.get("release_date", "")
            runtime = data.get("runtime", "")

            return release_date, runtime

    except:
        pass

    return "", ""
if __name__ == "__main__":
    print(get_movie_poster("Avatar"))



# import requests
# import streamlit as st
#
# API_KEY = "a2e02779d65925a649c2e422a44819b6"
#
# PLACEHOLDER = "https://dummyimage.com/300x450/222/fff&text=No+Image"
#
# HEADERS = {
#     "User-Agent": "Mozilla/5.0"
# }
#
# # ---------------- POSTER ----------------
# @st.cache_data(show_spinner=False)
# def get_movie_poster(title):
#
#     title = title.split("(")[0].strip()
#
#     try:
#         url = "https://api.themoviedb.org/3/search/movie"
#
#         params = {
#             "api_key": API_KEY,
#             "query": title
#         }
#
#         response = requests.get(
#             url,
#             params=params,
#             headers=HEADERS,
#             timeout=15   # ✅ fixed timeout
#         )
#
#         data = response.json()
#
#         if data.get("results"):
#             for movie in data["results"]:
#                 poster_path = movie.get("poster_path")
#
#                 if poster_path:
#                     return "https://image.tmdb.org/t/p/w500" + poster_path
#
#     except Exception as e:
#         print("Poster Error:", e)
#
#     return PLACEHOLDER   # ✅ fixed return
#
#
# # ---------------- TRAILER ----------------
# def get_trailer_link(title):
#
#     title = title.split("(")[0].strip()
#     return f"https://www.youtube.com/results?search_query={title}+trailer"
#
#
# # ---------------- TRENDING (GLOBAL) ----------------
# @st.cache_data(show_spinner=False)
# def get_trending_movies(limit=10):
#
#     url = "https://api.themoviedb.org/3/trending/movie/week"
#
#     params = {"api_key": API_KEY}
#
#     try:
#         response = requests.get(
#             url,
#             params=params,
#             headers=HEADERS,
#             timeout=15
#         )
#
#         data = response.json()
#
#         return data.get("results", [])[:limit]
#
#     except Exception as e:
#         print("Trending Error:", e)
#         return []
#
#
# # ---------------- BOLLYWOOD MOVIES ----------------
# @st.cache_data(show_spinner=False)
# def get_bollywood_movies(limit=10):
#
#     url = "https://api.themoviedb.org/3/discover/movie"
#
#     params = {
#         "api_key": API_KEY,
#         "with_original_language": "hi",   # Hindi movies
#         "sort_by": "popularity.desc"
#     }
#
#     try:
#         response = requests.get(
#             url,
#             params=params,
#             headers=HEADERS,
#             timeout=15
#         )
#
#         data = response.json()
#
#         return data.get("results", [])[:limit]
#
#     except Exception as e:
#         print("Bollywood Error:", e)
#         return []
#
#
# # ---------------- LANGUAGE FILTER ----------------
# @st.cache_data(show_spinner=False)
# def get_movies_by_language(lang_code="en", limit=10):
#
#     url = "https://api.themoviedb.org/3/discover/movie"
#
#     params = {
#         "api_key": API_KEY,
#         "with_original_language": lang_code,
#         "sort_by": "popularity.desc"
#     }
#
#     try:
#         response = requests.get(
#             url,
#             params=params,
#             headers=HEADERS,
#             timeout=15
#         )
#
#         data = response.json()
#
#         return data.get("results", [])[:limit]
#
#     except Exception as e:
#         print("Language Error:", e)
#         return []
