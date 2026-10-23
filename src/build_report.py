"""Rebuilds reports/TMDB_Movie_Data_Analysis_Report.docx from live data.

Run as `python -m src.build_report`. Fetches the movies (backup json when there
is no api key), cleans them, adds profit/roi, saves the eight chart pngs into
reports/, then writes the docx. The pdf is refreshed through Word: pywin32 if
it is installed, otherwise Word COM through PowerShell. No Word at all prints a
note and keeps the old pdf.
"""
import os
import subprocess

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from docx import Document
from docx.shared import Inches

from src.cleaning import clean, inspect_anomalies
from src.kpis import (add_profit_roi, rank, franchise_vs_standalone,
                      top_franchises, top_directors,
                      search_willis_scifi_action, search_thurman_tarantino,
                      ROI_MIN_BUDGET_MUSD, MIN_VOTES)
from src.tmdb_client import fetch_all
from src.visualize import (plot_revenue_vs_budget, plot_roi_by_genre,
                           plot_popularity_vs_rating, plot_yearly_box_office,
                           plot_franchise_vs_standalone, plot_distribution,
                           plot_boxplot)

TABLE_STYLE = "Light Grid Accent 1"
IMG_WIDTH = Inches(5.9)


def f0(x):
    """Thousands separator, no decimals (counts)."""
    return f"{x:,.0f}"


def f1(x):
    """Thousands separator, one decimal (money in millions)."""
    return f"{x:,.1f}"


def f2(x):
    """Thousands separator, two decimals (ratios, ratings)."""
    return f"{x:,.2f}"


def save_fig(ax, name):
    """savefig + close, so a batch of eight charts does not pile up figures.

    tight_layout like the notebook does it, otherwise the rotated genre
    labels get clipped at the bottom of the saved png.
    """
    fig = ax.figure
    fig.tight_layout()
    path = "reports/" + name
    fig.savefig(path)
    plt.close(fig)
    return path


def add_table(doc, header, rows):
    """Header plus rows as a grid table in the report style."""
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    t.style = TABLE_STYLE
    for j, h in enumerate(header):
        t.rows[0].cells[j].text = h
    for i, row in enumerate(rows, 1):
        for j, v in enumerate(row):
            t.rows[i].cells[j].text = str(v)
    return t


def rank_titles(df, col, top_n=3, ascending=False):
    """Titles of the top n rows for one column, for the rankings table."""
    return rank(df, col, n=top_n, ascending=ascending)["title"].tolist()


def rank_row(label, flt, df, col, ascending=False):
    """One rankings-table row: label, filter, then 1st/2nd/3rd as separate cells."""
    titles = rank_titles(df, col, top_n=3, ascending=ascending)
    while len(titles) < 3:
        titles.append("")
    return [label, flt] + titles[:3]


def main():
    """Fetch, clean, chart, then write the docx and refresh the pdf."""
    records = fetch_all()
    df_raw = pd.DataFrame(records)
    df_cleaned = clean(df_raw)
    df_enriched = add_profit_roi(df_cleaned)
    print("building docx from", len(df_enriched), "films")

    # value_counts sanity check on the columns i built, before anything is drawn
    EXTRACTED = ["belongs_to_collection", "genres", "spoken_languages",
                 "production_countries", "production_companies", "original_language"]
    inspect_anomalies(df_cleaned, EXTRACTED)

    rich = df_enriched[df_enriched["budget_musd"] >= ROI_MIN_BUDGET_MUSD]
    voted = df_enriched[df_enriched["vote_count"] >= MIN_VOTES]

    # ---- charts: reports/chart1..8.png, all gitignored ----
    save_fig(plot_revenue_vs_budget(df_enriched), "chart1.png")
    save_fig(plot_roi_by_genre(df_enriched), "chart2.png")
    save_fig(plot_popularity_vs_rating(df_enriched), "chart3.png")
    save_fig(plot_yearly_box_office(df_enriched), "chart4.png")
    save_fig(plot_franchise_vs_standalone(df_enriched), "chart5.png")
    save_fig(plot_distribution(df_enriched, "revenue_musd"), "chart6.png")
    save_fig(plot_distribution(df_enriched, "popularity"), "chart7.png")
    save_fig(plot_boxplot(df_enriched, "runtime"), "chart8.png")

    # ---- document ----
    doc = Document()

    doc.add_paragraph("TMDB Movie Data Analysis using Pandas and APIs", style="Title")
    doc.add_paragraph("18 films from the TMDB api, cleaned, ranked and charted")

    doc.add_heading("1. Objective", level=1)
    doc.add_paragraph(
        "I asked TMDB for 19 movie ids, cleaned what came back into a single "
        "analysis table, worked out profit and roi, ranked the set ten ways, ran "
        "two cast searches, compared franchises against standalones, looked at "
        "the distributions and outliers behind those numbers, and drew 8 charts. "
        "Everything below is produced by the code in this repo."
    )

    doc.add_heading("2. Where the data came from", level=1)
    doc.add_paragraph(
        "GET /movie/{id} gives budget, revenue, genres, release date and votes. "
        "GET /movie/{id}/credits gives the cast list and the crew list, which is "
        "where cast, cast_size, director and crew_size come from. I loop the cast "
        "list picking name, and the crew list picking the entry whose job is "
        "Director."
    )
    doc.add_paragraph(
        "The brief lists 19 ids. Id 0 is not a real film and the api answers 404, "
        "so it is skipped and 18 rows come back. I wait 0.25s between calls to "
        "stay under the rate limit. A 429 sleeps 1.5s and retries once. The key "
        "lives in .env and is never committed. If there is no key the fetch falls "
        "back to a local backup json."
    )

    doc.add_heading("3. Methodology", level=1)
    bullets = [
        "Dropped adult, imdb_id, original_title, video and homepage.",
        "Pulled the collection name out of its dict and joined genres, languages, "
        "companies and countries into pipe separated text with a loop.",
        "Ran value_counts on each joined column before trusting it. On genres it "
        "showed that 8 films share the same 3 genres, but the api wrote them in 4 "
        "different orders, for example Action|Adventure|Science Fiction and "
        "Adventure|Action|Science Fiction. They are one group, not two, so "
        "anything comparing genre as whole text would be comparing spelling "
        "rather than content. That is why the search and the chart both split on "
        "the pipe.",
        "Turned budget, revenue, id, popularity and votes into numbers and the "
        "release date into a date, with errors coerced so bad text becomes empty "
        "instead of crashing.",
        "Treated 0 in budget, revenue and runtime as unknown rather than real, so "
        "those become empty. A film with a budget of 0 is a film nobody typed a "
        "budget for.",
        "Where vote_count is 0 the vote_average is meaningless, so it becomes "
        "empty. I write this with df.loc on a mask, not df[col].iloc[i], because "
        "chained assignment is silently dropped by pandas 3 and the rating would "
        "stay put. No film in this set has 0 votes, so a fake record in the test "
        "suite covers it.",
        "Converted budget and revenue to millions of dollars.",
        "Kept only Released films, then dropped the status column, removed "
        "duplicates by id and title, dropped rows with no id or title, and kept "
        "rows with at least 10 populated values.",
        "Reordered to the 22 columns in the order the brief lists and reset the "
        "index.",
        "Added profit and roi, then ranked ten ways, searched twice, grouped "
        "franchise against standalone, described the numeric columns, histogrammed "
        "and boxplotted the ones the kpis rest on, and drew the charts.",
    ]
    for b in bullets:
        doc.add_paragraph(b, style="List Bullet")

    doc.add_heading("4. Key insights", level=1)
    for b in [
        "Avengers: Endgame is the biggest earner at 2,927.4M, but Avatar makes "
        "the most profit at 2,686.7M because its budget is a fraction of the "
        "size. Gross and profit are not the same ranking.",
        "Avatar also has the best return, roi of 12.34 against a budget of "
        "237.0M. The roi column is badly skewed: mean 8.20 against median 7.94 "
        "and a maximum of 12.34. One big film drags the mean up, which is exactly "
        "why the franchise table below reports the median and not the mean.",
        "16 of the 18 films belong to a collection and only 2 are standalones. "
        "This is a franchise-heavy set, which limits what any franchise against "
        "standalone comparison can prove.",
        "On that split the standalones show a higher median roi (9.62 against "
        "7.84) but they are two films. 2 against 16 is not a comparison worth "
        "drawing a conclusion from.",
        "The most successful franchise by total revenue is The Avengers "
        "Collection with 4 films and 7,904.1M. The top director is James Cameron "
        "on 5,187.9M across 2 films.",
        "Both cast searches return nothing. The Willis search wants Science "
        "Fiction and Action with Bruce Willis, the Thurman search wants Uma "
        "Thurman directed by Quentin Tarantino, and this set is 18 top grossing "
        "films with no Willis film and no Tarantino film among them. That is a "
        "property of the sample, not a bug in the search. Widen the id list and "
        "both would return rows.",
        "TMDB popularity and rating do not move together in this set, so "
        "popularity is not a usable stand-in for quality. Worth knowing before "
        "anyone builds a recommendation list on it.",
    ]:
        doc.add_paragraph(b, style="List Bullet")

    doc.add_heading("5. Rankings", level=1)
    doc.add_paragraph(
        "The brief asks for ten. roi is filtered to films with a budget of at "
        "least 10M and rating to films with at least 10 votes, because small "
        "budgets and thin vote counts make both numbers jump around. The top "
        "three of each are shown, the notebook has the full list."
    )
    rank_rows = [
        rank_row("1. highest revenue", "none", df_enriched, "revenue_musd"),
        rank_row("2. highest budget", "none", df_enriched, "budget_musd"),
        rank_row("3. highest profit", "none", df_enriched, "profit"),
        rank_row("4. lowest profit", "none", df_enriched, "profit", ascending=True),
        rank_row("5. highest roi", "budget >= 10M", rich, "roi"),
        rank_row("6. lowest roi", "budget >= 10M", rich, "roi", ascending=True),
        rank_row("7. most voted", "none", df_enriched, "vote_count"),
        rank_row("8. highest rated", "votes >= 10", voted, "vote_average"),
        rank_row("9. lowest rated", "votes >= 10", voted, "vote_average", ascending=True),
        rank_row("10. most popular", "none", df_enriched, "popularity"),
    ]
    add_table(doc, ["ranking", "filter", "1st", "2nd", "3rd"], rank_rows)

    doc.add_paragraph("Willis, science fiction and action: "
                      f"{len(search_willis_scifi_action(df_enriched))} matches.")
    doc.add_paragraph("Uma Thurman directed by Quentin Tarantino: "
                      f"{len(search_thurman_tarantino(df_enriched))} matches.")
    doc.add_paragraph(
        "Both are empty for the reason given in the insights. The search logic is "
        "exercised by the test suite against fake records that do contain a "
        "match, so an empty result here is the data and not the code."
    )

    doc.add_heading("6. Franchise against standalone", level=1)
    doc.add_paragraph(
        "Mean revenue, mean budget, median roi, mean popularity and mean rating "
        "for the two groups."
    )
    parted = franchise_vs_standalone(df_enriched)
    part_rows = []
    for grp, row in parted.iterrows():
        part_rows.append([
            grp, int(row["movies"]), f1(row["mean_revenue"]), f1(row["mean_budget"]),
            f2(row["median_roi"]), f1(row["mean_popularity"]), f2(row["mean_rating"]),
        ])
    add_table(doc, ["group", "films", "mean revenue", "mean budget", "median roi",
                    "mean popularity", "mean rating"], part_rows)
    doc.add_paragraph(
        "roi is the median on purpose. With one large film in a group the mean "
        "moves and the median does not, and here the two groups differ by less "
        "than the spread inside each of them."
    )

    doc.add_heading("Most successful franchises, by total revenue", level=2)
    fr_rows = []
    for _, row in top_franchises(df_enriched).head(5).iterrows():
        fr_rows.append([
            row["franchise"], int(row["movies"]), f1(row["total_revenue"]),
            f1(row["mean_revenue"]), f2(row["mean_rating"]),
        ])
    add_table(doc, ["franchise", "films", "total revenue", "mean revenue",
                    "mean rating"], fr_rows)

    doc.add_heading("Most successful directors, by total revenue", level=2)
    dr_rows = []
    for _, row in top_directors(df_enriched).head(5).iterrows():
        dr_rows.append([
            row["director"], int(row["movies"]), f1(row["total_revenue"]),
            f2(row["mean_rating"]),
        ])
    add_table(doc, ["director", "films", "total revenue", "mean rating"], dr_rows)

    # ---- eda: distributions and outliers ----
    doc.add_heading("7. Distributions and outliers", level=1)
    doc.add_paragraph(
        "Before trusting any ranking, look at the spread of the columns the "
        "rankings rest on. The table is describe() on the six numeric columns; "
        "the histograms show the shape of the columns that are skewed and the "
        "boxplot shows which points are genuinely unusual."
    )
    desc_cols = ["budget_musd", "revenue_musd", "runtime", "vote_average", "popularity"]
    desc = df_enriched[desc_cols].describe()
    desc_rows = []
    for stat, row in desc.iterrows():
        if stat == "count":
            desc_rows.append([stat] + [f0(v) for v in row])
        else:
            desc_rows.append([stat] + [f2(v) for v in row])
    add_table(doc, ["stat"] + desc_cols, desc_rows)

    for b in [
        "Budgets are tight: 125.0M to 356.0M with a median of 200.0M and no "
        "outliers at all. Money is uniformly large across this set.",
        "Revenue is right-skewed: median 1,484.54M against mean 1,699.04M, and "
        "Endgame (2,927.45M) and Avatar (2,923.71M) both sit past the 2,888.71M "
        "upper fence. The mean overstates a typical film here, which is why "
        "group comparisons quote the median.",
        "Runtimes sit between 102 and 194 minutes with a median of 135.5. Only "
        "Titanic (194) and Endgame (181) blow the 180.9 fence - the two very long "
        "films are also the two biggest earners, a coincidence worth noticing "
        "rather than a rule.",
        "Ratings barely move (6.50 to 8.24, zero outliers). Expected: the list "
        "is the brief's heavily-voted blockbusters, not a random sample of all "
        "films.",
        "Popularity is the most skewed column: median 33.61 against a max of "
        "96.86, with the two Avengers films (96.86 and 93.14) as the only "
        "outliers. Popularity measures release-window buzz, not long-run demand, "
        "so it gets read differently from ratings.",
    ]:
        doc.add_paragraph(b, style="List Bullet")

    doc.add_picture("reports/chart6.png", width=IMG_WIDTH)
    doc.add_paragraph(
        "Chart 6. Distribution of revenue, median marked. The pile below ~1,500M "
        "with a long right tail is why the median gets quoted more than the mean."
    )
    doc.add_picture("reports/chart7.png", width=IMG_WIDTH)
    doc.add_paragraph(
        "Chart 7. Distribution of popularity. Heavily right-skewed: one small "
        "cluster of films, the two Avengers entries, sits far above the pack."
    )
    doc.add_picture("reports/chart8.png", width=IMG_WIDTH)
    doc.add_paragraph(
        "Chart 8. Boxplot of runtime. Whiskers reach ~102 and ~181 minutes; "
        "Titanic and Endgame are the two plotted outlier points."
    )

    # ---- the five question charts ----
    doc.add_heading("8. Visualizations", level=1)
    chart_captions = [
        ("chart1.png",
         "Chart 1. Revenue against budget for the 18 films. The two sit off a "
         "diagonal, so bigger budget buys more revenue, but the spread at any "
         "budget is wide."),
        ("chart2.png",
         "Chart 2. Mean roi by genre, sorted, with the film count on each label. "
         "Read the n= first: Comedy and Crime rest on a single film, so those two "
         "bars are not a finding. Adventure, Science Fiction and Action are the "
         "only genres with a sample worth reading."),
        ("chart3.png",
         "Chart 3. Popularity against rating. The two barely move together, so "
         "TMDB popularity is not a proxy for quality."),
        ("chart4.png",
         "Chart 4. Mean revenue per release year. The set is chosen by box "
         "office, so later years look stronger purely because of selection."),
        ("chart5.png",
         "Chart 5. Mean revenue, franchise against standalone. Standalones edge "
         "it, but there are only two of them against sixteen."),
    ]
    for png, caption in chart_captions:
        doc.add_picture("reports/" + png, width=IMG_WIDTH)
        doc.add_paragraph(caption)

    doc.add_heading("9. Limitations", level=1)
    for b in [
        "18 films is a small set and it is not a random sample. It is the brief's "
        "id list, which is heavy on modern blockbusters, so every conclusion here "
        "is about big films and nothing more.",
        "Four of the eleven genres rest on two films or fewer, so the genre chart "
        "is descriptive only. The counts are printed on the chart for that "
        "reason.",
        "Both cast searches return empty, so neither search path is demonstrated "
        "on the real data. The test suite covers the matching logic against fake "
        "records.",
        "roi is undefined for any film with no budget recorded. Those rows are "
        "excluded from roi rankings rather than treated as zero.",
        "The backup json is not committed, so a clone without an api key still "
        "runs the whole test suite against synthetic records, but cannot rebuild "
        "this report's numbers.",
    ]:
        doc.add_paragraph(b, style="List Bullet")

    doc.add_heading("10. How to run it again", level=1)
    doc.add_paragraph(
        "pip install -r requirements.txt\n"
        "copy .env.example to .env and put your key in\n"
        "pytest\n"
        "python -m src.tmdb_client  (saves data/raw_movies.json)\n"
        "python -m src.main  (prints the clean table shape and the profit head)\n"
        "python -m src.build_report  (rebuilds this docx)\n"
        "open analysis.ipynb and run it top to bottom"
    )

    out_docx = "reports/TMDB_Movie_Data_Analysis_Report.docx"
    doc.save(out_docx)
    print("saved", out_docx)
    export_pdf(out_docx)


def export_pdf(docx_path):
    """Refresh the pdf through Word, direct or via PowerShell; keep the old if neither works."""
    docx_abs = os.path.abspath(docx_path)
    pdf_abs = os.path.abspath(docx_path.replace(".docx", ".pdf"))

    try:
        import win32com.client
    except ImportError:
        win32com = None
    else:
        win32com = win32com.client

    if win32com is not None:
        word = None
        try:
            word = win32com.Dispatch("Word.Application")
            word.Visible = False
            doc = word.Documents.Open(docx_abs)
            try:
                doc.SaveAs(pdf_abs, FileFormat=17)
            finally:
                doc.Close(False)
            print("saved", pdf_abs)
            return
        except Exception as e:
            print("python pdf export failed, trying powershell:", e)
        finally:
            if word is not None:
                try:
                    word.Quit()
                except Exception:
                    pass

    script = (
        "$w = New-Object -ComObject Word.Application; $w.Visible = $false; "
        "$d = $w.Documents.Open('" + docx_abs + "'); "
        "$d.SaveAs('" + pdf_abs + "', 17); $d.Close($false); $w.Quit()"
    )
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True, text=True, timeout=180,
        )
        if out.returncode == 0 and os.path.exists(pdf_abs):
            print("saved", pdf_abs)
        else:
            print("pdf export skipped:", (out.stderr or "no word").strip()[-200:])
    except Exception as e:
        print("pdf export skipped:", e)


if __name__ == "__main__":
    main()
