from tmdb_client import MOVIE_IDS, fetch_movie, load_offline_backup


class FakeResponse:
    def __init__(self, data, status):
        self.data = data
        self.status_code = status

    def json(self):
        return self.data


class FakeInternet:
    def __init__(self, movie, credits):
        self.movie = movie
        self.credits = credits

    def get(self, url, params=None, timeout=None):
        if url.endswith("/credits"):
            return FakeResponse(self.credits, 200)
        if self.movie is None:
            return FakeResponse(None, 404)
        return FakeResponse(self.movie, 200)


def test_movie_ids_match_lab_spec():
    assert len(MOVIE_IDS) == 19
    assert MOVIE_IDS[0] == 0


def test_fetch_movie_merges_credits(monkeypatch):
    import tmdb_client

    fake_movie = {"id": 597, "title": "Titanic", "budget": 200000000}
    fake_credits = {
        "cast": [{"name": "A"}, {"name": "B"}],
        "crew": [{"name": "Cameron", "job": "Director"}],
    }
    fake = FakeInternet(fake_movie, fake_credits)

    def fake_get(url, params=None, timeout=None):
        return fake.get(url, params=params, timeout=timeout)

    monkeypatch.setattr(tmdb_client.requests, "get", fake_get)

    out = fetch_movie(597, "fake-key", "http://x")
    assert out["director"] == "Cameron"
    assert out["cast_size"] == 2
    assert out["cast"] == ["A", "B"]


def test_fetch_movie_404_returns_none(monkeypatch):
    import tmdb_client

    def fake_get_404(url, params=None, timeout=None):
        return FakeResponse(None, 404)

    monkeypatch.setattr(tmdb_client.requests, "get", fake_get_404)
    assert fetch_movie(0, "fake-key", "http://x") is None


def test_offline_backup_loads(tmp_path):
    import json
    p = tmp_path / "b.json"
    p.write_text(json.dumps([{"id": 1, "title": "T"}]), encoding="utf-8")
    assert load_offline_backup(p) == [{"id": 1, "title": "T"}]
