# TMDB Movie Data Analysis (DEM02 lab)

End-to-end movie data pipeline: fetch 19 fixed TMDB IDs, clean nested
JSON columns, compute ranking/profit/ROI/franchise/director KPIs, visualize.
Built for the DEM02 "Python Programming with Pandas and NumPy" lab and the
Applied AI "Multi-Stage AI Workflow" lab (this repo is the workflow's object).

## Quickstart
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your TMDB v3 API key
   (free at https://www.themoviedb.org/settings/api). Never commit `.env`.
3. `pytest` — mocked unit tests, pass offline.
4. `python tmdb_client.py` — live fetch to `data/raw_movies.json`
   (falls back to `data/tmdb_backup.json` when offline).
5. Open `analysis.ipynb` and run Step 1-4 sections in order.

## Layout
- `tmdb_client.py` — Step 1: v3 API client (`/movie/{id}` + `/credits`).
  Auth is the `api_key` query param; the v4 read token in `.env` is the
  Bearer alternative for v4 endpoints.
- `analysis.ipynb` — Steps 2-4: cleaning, KPIs (ranking UDF, ROI>=10M,
  rating>=10 votes, franchise vs standalone), five matplotlib plots.
- `reports/build_report.py` — regenerates the Word final report skeleton.
- `data/` — put the offline backup here as `data/tmdb_backup.json`.

## Lab mapping
| Lab step | Code |
|---|---|
| 1 Fetch | `tmdb_client.fetch_all()` |
| 2 Clean | notebook Step 2 (pipe-separated nested fields, 0->NaN, Musd, Released-only) |
| 3 KPIs | notebook Step 3 (ranking UDF, searches, franchise/directors) |
| 4 Visualize | notebook Step 4 (revenue/budget, ROI by genre, popularity/rating, yearly, franchise) |
