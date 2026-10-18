"""Fake movie records so the tests run on a machine with no data.

data/tmdb_backup.json is gitignored because it is big, so a fresh clone does
not have it and any test that opens it fails. these records have the same shape
the api gives back, just 4 of them instead of 18.

they cover the cases the brief cares about: a franchise and a standalone movie,
three directors, genres that repeat, and one movie with zero votes so the
vote_count rule gets tested.
"""
import json
import os

import pandas as pd

import src.cleaning as cleaning
import src.kpis as kpis

BACKUP_PATH = "data/tmdb_backup.json"


def _movie(mid, title, year, month, day, budget, revenue, votes, rating,
           popularity, runtime, collection, director, genres, cast):
    return {
        "id": mid,
        "title": title,
        "tagline": "a short tagline",
        "overview": "an overview that is real text",
        "release_date": f"{year}-{month:02d}-{day:02d}",
        "status": "Released",
        "adult": False,
        "imdb_id": "tt0000001",
        "original_title": title.upper(),
        "video": False,
        "homepage": "",
        "original_language": "en",
        "budget": budget,
        "revenue": revenue,
        "vote_count": votes,
        "vote_average": rating,
        "popularity": popularity,
        "runtime": runtime,
        "poster_path": "/p.jpg",
        "belongs_to_collection": (
            None if collection is None else {"id": 900, "name": collection}
        ),
        "genres": [{"id": i, "name": g} for i, g in enumerate(genres)],
        "production_companies": [{"id": 1, "name": "Fake Studio"}],
        "production_countries": [{"iso_3166_1": "US", "name": "United States"}],
        "spoken_languages": [{"iso_639_1": "en", "english_name": "English",
                              "name": "English", "flag": "us"}],
        "cast": [{"cast_id": i, "name": n} for i, n in enumerate(cast)],
        "cast_size": len(cast),
        "director": director,
        "crew_size": 12,
    }


def fake_movies():
    """Six records.

    two franchises plus a third, and three standalones. each group has one
    film with a wild roi so that mean and median do not come out the same.
    without those, mean == median and a test for median proves nothing.
    """
    return [
        _movie(1, "Alpha", 2010, 5, 1, 20000000, 60000000, 800, 7.5, 55.0, 120,
               "Alpha Collection", "Jane Doe",
               ["Action", "Science Fiction"], ["Bruce Willis", "Uma Thurman"]),
        _movie(2, "Beta", 2012, 7, 4, 10000000, 30000000, 400, 6.5, 40.0, 98,
               "Alpha Collection", "Jane Doe",
               ["Drama"], ["Uma Thurman"]),
        # franchise outlier, roi 19.0 against two films on 3.0
        _movie(3, "Epsilon", 2014, 9, 9, 5000000, 95000000, 600, 7.0, 48.0, 132,
               "Alpha Collection", "Jane Doe",
               ["Action"], ["Someone Else"]),
        _movie(4, "Gamma", 2015, 1, 20, 40000000, 80000000, 1000, 8.0, 70.0, 141,
               None, "John Roe",
               ["Action", "Science Fiction"], ["Bruce Willis"]),
        # zero votes, so vote_average is meaningless and has to become NaN
        _movie(5, "Delta", 2018, 3, 3, 5000000, 5000000, 0, 9.9, 12.0, 90,
               None, "John Roe",
               ["Comedy"], ["Someone Else"]),
        # standalone outlier, roi 40.0
        _movie(6, "Zeta", 2019, 11, 7, 1000000, 40000000, 300, 6.0, 33.0, 105,
               None, "Sam Poe",
               ["Science Fiction"], ["Someone Else"]),
    ]


def load_records():
    """real backup if this machine has it, fake records if not."""
    if os.path.exists(BACKUP_PATH):
        f = open(BACKUP_PATH, "r", encoding="utf-8")
        records = json.load(f)
        f.close()
        return records
    return fake_movies()


def done_df():
    """the cleaned frame with profit and roi on it, like the notebook has.

    uses the real backup when this machine has one, so a test that only wants
    to prove something runs should use this.
    """
    return _finish(pd.DataFrame(load_records()))


def fake_df():
    """always the 4 fake records. use this when the test asserts a number."""
    return _finish(pd.DataFrame(fake_movies()))


def _finish(df):
    return kpis.add_profit_roi(cleaning.clean(df))


def has_real_backup():
    return os.path.exists(BACKUP_PATH)
