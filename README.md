# tmdb movie analysis

small lab. fetch 18 movies, clean table, check profit and charts.

## run

```
pip install -r requirements.txt
copy .env.example .env
pytest
python tmdb_client.py
python app/main.py
```

open analysis.ipynb top to bottom.

make report:

```
python reports/build_report.py
```

## files

- tmdb_client.py - fetch from api
- src/cleaning.py - clean
- src/kpis.py - profit, rank, search
- src/visualize.py - 5 charts
- analysis.ipynb - shows all steps
- reports/build_report.py - makes docx
