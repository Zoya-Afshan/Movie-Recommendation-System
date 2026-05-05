# import requests
#
# url = "https://api.themoviedb.org/3/trending/movie/week"
# params = {"api_key": "a2e02779d65925a649c2e422a44819b6"}
#
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
# }
#
# try:
#     response = requests.get(url, params=params, headers=headers, timeout=15)
#
#     print("Status Code:", response.status_code)
#
#     data = response.json()
#
#     for movie in data.get("results", [])[:5]:
#         print(movie["title"])
#
# except Exception as e:
#     print("Error:", e)

import requests

url = "https://api.themoviedb.org/3/trending/movie/week"
params = {
    "api_key": "a2e02779d65925a649c2e422a44819b6"
}

try:
    response = requests.get(url, params=params, timeout=10)
    print(response.status_code)

    data = response.json()

    for movie in data.get("results", [])[:5]:
        print(movie["title"])

except Exception as e:
    print("Error:", e)