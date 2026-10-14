import pandas as pd
import src.cleaning as cleaning


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


def test_clean_backup():
    import json
    f = open("data/tmdb_backup.json", encoding="utf-8")
    records = json.load(f)
    f.close()
    df = pd.DataFrame(records)
    out = cleaning.clean(df)
    assert list(out.columns) == cleaning.FINAL_COLUMNS
    assert len(out) == 18
