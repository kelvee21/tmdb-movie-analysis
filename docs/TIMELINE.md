# my week

deadline sat 17th 8pm.

## wed - clean

drop 5 cols. get collection name. join genres, languages, companies, countries with |.
fix numbers with to_numeric, dates with to_datetime.
0 -> empty, dollars / 1000000 to musd.
keep Released only, drop dupes by id title.

check: 22 cols, 18 rows.

## thu - profit

profit = revenue - budget. roi = revenue / budget.
rank = sort + head 5.

10 lists: revenue, budget, profit top/bottom, roi top/bottom where budget >= 10,
votes, rating top/bottom where votes >= 10, popularity.

## fri - search

willis = genres has Science Fiction and Action and cast has Bruce Willis, sort by rating.
thurman = cast has Uma Thurman and director is Quentin Tarantino, sort by runtime.
both give 0 here because set is top grossing films, I write that down.

franchise vs single by collection empty or not. mean revenue, budget, roi, popularity, rating.
top franchises and directors by total revenue.

## sat - charts + report

5 plots: budget vs revenue dots, roi by genre bars, popularity vs rating dots,
yearly mean line, franchise vs single bars.

freeze at 3pm. run pytest, app/main.py, build_report.py. fill docx. submit by 8pm.

```
pytest
python app/main.py
python reports/build_report.py
```
