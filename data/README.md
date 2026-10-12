# data/ (gitignored except this note)

Runtime + backup JSON lives here and is never committed:
- `raw_movies.json` — written by `python tmdb_client.py`.
- `tmdb_backup.json` — your large offline backup (same record shape).
  Fetch falls back to it when the API is unreachable.
