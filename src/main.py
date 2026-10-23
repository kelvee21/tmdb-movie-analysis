import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from dotenv import load_dotenv

from src.tmdb_client import fetch_all


def main():
    """Fetch, clean and enrich the records, printing each stage."""
    load_dotenv()
    records = fetch_all()
    df_raw = pd.DataFrame(records)
    print("got", len(df_raw), "movies")

    if len(df_raw) > 0:
        print(df_raw["title"].head(3).tolist())

    from src.cleaning import clean
    df_cleaned = clean(df_raw)
    print("clean shape:", df_cleaned.shape)

    from src.kpis import add_profit_roi
    df_enriched = add_profit_roi(df_cleaned)
    print("profit ok, columns:", df_enriched[["title", "profit", "roi"]].head(2).to_string())


if __name__ == "__main__":
    main()
