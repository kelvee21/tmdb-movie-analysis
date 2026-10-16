import pandas as pd
import matplotlib.pyplot as plt


def plot_revenue_vs_budget(df):
    fig, ax = plt.subplots()
    ax.scatter(df["budget_musd"], df["revenue_musd"])
    ax.set_xlabel("budget (musd)")
    ax.set_ylabel("revenue (musd)")
    ax.set_title("revenue vs budget")
    return ax


def plot_roi_by_genre(df):
    genres = []
    for g in df["genres"]:
        if isinstance(g, str):
            parts = g.split("|")
            for p in parts:
                if p not in genres:
                    genres.append(p)

    means = []
    for gen in genres:
        vals = []
        for i in range(len(df)):
            row = df.iloc[i]
            g = str(row["genres"])
            parts = g.split("|")
            if gen in parts:
                v = row["roi"]
                if pd.notna(v):
                    vals.append(v)
        if len(vals) > 0:
            s = 0
            for v in vals:
                s = s + v
            means.append(s / len(vals))
        else:
            means.append(0)

    fig, ax = plt.subplots()
    ax.bar(genres, means)
    ax.set_xlabel("genre")
    ax.set_ylabel("mean roi")
    ax.set_title("roi by genre")
    plt.xticks(rotation=45)
    return ax


def plot_popularity_vs_rating(df):
    fig, ax = plt.subplots()
    ax.scatter(df["popularity"], df["vote_average"])
    ax.set_xlabel("popularity")
    ax.set_ylabel("rating")
    ax.set_title("popularity vs rating")
    return ax


def plot_yearly_box_office(df):
    df2 = df.copy()
    df2["year"] = pd.to_datetime(df2["release_date"]).dt.year
    years = []
    vals = []
    for y in sorted(df2["year"].dropna().unique()):
        part = df2[df2["year"] == y]
        s = 0
        n = 0
        for v in part["revenue_musd"]:
            if pd.notna(v):
                s = s + v
                n = n + 1
        if n > 0:
            years.append(y)
            vals.append(s / n)
    fig, ax = plt.subplots()
    ax.plot(years, vals)
    ax.set_xlabel("year")
    ax.set_ylabel("mean revenue (musd)")
    ax.set_title("box office by year")
    return ax


def plot_franchise_vs_standalone(df):
    groups = []
    for v in df["belongs_to_collection"]:
        if pd.isna(v):
            groups.append("standalone")
        else:
            groups.append("franchise")
    df2 = df.copy()
    df2["group"] = groups
    g = df2.groupby("group")["revenue_musd"].mean()

    labels = []
    vals = []
    for k in g.index:
        labels.append(k)
        vals.append(g[k])

    fig, ax = plt.subplots()
    ax.bar(labels, vals)
    ax.set_xlabel("group")
    ax.set_ylabel("mean revenue (musd)")
    ax.set_title("franchise vs standalone")
    return ax
