# what I learned for this lab

my own notes. read this if you want to redo the lab alone.

## 1. python I actually used

- for loop over a list. I use it everywhere to go through rows or names.
- if and in. like `if "Action" in g` to test text.
- dict .get. `credits.get("cast", [])` gives [] if missing, no crash.
- isinstance(x, dict) and isinstance(x, list). json from api mixes dicts, lists and null, so I check type first.
- open and json.load. backup file is just a list of dicts.
- os.getenv. reads key from .env so key is not in code.
- def with copy. I always do df2 = df.copy() then change df2, so old df stays.

I did not use list comp or lambda. a plain for loop is slower but I can explain it.

## 2. requests

- requests.get(url, params={"api_key": key}, timeout=20)
- r.status_code is 200 ok, 404 not found, 401 bad key, 429 too fast.
- r.json() turns web answer to dict.
- time.sleep(0.25) so I do not hit the limit.

try it: fetch id 597, print title, budget. fetch id 0, see 404 and skip.

## 3. pandas basics

- pd.DataFrame(records) makes table from list of dicts.
- df.copy, df.head, df.shape, df.columns.
- df[col] picks a column. df[mask] keeps rows where mask is True.
- del df2[col] drops a column. simple to explain.
- pd.to_numeric(col, errors="coerce"). bad text -> NaN.
- pd.to_datetime(col, errors="coerce"). bad date -> NaT.
- col.replace(0, float("nan")). 0 here means unknown, not zero.
- col / 1000000. dollars to millions.
- df[cond]. sort with sort_values(by="x", ascending=False). head(5) takes top 5.
- drop_duplicates(subset=["id", "title"]). I use subset because cast col is a list and full dup check crashes.
- dropna(subset=["id", "title"]) drops rows with no id. dropna(thresh=10) keeps rows with 10+ values.
- df[col].value_counts(dropna=False) to see what values turned up in a column I built. I run it on the joined columns before I trust them, otherwise a typo like "Sci Fi" just sits there.
- groupby("group").mean() and .sum(), .size() for counts.
- pd.isna(v) and pd.notna(v) to test empty. `v == v` is False for NaN but isna is clearer.
- str(row["genres"]) turns list or NaN to text so `in` works and never crashes.

practice: load backup json, print titles, check dtypes, try sort by revenue.

## 4. cleaning steps in order

1. drop adult, imdb_id, original_title, video, homepage.
2. collection dict -> name text. None stays empty.
3. genres, spoken_languages, companies, countries, cast lists -> "A|B" text. I loop items, pick key, join with + "|" +.
4. numbers and dates with to_numeric / to_datetime.
5. 0 to NaN for budget, revenue, runtime. new budget_musd, revenue_musd. vote_average to NaN where vote_count == 0. "No Data" and "" to NaN.
   the vote_average one uses df.loc[mask, col] = nan, not df["col"].iloc[i] = nan. chained
   assignment is dropped by pandas 3 and it fails silently, the value just stays.
6. keep status == "Released", then delete status col. drop dupes, drop no id/title, thresh 10.
7. keep FINAL_COLUMNS order, reset_index.

final check: list(df.columns) == FINAL_COLUMNS and len 18.

## 5. kpi steps

- profit = revenue_musd - budget_musd. roi = revenue_musd / budget_musd.
- roi only if budget >= 10. rating only if votes >= 10. these are lab rules.
- rank(col) = sort + head. ascending True means smallest first.
- 10 ranks: revenue, budget, profit high/low, roi high/low with filter, votes, rating high/low with filter, popularity.
- search: loop rows with iloc, test with `in`, collect True/False list, filter, sort. willis sorts by vote_average desc, thurman by runtime asc. here both are 0, that is fine, I say so in report.
- franchise: new col group = "franchise" if collection not empty else "standalone". groupby. revenue, budget, popularity and rating use mean, roi uses median because one big film moves the mean and not the median.
- top franchises / directors: get unique names with a loop, for each name filter table, use len, sum, mean, put in list of dicts, make DataFrame, sort by total_revenue desc.

## 6. plots

same each time:

```
fig, ax = plt.subplots()
ax.scatter(x, y) or ax.bar(labels, vals) or ax.plot(years, vals)
ax.set_xlabel, ax.set_ylabel, ax.set_title
return ax
```

- revenue vs budget: scatter budget_musd x, revenue_musd y.
- roi by genre: split genres by "|", mean roi per genre, bar. I loop, no explode.
- popularity vs rating: scatter.
- yearly: year = pd.to_datetime(release_date).dt.year, mean per year, plot line.
- franchise vs single: mean revenue per group, bar.

notebook shows with plt.show(). report saves with plt.savefig then add_picture.

## 7. tests and git

- pytest runs files starting with test_. my tests use tiny DataFrames or fake movie records so they run offline.
- data/tmdb_backup.json is gitignored, so a test that opens it fails on a fresh clone. tests/helpers.py
  load_records() uses the real backup if it is there and fake_movies() if not. fake_df() is always fake,
  done_df() is real-or-fake. use fake_df() when the test checks a number.
- python app/main.py prints got 18 movies and clean shape.
- git add, git commit -m "short msg", git log --oneline to see week. git status must not show .env.

if stuck 30 min, reread the one function and try it on 2 rows in notebook.
