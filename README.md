# tmdb movie analysis

small lab. fetch 18 movies, clean the table, check profit and distributions,
then chart it. with no api key it runs from data/tmdb_backup.json.

## run

```
pip install -r requirements.txt
copy .env.example .env
pytest
python -m src.tmdb_client
python -m src.main
python -m src.build_report
```

open analysis.ipynb and run it top to bottom.

`build_report` writes reports/TMDB_Movie_Data_Analysis_Report.docx and refreshes
the pdf. the pdf step needs Word; without it the docx still builds and the old
pdf stays.

## files

- src/ - all source lives here
- src/tmdb_client.py - fetch from api, falls back to the backup json
- src/cleaning.py - clean
- src/kpis.py - profit, rank, search, groups
- src/visualize.py - 7 plots (5 question charts + distribution + boxplot)
- src/main.py - glue, prints the pipeline
- src/build_report.py - rebuilds the docx (8 charts, 5 tables) and pdf
- tests/ - 31 pytest tests, no network needed
- data/ - backup json (not committed)
- reports/ - docx deliverable (committed); pdf and chart pngs are not
- docs/ - study notes, api notes, pipeline walkthrough, timeline
- analysis.ipynb - all steps incl. eda, runs top to bottom
