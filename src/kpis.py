import pandas as pd

ROI_MIN_BUDGET_MUSD = 10.0
MIN_VOTES = 10


def add_profit_roi(df):
    df2 = df.copy()
    df2["profit"] = df2["revenue_musd"] - df2["budget_musd"]
    df2["roi"] = df2["revenue_musd"] / df2["budget_musd"]
    return df2


def rank(df, col, n=5, ascending=False):
    df2 = df.copy()
    if ascending:
        df2 = df2.sort_values(by=col, ascending=True)
    else:
        df2 = df2.sort_values(by=col, ascending=False)
    return df2.head(n)


def search_willis_scifi_action(df):
    df2 = df.copy()
    keep = []
    for i in range(len(df2)):
        row = df2.iloc[i]
        g = str(row["genres"])
        c = str(row["cast"])
        if "Science Fiction" in g and "Action" in g and "Bruce Willis" in c:
            keep.append(True)
        else:
            keep.append(False)
    df2 = df2[keep]
    df2 = df2.sort_values(by="vote_average", ascending=False)
    return df2


def search_thurman_tarantino(df):
    df2 = df.copy()
    keep = []
    for i in range(len(df2)):
        row = df2.iloc[i]
        c = str(row["cast"])
        d = str(row["director"])
        if "Uma Thurman" in c and d == "Quentin Tarantino":
            keep.append(True)
        else:
            keep.append(False)
    df2 = df2[keep]
    df2 = df2.sort_values(by="runtime", ascending=True)
    return df2


def franchise_vs_standalone(df):
    df2 = df.copy()
    groups = []
    for v in df2["belongs_to_collection"]:
        if pd.isna(v):
            groups.append("standalone")
        else:
            groups.append("franchise")
    df2["group"] = groups
    g = df2.groupby("group")
    out = pd.DataFrame({
        "movies": g.size(),
        "mean_revenue": g["revenue_musd"].mean(),
        "mean_budget": g["budget_musd"].mean(),
        "mean_roi": g["roi"].mean(),
        "mean_popularity": g["popularity"].mean(),
        "mean_rating": g["vote_average"].mean(),
    })
    return out


def top_franchises(df):
    df2 = df[df["belongs_to_collection"].notna()].copy()
    names = []
    for v in df2["belongs_to_collection"]:
        if v not in names:
            names.append(v)
    rows = []
    for name in names:
        part = df2[df2["belongs_to_collection"] == name]
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
    out = pd.DataFrame(rows)
    if len(out) > 0:
        out = out.sort_values(by="total_revenue", ascending=False)
        out = out.reset_index(drop=True)
    return out


def top_directors(df):
    df2 = df[df["director"].notna()].copy()
    names = []
    for v in df2["director"]:
        if v not in names:
            names.append(v)
    rows = []
    for name in names:
        part = df2[df2["director"] == name]
        rows.append({
            "director": name,
            "movies": len(part),
            "total_revenue": part["revenue_musd"].sum(),
            "mean_rating": part["vote_average"].mean(),
        })
    out = pd.DataFrame(rows)
    if len(out) > 0:
        out = out.sort_values(by="total_revenue", ascending=False)
        out = out.reset_index(drop=True)
    return out
