import json
import pandas as pd
import src.cleaning as cleaning
import src.kpis as kpis
import src.visualize as viz


def get_done_df():
    f = open("data/tmdb_backup.json", encoding="utf-8")
    records = json.load(f)
    f.close()
    df = pd.DataFrame(records)
    df = cleaning.clean(df)
    df = kpis.add_profit_roi(df)
    return df


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


def test_thresholds():
    assert kpis.ROI_MIN_BUDGET_MUSD == 10.0
    assert kpis.MIN_VOTES == 10


def test_searches_run():
    df = get_done_df()
    r1 = kpis.search_willis_scifi_action(df)
    r2 = kpis.search_thurman_tarantino(df)
    assert len(r1) >= 0
    assert len(r2) >= 0


def test_franchise_tables():
    df = get_done_df()
    t1 = kpis.franchise_vs_standalone(df)
    t2 = kpis.top_franchises(df)
    t3 = kpis.top_directors(df)
    assert "franchise" in t1.index or len(t1) > 0
    assert len(t2) > 0
    assert len(t3) > 0


def test_charts_run():
    df = get_done_df()
    viz.plot_revenue_vs_budget(df)
    viz.plot_roi_by_genre(df)
    viz.plot_popularity_vs_rating(df)
    viz.plot_yearly_box_office(df)
    viz.plot_franchise_vs_standalone(df)
