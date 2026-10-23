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
    """Mean roi per genre, sorted, with the film count written on the tick.

    with only 18 rows some genres have 1 or 2 films, so a bar on its own would
    read as a finding when it is really one film. putting n= on the label makes
    the reader see which bars are too thin to mean anything.
    """
    genres = []
    for g in df["genres"]:
        if isinstance(g, str):
            for p in g.split("|"):
                if p not in genres:
                    genres.append(p)

    means = []
    counts = []
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
        counts.append(len(vals))
        if len(vals) > 0:
            s = 0
            for v in vals:
                s = s + v
            means.append(s / len(vals))
        else:
            means.append(0)

    order = sorted(range(len(genres)), key=lambda i: means[i], reverse=True)
    labels = [f"{genres[i]}\n(n={counts[i]})" for i in order]
    values = [means[i] for i in order]

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_xlabel("genre, with number of films")
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
    df_dated = df.copy()
    df_dated["year"] = pd.to_datetime(df_dated["release_date"]).dt.year
    years = []
    vals = []
    for y in sorted(df_dated["year"].dropna().unique()):
        part = df_dated[df_dated["year"] == y]
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
    df_labeled = df.copy()
    groups = []
    for v in df_labeled["belongs_to_collection"]:
        if pd.isna(v):
            groups.append("standalone")
        else:
            groups.append("franchise")
    df_labeled["group"] = groups
    g = df_labeled.groupby("group")["revenue_musd"].mean()

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


def plot_distribution(df, column, bins=20):
    """Histogram of one numeric column with the median marked.

    eda helper: shows the shape of a column (skew, heaps at the edges)
    before any kpi work, so later numbers get read with the spread in mind.
    """
    values = df[column].dropna()
    median = values.median()
    fig, ax = plt.subplots()
    ax.hist(values, bins=bins)
    if pd.notna(median):
        ax.axvline(median, linestyle="--")
    ax.set_xlabel(column)
    ax.set_ylabel("movies")
    title = f"{column} distribution"
    if pd.notna(median):
        title = title + f" (median={median:g})"
    ax.set_title(title)
    return ax


def plot_boxplot(df, column):
    """Horizontal boxplot of one numeric column, quick outlier view."""
    values = df[column].dropna()
    fig, ax = plt.subplots()
    # no tick_labels here, that only exists in matplotlib 3.9 and the
    # requirements allow 3.8. the column name is already on the axis.
    ax.boxplot(values, vert=False)
    ax.set_yticks([])
    ax.set_xlabel(column)
    ax.set_title(f"{column} boxplot")
    return ax
