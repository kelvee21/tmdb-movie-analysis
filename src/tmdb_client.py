import json
import os
import time

import requests
from dotenv import load_dotenv

MOVIE_IDS = [
    0, 299534, 19995, 140607, 299536, 597, 135397,
    420818, 24428, 168259, 99861, 284054, 12445,
    181808, 330457, 351286, 109445, 321612, 260513,
]

TIMEOUT = 20


def fetch_movie(movie_id, api_key, base_url):
    url = base_url + "/movie/" + str(movie_id)
    try:
        r = requests.get(url, params={"api_key": api_key}, timeout=TIMEOUT)
    except Exception as e:
        print("network error", movie_id, e)
        return None

    if r.status_code == 404:
        print("movie", movie_id, "not found, skip it")
        return None

    if r.status_code in (429, 500, 502, 503, 504):
        # one retry only. a second 429 just skips this film.
        time.sleep(1.5)
        try:
            r = requests.get(url, params={"api_key": api_key}, timeout=TIMEOUT)
        except Exception as e:
            print("retry failed", movie_id, e)
            return None

    if r.status_code != 200:
        print("skip movie", movie_id, r.status_code)
        return None

    movie = r.json()

    credits_url = base_url + "/movie/" + str(movie_id) + "/credits"
    try:
        cr = requests.get(credits_url, params={"api_key": api_key}, timeout=TIMEOUT)
        credits = cr.json()

        cast_list = credits.get("cast", [])
        names = []
        for p in cast_list:
            if "name" in p:
                names.append(p["name"])
        movie["cast"] = names
        movie["cast_size"] = len(names)

        crew_list = credits.get("crew", [])
        director = None
        for p in crew_list:
            if p.get("job") == "Director":
                director = p.get("name")
                break
        movie["director"] = director
        movie["crew_size"] = len(crew_list)
    except Exception as e:
        print("credits problem", movie_id, e)

    return movie


def load_offline_backup(path):
    if not os.path.exists(path):
        raise FileNotFoundError(
            "no TMDB_API_KEY in .env and no backup at " + path +
            ". put a key in .env, or put the backup json back in data/."
        )
    f = open(path, "r", encoding="utf-8")
    data = json.load(f)
    f.close()
    print("loaded backup", len(data), "movies")
    return data


def fetch_all(movie_ids=None):
    load_dotenv()
    api_key = os.getenv("TMDB_API_KEY", "")
    base_url = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")
    backup = os.getenv("OFFLINE_BACKUP_PATH", "data/tmdb_backup.json")

    if movie_ids is None:
        movie_ids = MOVIE_IDS

    if api_key == "":
        return load_offline_backup(backup)

    out = []
    for mid in movie_ids:
        m = fetch_movie(mid, api_key, base_url)
        if m is not None:
            out.append(m)
        time.sleep(0.25)

    if len(out) == 0 and os.path.exists(backup):
        return load_offline_backup(backup)

    return out


if __name__ == "__main__":
    movies = fetch_all()
    os.makedirs("data", exist_ok=True)
    f = open("data/raw_movies.json", "w", encoding="utf-8")
    json.dump(movies, f, indent=1)
    f.close()
    print("saved", len(movies), "movies")
