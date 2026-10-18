import pandas as pd

DROP_COLUMNS = ["adult", "imdb_id", "original_title", "video", "homepage"]

FINAL_COLUMNS = [
    "id", "title", "tagline", "release_date", "genres", "belongs_to_collection",
    "original_language", "budget_musd", "revenue_musd", "production_companies",
    "production_countries", "vote_count", "vote_average", "popularity", "runtime",
    "overview", "spoken_languages", "poster_path", "cast", "cast_size", "director", "crew_size",
]


def get_collection_name(value):
    if isinstance(value, dict):
        return value.get("name")
    return None


def join_names(items, key):
    if isinstance(items, list):
        names = []
        for d in items:
            if isinstance(d, dict) and key in d:
                names.append(d[key])
            elif isinstance(d, str):
                names.append(d)
        if len(names) == 0:
            return None
        s = names[0]
        for n in names[1:]:
            s = s + "|" + n
        return s
    return items


def drop_irrelevant_columns(df):
    df2 = df.copy()
    for col in DROP_COLUMNS:
        if col in df2.columns:
            del df2[col]
    return df2


def extract_collection_name(df):
    df2 = df.copy()
    out = []
    for v in df2["belongs_to_collection"]:
        out.append(get_collection_name(v))
    df2["belongs_to_collection"] = out
    return df2


def pipe_join_names(df, column, name_key):
    df2 = df.copy()
    out = []
    for v in df2[column]:
        out.append(join_names(v, name_key))
    df2[column] = out
    return df2


def inspect_anomalies(df, columns):
    """Print value_counts for the columns i built, and give the counts back
    so a test can check this actually ran."""
    out = {}
    for col in columns:
        print(col)
        counts = df[col].value_counts(dropna=False).head(10)
        print(counts)
        out[col] = counts
    return out


def convert_dtypes(df):
    df2 = df.copy()
    df2["budget"] = pd.to_numeric(df2["budget"], errors="coerce")
    df2["revenue"] = pd.to_numeric(df2["revenue"], errors="coerce")
    df2["id"] = pd.to_numeric(df2["id"], errors="coerce")
    df2["popularity"] = pd.to_numeric(df2["popularity"], errors="coerce")
    df2["vote_count"] = pd.to_numeric(df2["vote_count"], errors="coerce")
    df2["vote_average"] = pd.to_numeric(df2["vote_average"], errors="coerce")
    df2["runtime"] = pd.to_numeric(df2["runtime"], errors="coerce")
    df2["release_date"] = pd.to_datetime(df2["release_date"], errors="coerce")
    return df2


def clean_unrealistic_values(df):
    df2 = df.copy()
    for col in ["budget", "revenue", "runtime"]:
        df2[col] = df2[col].replace(0, float("nan"))
    df2["budget_musd"] = df2["budget"] / 1000000
    df2["revenue_musd"] = df2["revenue"] / 1000000
    # a movie with no votes has a vote_average that means nothing, so it goes
    # to NaN. .loc not .iloc, chained assignment is dropped by pandas 3.
    no_votes = df2["vote_count"] == 0
    df2.loc[no_votes, "vote_average"] = float("nan")
    for col in ["overview", "tagline"]:
        if col in df2.columns:
            df2[col] = df2[col].replace("No Data", float("nan"))
            df2[col] = df2[col].replace("", float("nan"))
    return df2


def filter_released_and_dedup(df):
    df2 = df.copy()
    df2 = df2[df2["status"] == "Released"]
    if "status" in df2.columns:
        del df2["status"]
    df2 = df2.drop_duplicates(subset=["id", "title"])
    df2 = df2.dropna(subset=["id", "title"])
    df2 = df2.dropna(thresh=10)
    return df2


def reorder_and_reset(df):
    df2 = df[FINAL_COLUMNS].copy()
    df2 = df2.reset_index(drop=True)
    return df2


def clean(df):
    df2 = df.copy()
    df2 = drop_irrelevant_columns(df2)
    df2 = extract_collection_name(df2)
    df2 = pipe_join_names(df2, "genres", "name")
    df2 = pipe_join_names(df2, "spoken_languages", "english_name")
    df2 = pipe_join_names(df2, "production_countries", "name")
    df2 = pipe_join_names(df2, "production_companies", "name")
    df2 = pipe_join_names(df2, "cast", "name")
    df2 = convert_dtypes(df2)
    df2 = clean_unrealistic_values(df2)
    df2 = filter_released_and_dedup(df2)
    df2 = reorder_and_reset(df2)
    return df2
