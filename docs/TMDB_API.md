# tmdb api notes

source: https://developer.themoviedb.org/docs/getting-started

## key

1. make account on themoviedb.org
2. settings -> api, copy v3 key
3. copy .env.example to .env and paste key
4. never commit .env

## calls I use

```
GET /movie/{id}?api_key=KEY
GET /movie/{id}/credits?api_key=KEY
```

{id} is like 597. lab has 19 ids, 0 is bad and gives 404 so I skip it. 18 left.

limit is about 40 per sec. I sleep 0.25s between calls.

## one movie looks like

- budget, revenue in dollars, 0 means unknown
- runtime in min, 0 means unknown
- status is Released for all 18 here
- belongs_to_collection is dict with name or null
- genres is list like [{"name": "Action"}] -> I make "Action|Comedy"
- spoken_languages uses english_name
- production_companies and countries use name
- adult, imdb_id, original_title, video, homepage -> I drop these

## credits looks like

cast is [{"name": "..."}] and crew has {"job": "Director"}.
I keep cast names, cast_size, director, crew_size.

## errors

200 ok. 404 skip (id 0). 401 means bad key. 429 too fast, wait and retry once.
no internet or no key -> use data/tmdb_backup.json. live returns 0 rows -> same.
