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
    # genres and friends come in as dicts with a name key, cast comes in as
    # plain strings. handle both so one helper can join all of them.
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
    df_dropped = df.copy()
    for col in DROP_COLUMNS:
        if col in df_dropped.columns:
            del df_dropped[col]
    return df_dropped


def extract_collection_name(df):
    df_collection_named = df.copy()
    out = []
    for v in df_collection_named["belongs_to_collection"]:
        out.append(get_collection_name(v))
    df_collection_named["belongs_to_collection"] = out
    return df_collection_named


def pipe_join_names(df, column, name_key):
    df_flattened = df.copy()
    out = []
    for v in df_flattened[column]:
        out.append(join_names(v, name_key))
    df_flattened[column] = out
    return df_flattened


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
    df_typed = df.copy()
    df_typed["budget"] = pd.to_numeric(df_typed["budget"], errors="coerce")
    df_typed["revenue"] = pd.to_numeric(df_typed["revenue"], errors="coerce")
    df_typed["id"] = pd.to_numeric(df_typed["id"], errors="coerce")
    df_typed["popularity"] = pd.to_numeric(df_typed["popularity"], errors="coerce")
    df_typed["vote_count"] = pd.to_numeric(df_typed["vote_count"], errors="coerce")
    df_typed["vote_average"] = pd.to_numeric(df_typed["vote_average"], errors="coerce")
    df_typed["runtime"] = pd.to_numeric(df_typed["runtime"], errors="coerce")
    df_typed["release_date"] = pd.to_datetime(df_typed["release_date"], errors="coerce")
    return df_typed


def clean_unrealistic_values(df):
    df_sane = df.copy()
    for col in ["budget", "revenue", "runtime"]:
        df_sane[col] = df_sane[col].replace(0, float("nan"))
    df_sane["budget_musd"] = df_sane["budget"] / 1000000
    df_sane["revenue_musd"] = df_sane["revenue"] / 1000000
    # a movie with no votes has a vote_average that means nothing, so it goes
    # to NaN. .loc not .iloc, chained assignment is dropped by pandas 3.
    no_votes = df_sane["vote_count"] == 0
    df_sane.loc[no_votes, "vote_average"] = float("nan")
    for col in ["overview", "tagline"]:
        if col in df_sane.columns:
            df_sane[col] = df_sane[col].replace("No Data", float("nan"))
            df_sane[col] = df_sane[col].replace("", float("nan"))
    return df_sane


def filter_released_and_dedup(df):
    df_released = df.copy()
    df_released = df_released[df_released["status"] == "Released"]
    if "status" in df_released.columns:
        del df_released["status"]
    df_released = df_released.drop_duplicates(subset=["id", "title"])
    df_released = df_released.dropna(subset=["id", "title"])
    df_released = df_released.dropna(thresh=10)
    return df_released


def reorder_and_reset(df):
    df_ordered = df[FINAL_COLUMNS].copy()
    df_ordered = df_ordered.reset_index(drop=True)
    return df_ordered


def clean(df):
    df_current = df.copy()
    df_current = drop_irrelevant_columns(df_current)
    df_current = extract_collection_name(df_current)
    df_current = pipe_join_names(df_current, "genres", "name")
    df_current = pipe_join_names(df_current, "spoken_languages", "english_name")
    df_current = pipe_join_names(df_current, "production_countries", "name")
    df_current = pipe_join_names(df_current, "production_companies", "name")
    df_current = pipe_join_names(df_current, "cast", "name")
    df_current = convert_dtypes(df_current)
    df_current = clean_unrealistic_values(df_current)
    df_current = filter_released_and_dedup(df_current)
    df_current = reorder_and_reset(df_current)
    return df_current
