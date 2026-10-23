# data/ (gitignored except this note)

Runtime + backup JSON lives here and is never committed:
- `raw_movies.json` — written by `python -m src.tmdb_client`.
- `tmdb_backup.json` — your large offline backup (same record shape).
  Fetch falls back to it when the API is unreachable.

Both are gitignored. The notebook and report fall back to the backup when there is no
key; tests fall back to the fake records in `tests/helpers.py` when the backup is absent.
