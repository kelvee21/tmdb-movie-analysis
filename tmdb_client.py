"""TMDB API client for the DEM02 lab (Step 1: Fetch Movie Data from API).

Reads the v3 API key from `.env` (never hardcode it), fetches each fixed
movie ID from `/movie/{id}` plus `/movie/{id}/credits` (cast + director),
and returns a list of raw dicts ready for ``pd.DataFrame``.

Falls back to the offline backup (``OFFLINE_BACKUP_PATH``) when the network
or API is unreachable -- Step 1 must never block.
"""
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path

import requests

log = logging.getLogger("tmdb_client")

# Fixed lab movie IDs (lab spec, Step 1). 0 is intentionally invalid and
# exercises the error-handling path (L7: robust ETL scripts).
MOVIE_IDS = [
    0, 299534, 19995, 140607, 299536, 597, 135397,
    420818, 24428, 168259, 99861, 284054, 12445,
    181808, 330457, 351286, 109445, 321612, 260513,
]

TIMEOUT_S = 20
RETRYABLE = (429, 500, 502, 503, 504)


def _session(api_key: str) -> requests.Session:
    s = requests.Session()
    s.params = {"api_key": api_key}  # v3 query-param auth (see TMDB auth docs)
    s.headers.update({"Accept": "application/json"})
    return s


def fetch_movie(session: requests.Session, base_url: str, movie_id: int) -> dict | None:
    """One movie + its credits. None when the ID is invalid (e.g. 0)."""
    try:
        r = session.get(f"{base_url}/movie/{movie_id}", timeout=TIMEOUT_S)
        if r.status_code == 404:
            log.warning("movie %s not found (404), skipping", movie_id)
            return None
        if r.status_code in RETRYABLE:
            time.sleep(1.5)
            r = session.get(f"{base_url}/movie/{movie_id}", timeout=TIMEOUT_S)
        r.raise_for_status()
        movie = r.json()
        try:
            c = session.get(f"{base_url}/movie/{movie_id}/credits", timeout=TIMEOUT_S)
            c.raise_for_status()
            movie["cast"] = [m.get("name") for m in c.json().get("cast", [])]
            crew = c.json().get("crew", [])
            movie["director"] = next(
                (m.get("name") for m in crew if m.get("job") == "Director"), None)
            movie["cast_size"] = len(movie["cast"])
            movie["crew_size"] = len(crew)
        except requests.RequestException as e:
            log.warning("credits for %s failed (%s); continuing without them", movie_id, e)
        return movie
    except requests.RequestException as e:
        log.error("fetch movie %s failed: %s", movie_id, e)
        return None


def load_offline_backup(path: str | Path) -> list[dict]:
    """Offline backup: a JSON list of movie dicts shaped like API responses."""
    records = json.loads(Path(path).read_text(encoding="utf-8"))
    log.info("loaded %d records from offline backup %s", len(records), path)
    return records


def fetch_all(movie_ids: list[int] | None = None) -> list[dict]:
    """Fetch every ID; on network failure use the offline backup instead."""
    api_key = os.getenv("TMDB_API_KEY", "")
    base_url = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")
    backup = os.getenv("OFFLINE_BACKUP_PATH", "data/tmdb_backup.json")
    ids = movie_ids if movie_ids is not None else MOVIE_IDS
    if not api_key:
        log.warning("TMDB_API_KEY not set; using offline backup %s", backup)
        return load_offline_backup(backup)
    session = _session(api_key)
    records = []
    for mid in ids:
        rec = fetch_movie(session, base_url, mid)
        if rec is not None:
            records.append(rec)
        time.sleep(0.25)  # stay well under TMDB rate limits
    if not records and Path(backup).exists():
        log.warning("live fetch returned nothing; using offline backup")
        return load_offline_backup(backup)
    return records


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    recs = fetch_all()
    Path("data").mkdir(exist_ok=True)
    Path("data/raw_movies.json").write_text(json.dumps(recs, indent=1), encoding="utf-8")
    print(f"stored {len(recs)} movie records -> data/raw_movies.json")
