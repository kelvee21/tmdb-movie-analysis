import pandas as pd
import pytest

import src.cleaning as cleaning
from tests.helpers import fake_movies, has_real_backup, load_records


def test_final_columns():
    assert len(cleaning.FINAL_COLUMNS) == 22
    assert cleaning.FINAL_COLUMNS[0] == "id"
    assert "budget_musd" in cleaning.FINAL_COLUMNS


def test_drop_columns():
    df = pd.DataFrame([{"id": 1, "title": "T", "adult": False, "video": False}])
    out = cleaning.drop_irrelevant_columns(df)
    assert "adult" not in out.columns
    assert "video" not in out.columns


def test_collection_name():
    df = pd.DataFrame([
        {"belongs_to_collection": {"id": 10, "name": "Star Wars Collection"}},
        {"belongs_to_collection": None},
    ])
    out = cleaning.extract_collection_name(df)
    assert out["belongs_to_collection"][0] == "Star Wars Collection"
    assert pd.isna(out["belongs_to_collection"][1])


def test_join_names():
    df = pd.DataFrame([
        {"genres": [{"name": "Action"}, {"name": "Comedy"}]},
    ])
    out = cleaning.pipe_join_names(df, "genres", "name")
    assert out["genres"][0] == "Action|Comedy"


def test_join_names_uses_english_name():
    df = pd.DataFrame([
        {"spoken_languages": [{"english_name": "English", "name": "English"}]},
    ])
    out = cleaning.pipe_join_names(df, "spoken_languages", "english_name")
    assert out["spoken_languages"][0] == "English"


def test_clean_gives_the_brief_columns():
    out = cleaning.clean(pd.DataFrame(fake_movies()))
    assert list(out.columns) == cleaning.FINAL_COLUMNS
    assert len(out.columns) == 22
    assert list(out.index) == list(range(len(out)))


def test_clean_keeps_every_fake_row():
    out = cleaning.clean(pd.DataFrame(fake_movies()))
    assert len(out) == 6


def test_zero_budget_revenue_runtime_become_nan():
    df = pd.DataFrame(fake_movies())
    df["budget"] = 0
    df["revenue"] = 0
    df["runtime"] = 0
    out = cleaning.clean_unrealistic_values(df)
    assert out["budget"].isna().all()
    assert out["revenue"].isna().all()
    assert out["runtime"].isna().all()


def test_budget_and_revenue_become_millions():
    df = pd.DataFrame(fake_movies())
    out = cleaning.clean_unrealistic_values(df)
    row = out[out["id"] == 1].iloc[0]
    assert row["budget_musd"] == 20.0
    assert row["revenue_musd"] == 60.0


def test_vote_count_zero_clears_the_rating():
    """A movie with no votes has a vote_average that means nothing.

    this used to use chained assignment, pandas 3 dropped the write and the
    rating stayed put. keep this test or it can come back.
    """
    out = cleaning.clean(pd.DataFrame(fake_movies()))
    zero = out[out["vote_count"] == 0]
    assert len(zero) == 1
    assert pd.isna(zero["vote_average"].iloc[0])


def test_movies_with_votes_keep_their_rating():
    out = cleaning.clean(pd.DataFrame(fake_movies()))
    voted = out[out["vote_count"] > 0]
    assert voted["vote_average"].notna().all()


def test_no_data_text_becomes_nan():
    df = pd.DataFrame(fake_movies())
    df["overview"] = "No Data"
    out = cleaning.clean_unrealistic_values(df)
    assert out["overview"].isna().all()


def test_inspect_anomalies_returns_value_counts():
    """Brief step 2.4. this used to be a function nothing called."""
    out = cleaning.clean(pd.DataFrame(fake_movies()))
    counts = cleaning.inspect_anomalies(out, ["genres", "original_language"])
    assert "genres" in counts and "original_language" in counts
    assert len(counts["genres"]) > 0
    assert counts["genres"].sum() == len(out)


def test_clean_real_backup():
    if not has_real_backup():
        pytest.skip("no backup json on this machine, fake records cover this")
    out = cleaning.clean(pd.DataFrame(load_records()))
    assert list(out.columns) == cleaning.FINAL_COLUMNS
    assert len(out) == 18
