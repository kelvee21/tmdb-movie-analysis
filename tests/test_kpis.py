import pandas as pd

import src.kpis as kpis
import src.visualize as viz
from tests.helpers import done_df, fake_df


def test_profit_math():
    df = pd.DataFrame([{"revenue_musd": 800.0, "budget_musd": 200.0}])
    out = kpis.add_profit_roi(df)
    assert out["profit"][0] == 600.0
    assert out["roi"][0] == 4.0


def test_rank_top():
    df = pd.DataFrame([
        {"title": "A", "revenue_musd": 100.0},
        {"title": "B", "revenue_musd": 300.0},
        {"title": "C", "revenue_musd": 200.0},
    ])
    out = kpis.rank(df, "revenue_musd", n=2)
    assert out["title"].tolist() == ["B", "C"]


def test_rank_bottom():
    df = pd.DataFrame([
        {"title": "A", "revenue_musd": 100.0},
        {"title": "B", "revenue_musd": 300.0},
        {"title": "C", "revenue_musd": 200.0},
    ])
    out = kpis.rank(df, "revenue_musd", n=1, ascending=True)
    assert out["title"].tolist() == ["A"]


def test_thresholds():
    assert kpis.ROI_MIN_BUDGET_MUSD == 10.0
    assert kpis.MIN_VOTES == 10


def test_searches_run():
    df = done_df()
    r1 = kpis.search_willis_scifi_action(df)
    r2 = kpis.search_thurman_tarantino(df)
    assert len(r1) >= 0
    assert len(r2) >= 0


def test_willis_search_finds_the_fake_row():
    """the real 18 movie set has no Willis film, the fake one does."""
    df = fake_df()
    r = kpis.search_willis_scifi_action(df)
    assert "Alpha" in r["title"].tolist()
    assert list(r["vote_average"]) == sorted(r["vote_average"], reverse=True)


def test_franchise_tables():
    df = done_df()
    t1 = kpis.franchise_vs_standalone(df)
    t2 = kpis.top_franchises(df)
    t3 = kpis.top_directors(df)
    assert "franchise" in t1.index or len(t1) > 0
    assert len(t2) > 0
    assert len(t3) > 0


def test_franchise_table_uses_median_roi():
    """The brief asks for median ROI here, not mean."""
    df = fake_df()
    t = kpis.franchise_vs_standalone(df)
    assert "median_roi" in t.columns
    assert "mean_roi" not in t.columns


def test_median_roi_is_not_the_mean():
    """Mean and median only differ if there is an outlier, so check both.

    franchise roi is 3.0, 3.0, 19.0 -> median 3.0, mean about 8.33.
    standalone roi is 2.0, 1.0, 40.0 -> median 2.0, mean about 14.33.
    """
    df = fake_df()
    t = kpis.franchise_vs_standalone(df)
    assert abs(t.loc["franchise", "median_roi"] - 3.0) < 1e-9
    assert abs(t.loc["standalone", "median_roi"] - 2.0) < 1e-9
    # the mean gets dragged up by the outlier, the median does not move
    franchise = df[df["belongs_to_collection"].notna()]["roi"].tolist()
    mean_franchise = sum(franchise) / len(franchise)
    assert mean_franchise > 3.0


def test_franchise_vs_standalone_has_both_groups():
    df = fake_df()
    t = kpis.franchise_vs_standalone(df)
    assert "franchise" in t.index
    assert "standalone" in t.index


def test_top_franchises_columns():
    df = fake_df()
    t = kpis.top_franchises(df)
    for col in ["movies", "total_revenue", "mean_revenue",
                "total_budget", "mean_budget", "mean_rating"]:
        assert col in t.columns
    # Alpha Collection holds Alpha, Beta and Epsilon
    assert t.iloc[0]["franchise"] == "Alpha Collection"
    assert t.iloc[0]["movies"] == 3


def test_top_directors_columns():
    df = fake_df()
    t = kpis.top_directors(df)
    for col in ["movies", "total_revenue", "mean_rating"]:
        assert col in t.columns
    # Jane Doe has the three Alpha Collection films and the biggest total
    assert t.iloc[0]["director"] == "Jane Doe"
    assert t.iloc[0]["movies"] == 3


def test_charts_run():
    df = done_df()
    viz.plot_revenue_vs_budget(df)
    viz.plot_roi_by_genre(df)
    viz.plot_popularity_vs_rating(df)
    viz.plot_yearly_box_office(df)
    viz.plot_franchise_vs_standalone(df)
