# Daily brief process

Standing procedure for producing each day's dashboard brief. Follow this for every `days/<YYYY-MM-DD>.json`.

Date in steps below = the brief's date (today, unless backfilling).

## 1. Pull news

Scan the canonical sources listed in the prior day-file's `live_sources` for items dated since the last brief:

- City of Toledo news, The Blade (business + city), WTOL, 13abc
- Downtown Toledo Inc., Toledo City Paper (business)
- Regional Growth Partnership / toledobiz
- Vibrancy hub, RAISE / Uptown-Junction
- Warehouse District Assoc., Ostrich Towne, Watershed Weekend
- Plus any district / project sites a current story points to

For every candidate item, capture: headline, source URL(s), source date, district/topic, key people.

## 2. Triage against existing stories

For each item, classify against `dashboard/stories/` (28+ files):

- **NEW** — no existing story file matches → create `dashboard/stories/<kebab-id>.json`.
- **UPDATE** — matches an existing story → modify the existing file:
  - `last_updated` = today
  - `date_label` = `"Updated <Month D, YYYY>"`
  - `date_age_class` = `"age-new"`
  - Revise `paragraphs` / `why_it_matters` to fold in the new chapter (don't just append — rewrite tight)
  - Append new `sources`
  - Add one entry to `STORY_CHAINS[<id>]` in `dashboard/index.html` (`{ date, headline, snippet }`, most-recent-first), and set `isFreshChapter: true`
- **ONGOING** — no new chapter today → keep in `ongoing_story_ids`, don't touch the file.

Story JSON schema (see `extract_today.py` for the canonical field list):
`id, headline, section, tags, posted_date, source_date, last_updated, date_label, date_age_class, paragraphs, why_it_matters, people, sources, locations, external_map_link, related_story_ids, search_terms`.

## 3. Pick the top story

One story leads the brief. Top story is what a regional EDO leader would open with — biggest signal, broadest implication.

## 4. Build the day-file

Write `dashboard/days/<date>.json` with:

- `date`, `title`, `window` ("Rolling 48-hour focus"), `auto_refresh` ("Daily 5:00 AM")
- `top_story_id`
- `sections` (recency-based, in this order; the convention set in commit dba9fd1):
  1. `""` (untitled) — `[top_story_id]` only
  2. `"New stories"` — every NEW item
  3. `"Updates this brief"` — every UPDATE
  4. `"Ongoing"` — items being tracked but with no new chapter today
- `ongoing_story_ids` (flat list, drives the "ongoing" badge regardless of section)
- `watch_list` — what to watch in the next report (carry forward + edit; remove resolved items)
- `live_sources` — carry forward; add/remove as the coverage map changes

## 5. Render the markdown archive

```bash
python3 dashboard/scripts/render_brief.py <date>
```

Writes `dashboard/archive/<date>_toledo_development_brief.md`.

## 6. Deploy

```bash
dashboard/deploy.sh
```

Validates every JSON under `dashboard/` (aborts on parse error), stages `dashboard/`, commits with `Dashboard daily update: <date>` (or a passed-in subject), pushes to origin. Pages serves the result at `/dashboard/`.

## Multiple passes per day

It is normal to ship several commits in a day as new material lands ("expanded", "+ Foundation Steel", "regional EDO leadership stories", etc.). Each pass repeats steps 1–6 against the live day-file; the deploy script is idempotent.
