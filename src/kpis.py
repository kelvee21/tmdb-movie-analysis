import pandas as pd

ROI_MIN_BUDGET_MUSD = 10.0
MIN_VOTES = 10


def add_profit_roi(df):
    df_enriched = df.copy()
    df_enriched["profit"] = df_enriched["revenue_musd"] - df_enriched["budget_musd"]
    df_enriched["roi"] = df_enriched["revenue_musd"] / df_enriched["budget_musd"]
    return df_enriched


def rank(df, col, n=5, ascending=False):
    df_ranked = df.copy()
    if ascending:
        df_ranked = df_ranked.sort_values(by=col, ascending=True)
    else:
        df_ranked = df_ranked.sort_values(by=col, ascending=False)
    return df_ranked.head(n)


def search_willis_scifi_action(df):
    df_matches = df.copy()
    keep = []
    for i in range(len(df_matches)):
        row = df_matches.iloc[i]
        g = str(row["genres"])
        c = str(row["cast"])
        if "Science Fiction" in g and "Action" in g and "Bruce Willis" in c:
            keep.append(True)
        else:
            keep.append(False)
    df_matches = df_matches[keep]
    df_matches = df_matches.sort_values(by="vote_average", ascending=False)
    return df_matches


def search_thurman_tarantino(df):
    df_matches = df.copy()
    keep = []
    for i in range(len(df_matches)):
        row = df_matches.iloc[i]
        c = str(row["cast"])
        d = str(row["director"])
        if "Uma Thurman" in c and d == "Quentin Tarantino":
            keep.append(True)
        else:
            keep.append(False)
    df_matches = df_matches[keep]
    df_matches = df_matches.sort_values(by="runtime", ascending=True)
    return df_matches


def franchise_vs_standalone(df):
    df_labeled = df.copy()
    groups = []
    for v in df_labeled["belongs_to_collection"]:
        if pd.isna(v):
            groups.append("standalone")
        else:
            groups.append("franchise")
    df_labeled["group"] = groups
    grouped = df_labeled.groupby("group")
    # roi is a median: one huge film moves the mean and not the median.
    df_summary = pd.DataFrame({
        "movies": grouped.size(),
        "mean_revenue": grouped["revenue_musd"].mean(),
        "median_roi": grouped["roi"].median(),
        "mean_budget": grouped["budget_musd"].mean(),
        "mean_popularity": grouped["popularity"].mean(),
        "mean_rating": grouped["vote_average"].mean(),
    })
    return df_summary


def top_franchises(df):
    df_franchises = df[df["belongs_to_collection"].notna()].copy()
    names = []
    for v in df_franchises["belongs_to_collection"]:
        if v not in names:
            names.append(v)
    rows = []
    for name in names:
        part = df_franchises[df_franchises["belongs_to_collection"] == name]
        total_rev = part["revenue_musd"].sum()
        mean_rev = part["revenue_musd"].mean()
        total_bud = part["budget_musd"].sum()
        mean_bud = part["budget_musd"].mean()
        mean_rate = part["vote_average"].mean()
        rows.append({
            "franchise": name,
            "movies": len(part),
            "total_revenue": total_rev,
            "mean_revenue": mean_rev,
            "total_budget": total_bud,
            "mean_budget": mean_bud,
            "mean_rating": mean_rate,
        })
    df_summary = pd.DataFrame(rows)
    if len(df_summary) > 0:
        df_summary = df_summary.sort_values(by="total_revenue", ascending=False)
        df_summary = df_summary.reset_index(drop=True)
    return df_summary


def top_directors(df):
    df_directors = df[df["director"].notna()].copy()
    names = []
    for v in df_directors["director"]:
        if v not in names:
            names.append(v)
    rows = []
    for name in names:
        part = df_directors[df_directors["director"] == name]
        rows.append({
            "director": name,
            "movies": len(part),
            "total_revenue": part["revenue_musd"].sum(),
            "mean_rating": part["vote_average"].mean(),
        })
    df_summary = pd.DataFrame(rows)
    if len(df_summary) > 0:
        df_summary = df_summary.sort_values(by="total_revenue", ascending=False)
        df_summary = df_summary.reset_index(drop=True)
    return df_summary
