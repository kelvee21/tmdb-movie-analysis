import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from dotenv import load_dotenv
from tmdb_client import fetch_all


def main():
    load_dotenv()
    records = fetch_all()
    df = pd.DataFrame(records)
    print("got", len(df), "movies")

    if len(df) > 0:
        print(df["title"].head(3).tolist())

    from src.cleaning import clean
    df2 = clean(df)
    print("clean shape:", df2.shape)

    from src.kpis import add_profit_roi
    df3 = add_profit_roi(df2)
    print("profit ok, columns:", df3[["title", "profit", "roi"]].head(2).to_string())


if __name__ == "__main__":
    main()
