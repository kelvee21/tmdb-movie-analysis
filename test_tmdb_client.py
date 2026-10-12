"""Smoke tests for tmdb_client (L7: unit testing). All network calls mocked."""
from tmdb_client import MOVIE_IDS, fetch_movie, load_offline_backup


class _Resp:
    def __init__(self, payload, status=200):
        self._p = payload
        self.status_code = status

    def json(self):
        return self._p

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"http {self.status_code}")


class _Session:
    def __init__(self, movie, credits):
        self.movie, self.credits = movie, credits

    def get(self, url, timeout=None):
        if url.endswith("/credits"):
            return _Resp(self.credits)
        return _Resp(self.movie, 200 if self.movie else 404)


def test_movie_ids_match_lab_spec():
    assert len(MOVIE_IDS) == 19
    assert MOVIE_IDS[0] == 0  # invalid ID exercises error handling


def test_fetch_movie_merges_credits():
    movie = {"id": 597, "title": "Titanic", "budget": 200000000}
    credits = {"cast": [{"name": "A"}, {"name": "B"}],
               "crew": [{"name": "Cameron", "job": "Director"}]}
    rec = fetch_movie(_Session(movie, credits), "http://x", 597)
    assert rec["director"] == "Cameron"
    assert rec["cast_size"] == 2


def test_fetch_movie_404_returns_none():
    assert fetch_movie(_Session(None, {}), "http://x", 0) is None


def test_offline_backup_loads(tmp_path):
    import json
    p = tmp_path / "b.json"
    p.write_text(json.dumps([{"id": 1, "title": "T"}]), encoding="utf-8")
    assert load_offline_backup(p) == [{"id": 1, "title": "T"}]
