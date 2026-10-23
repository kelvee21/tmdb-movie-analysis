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
yearly mean line, franchise vs single bars. (+2 eda plots later)

freeze at 3pm. run pytest, python -m src.main, python -m src.build_report. fill docx. submit by 8pm.

```
pytest
python -m src.main
python -m src.build_report
```

## fri 23 - polish after feedback

moved all source into src/, tests into tests/. root keeps only config, data, docs,
reports and the notebook.

renamed df1/df2/df3: df_raw -> df_cleaned -> df_enriched, and each cleaning helper
names its own copy (df_dropped, df_collection_named, df_flattened, df_typed,
df_sane, df_released, df_ordered). the steps read like the pipeline now.

added the eda section: describe() on the numeric columns, 5 histograms, 3 boxplots,
and markdown saying what they show. the report got section 7 with charts 6-8.

rebuilt the docx from the backup json and refreshed the pdf through word. pytest 31
green, notebook runs 1-11 offline. review pass fixed clipped genre labels, the
rankings table cells, a duplicate paragraph, and the boxplot call that only worked
on matplotlib 3.9.

docs updated: readme, study notes, pipeline walkthrough, code review, this timeline.
