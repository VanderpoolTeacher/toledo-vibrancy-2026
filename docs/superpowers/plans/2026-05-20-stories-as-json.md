# Stories-as-JSON Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the dashboard data model: every story becomes a per-file JSON record in `dashboard/stories/`, every day becomes a per-file editorial index in `dashboard/days/`, and `dashboard/index.html` becomes a thin shell that fetches and renders.

**Architecture:** JSON is the source of truth. The daily 5 AM task writes JSON; the dashboard renders from JSON; markdown briefs are auto-generated from JSON. Cutover is done by building the new shell alongside the live one (`index.new.html`) and swapping atomically at the end so the live site never breaks mid-implementation.

**Tech Stack:** Python 3 + `beautifulsoup4` (one-time HTML→JSON extraction and markdown renderer), vanilla JavaScript, Leaflet 1.9.4. No build step, no framework, no automated tests (per project pattern — manual browser verification).

**Source spec:** `docs/superpowers/specs/2026-05-20-stories-as-json-design.md` (latest revision at commit `4ddb898` adds `locations[]` + `external_map_link`).

**Project conventions:**
- Single static HTML file pattern, no build pipeline.
- Small commits to `main` directly (no feature branches).
- Manual browser testing only.
- Daily 5 AM scheduled task may add commits while you work — handle by rebase on push if needed.

---

## File Structure

**Create:**
- `dashboard/scripts/extract_today.py` — one-time bootstrap script (HTML → JSON corpus).
- `dashboard/scripts/render_brief.py` — day-file + stories → markdown brief.
- `dashboard/stories/<id>.json` — canonical story file (one per story; ~16 written by extraction).
- `dashboard/days/2026-05-20.json` — today's editorial index.
- `dashboard/index.new.html` — staging file for the new shell during development; renamed to `index.html` at cutover.

**Modify:**
- `dashboard/index.html` — replaced at cutover with the contents of `index.new.html`. Old per-story HTML and `STORY_LOCATIONS` JS object are gone.
- `dashboard/deploy.sh` — add `jq empty` pre-commit JSON validation.
- `dashboard/archive/2026-05-20_toledo_development_brief.md` — regenerated from JSON via `render_brief.py`.

**Untouched:**
- `dashboard/followed_stories.json` — follow-list semantics unchanged.
- `dashboard/coords-source.md` — coordinate audit trail; carries over.
- `dashboard/archive/2026-05-19_toledo_development_brief.md` — pre-cutover record; left as-is (no retroactive backfill per spec).
- All existing CSS rules inside `dashboard/index.html` — preserved verbatim during the rewrite.

---

## Task 1: Add scripts/extract_today.py (one-time HTML→JSON extractor)

**Files:**
- Create: `dashboard/scripts/extract_today.py`

**Goal:** Build the one-time bootstrap script. Don't run it yet — Task 2 runs it and commits outputs.

- [ ] **Step 1.1: Verify Python 3 and beautifulsoup4 are available.**

```bash
python3 --version
python3 -c "import bs4; print(bs4.__version__)" 2>&1 | head -1
```

If `bs4` is missing, install with `python3 -m pip install --user beautifulsoup4`. The script is one-time; don't pollute project dependencies with a requirements file.

- [ ] **Step 1.2: Create the scripts directory.**

```bash
mkdir -p dashboard/scripts
```

- [ ] **Step 1.3: Write `dashboard/scripts/extract_today.py`.** Full contents:

```python
#!/usr/bin/env python3
"""One-time bootstrap: parse dashboard/index.html into:
  - dashboard/stories/<id>.json (one per story)
  - dashboard/days/<TODAY>.json (today's editorial index)

This script runs ONCE during the stories-as-JSON cutover. After cutover,
the daily 5 AM scheduled task writes JSON directly; this script becomes
historical reference.

Usage:
  python3 dashboard/scripts/extract_today.py
"""
import json
import re
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.stderr.write("Missing dependency: pip install --user beautifulsoup4\n")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent  # dashboard/
INDEX = ROOT / "index.html"
STORIES_DIR = ROOT / "stories"
DAYS_DIR = ROOT / "days"

# The cutover date. Every extracted story gets posted_date = TODAY. We don't
# pretend to know each story's true historical posting date — that information
# was not captured before the refactor.
TODAY = "2026-05-20"

# STORY_LOCATIONS extracted from the existing dashboard/index.html inline JS.
# Coordinates verified during the story-maps feature (dashboard/coords-source.md).
# This dict mirrors the JS object exactly so the extraction is faithful.
# Stories not in this dict get `locations: []` (no map data).
STORY_LOCATIONS = {
    "vibrancy-19-grants": {
        "external_map_link": {
            "href": "../index.html",
            "label": "View all 17 properties on the Vibrancy map",
        }
    },
    "huron-yards-phase-two": {
        "locations": [
            {"shape": "point", "label": "28 N. Erie St", "match": "28 N. Erie St.",
             "lat": 41.6492, "lon": -83.5407}
        ]
    },
    "port-warehouse-liquid-terminal": {
        "locations": [
            {"shape": "point", "label": "Toledo-Lucas County Port Authority", "match": None,
             "lat": 41.6538, "lon": -83.5283}
        ]
    },
    "ostrich-towne-tenants": {
        "locations": [
            {"shape": "point", "label": "Ostrich Towne (Vistula)", "match": "Ostrich Towne",
             "lat": 41.6509, "lon": -83.5367}
        ]
    },
    "vistula-metropark": {
        "locations": [
            {"shape": "line", "label": "Water St (Olive to Magnolia)",
             "match": "Water Street between Olive and Magnolia",
             "path": [[41.6535, -83.5293], [41.6572, -83.5237]]}
        ]
    },
    "soccer-stadium-vistula": {
        "locations": [
            {"shape": "point", "label": "Proposed stadium — Vistula riverfront",
             "match": "directly across the river from Glass City Metropark",
             "lat": 41.6539, "lon": -83.5215}
        ]
    },
    "raise-uptown-junction": {
        "locations": [
            {"shape": "polygon", "label": "RAISE area — 13th–21st St × Adams–Monroe",
             "match": "13th–21st Street, Adams to Monroe",
             "bbox": [[41.6537, -83.5520], [41.6580, -83.5610]]}
        ]
    },
    "owens-corning-250m": {
        "locations": [
            {"shape": "point", "label": "Owens Corning HQ", "match": None,
             "lat": 41.6476, "lon": -83.5350}
        ]
    },
    "connectoledo-music-grant": {
        "locations": [
            {"shape": "point", "label": "Promenade Park",       "match": "Promenade Park",
             "lat": 41.6503, "lon": -83.5333},
            {"shape": "point", "label": "Glass City Metropark", "match": "Glass City Metropark",
             "lat": 41.6547, "lon": -83.5168},
            {"shape": "point", "label": "Junction Park",        "match": "Junction Park",
             "lat": 41.6411, "lon": -83.5611},
            {"shape": "point", "label": "Danny Thomas Park",    "match": "Danny Thomas Park",
             "lat": 41.6254, "lon": -83.5650},
        ]
    },
    "mind-and-soul-gallery": {
        "locations": [
            {"shape": "point", "label": "Gardner Building (506 Madison Ave)",
             "match": "Gardner Building",
             "lat": 41.6522, "lon": -83.5359}
        ]
    },
}


def parse_people(raw: str):
    """data-people='Name|Role|Search Terms;Name2|Role2|Terms2' → [{name,role,search_terms}, ...]"""
    out = []
    for entry in (raw or "").split(";"):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split("|")
        name = parts[0].strip() if parts else ""
        if not name:
            continue
        role = parts[1].strip() if len(parts) > 1 else ""
        terms = parts[2].strip() if len(parts) > 2 else name
        out.append({"name": name, "role": role, "search_terms": terms})
    return out


def extract_story(el, section_title):
    """Read one .story-item div and return a story dict matching the spec schema."""
    classes = el.get("class", [])
    sid = el.get("data-story-id", "")
    tags = (el.get("data-tags") or "").split()
    search_terms = el.get("data-search-terms") or ""
    source_date = el.get("data-source-date") or ""

    headline_el = el.find(["h2", "h3"])
    headline = headline_el.get_text(strip=True) if headline_el else ""

    # Story paragraphs are top-level <p> children of the story div, EXCLUDING:
    #   - paragraphs inside .why (handled separately)
    paragraphs = []
    for p in el.find_all("p", recursive=True):
        # Skip <p> nested inside .why
        if p.find_parent(class_="why") is not None:
            continue
        text = p.get_text(" ", strip=True)
        if text:
            paragraphs.append(text)

    # "Why it matters" — strip the leading "Why it matters:" prefix
    why_el = el.find(class_="why")
    why_it_matters = ""
    if why_el:
        # Make a working copy text without the bold "Why it matters:" label
        strong = why_el.find("strong")
        if strong:
            strong.extract()
        text = why_el.get_text(" ", strip=True).lstrip(":").strip()
        why_it_matters = text

    sources = [
        {"title": a.get_text(strip=True), "url": a.get("href", "")}
        for a in el.select(".sources-inline a")
        if a.get("href")
    ]

    people = parse_people(el.get("data-people", ""))

    # Pull location + external_map_link from the embedded dict
    loc_entry = STORY_LOCATIONS.get(sid, {})
    locations = loc_entry.get("locations", [])
    external_map_link = loc_entry.get("external_map_link")

    return {
        "id": sid,
        "headline": headline,
        "section": section_title or "",
        "tags": tags,
        "posted_date": TODAY,
        "source_date": source_date,
        "last_updated": TODAY,
        "paragraphs": paragraphs,
        "why_it_matters": why_it_matters,
        "people": people,
        "sources": sources,
        "locations": locations,
        "external_map_link": external_map_link,
        "related_story_ids": [],
        "search_terms": search_terms,
    }, ("top-story" in classes, "is-ongoing" in classes)


def main():
    html = INDEX.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    wrap = soup.find(class_="wrap")
    if not wrap:
        sys.exit("Couldn't find .wrap container in dashboard/index.html")

    STORIES_DIR.mkdir(exist_ok=True)
    DAYS_DIR.mkdir(exist_ok=True)

    stories = []                    # list of story dicts
    sections = []                   # list of {title, story_ids}
    current_section_title = None
    top_story_id = None
    ongoing_story_ids = []

    # Walk direct children of .wrap in order. Section titles set the current
    # section; story items append to the most recent section.
    for child in wrap.find_all(recursive=False):
        cls = child.get("class") or []
        if "section-title" in cls:
            title = child.get_text(strip=True)
            current_section_title = title
            sections.append({"title": title, "story_ids": []})
        elif "story-item" in cls:
            # Top story doesn't sit inside a section-title in the source HTML;
            # treat it as belonging to whatever section is set (or "Top" if none).
            section_title = current_section_title or ""
            story, (is_top, is_ongoing) = extract_story(child, section_title)
            stories.append(story)
            if is_top:
                top_story_id = story["id"]
            if is_ongoing:
                ongoing_story_ids.append(story["id"])
            if sections:
                sections[-1]["story_ids"].append(story["id"])
            # If there's no current section (e.g., the top story appearing before
            # the first .section-title), put it in a synthesized top-level slot.
            else:
                sections.append({"title": "", "story_ids": [story["id"]]})

    # Watch-list and live-sources (move from HTML into day-file)
    watch_list = [li.get_text(" ", strip=True) for li in wrap.select(".watch-list ol > li")]
    live_sources = [
        {"title": a.get_text(strip=True), "url": a.get("href", "")}
        for a in wrap.select(".live-sources .grid > a")
        if a.get("href")
    ]

    # Strip empty section buckets (e.g., a synthesized top-only slot that ended up empty)
    sections = [s for s in sections if s["story_ids"]]

    # Write story files
    for story in stories:
        path = STORIES_DIR / f"{story['id']}.json"
        path.write_text(json.dumps(story, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")

    # Build and write day-file
    day = {
        "date": TODAY,
        "title": "Toledo Economic Development Dashboard",
        "window": "Rolling 48-hour focus",
        "auto_refresh": "Daily 5:00 AM",
        "top_story_id": top_story_id,
        "sections": sections,
        "ongoing_story_ids": ongoing_story_ids,
        "watch_list": watch_list,
        "live_sources": live_sources,
    }
    (DAYS_DIR / f"{TODAY}.json").write_text(
        json.dumps(day, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"Wrote {len(stories)} stories → {STORIES_DIR}")
    print(f"Wrote 1 day-file → {DAYS_DIR / (TODAY + '.json')}")
    print(f"Top story: {top_story_id}")
    print(f"Ongoing ({len(ongoing_story_ids)}): {', '.join(ongoing_story_ids)}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 1.4: Static syntax check.**

```bash
python3 -m py_compile dashboard/scripts/extract_today.py
```

Expected: exit 0, no output. If you see SyntaxError, fix it before continuing.

- [ ] **Step 1.5: Commit.**

```bash
git add dashboard/scripts/extract_today.py
git commit -m "Add extract_today.py: one-time HTML to JSON bootstrap"
```

---

## Task 2: Run extraction; commit JSON outputs

**Files:**
- Create: `dashboard/stories/<id>.json` (one per story)
- Create: `dashboard/days/2026-05-20.json`

**Goal:** Run the extractor and commit the JSON corpus. Live site is unaffected (it still reads from the unchanged `dashboard/index.html`).

- [ ] **Step 2.1: Run the script from the repo root.**

```bash
cd /Users/michaelvanderpool/Documents/GitHub/Toledo
python3 dashboard/scripts/extract_today.py
```

Expected output, roughly:
```
Wrote 16 stories → /Users/michaelvanderpool/Documents/GitHub/Toledo/dashboard/stories
Wrote 1 day-file → /Users/michaelvanderpool/Documents/GitHub/Toledo/dashboard/days/2026-05-20.json
Top story: watershed-weekend-riverwalk
Ongoing (11): huron-yards-phase-two, port-warehouse-liquid-terminal, ...
```

The exact story count depends on the live state of `dashboard/index.html` at extraction time (the daily 5 AM task may have added/removed stories). 14–18 stories is the expected range.

- [ ] **Step 2.2: Spot-check a single-point story.**

```bash
cat dashboard/stories/huron-yards-phase-two.json
```

Expected: well-formed JSON with `posted_date: "2026-05-20"`, `last_updated: "2026-05-20"`, `source_date: ""` or a date string, `paragraphs: [...]` non-empty, `why_it_matters: "..."` non-empty starting with "A grocery store" or similar (NOT starting with "Why it matters:"), `locations: [{shape: "point", label: "28 N. Erie St", match: "28 N. Erie St.", lat: 41.6492, lon: -83.5407}]`, `external_map_link: null`.

- [ ] **Step 2.3: Spot-check the multi-point story (ConnecToledo).**

```bash
cat dashboard/stories/connectoledo-music-grant.json | python3 -m json.tool | head -40
```

Expected: `locations` is an array with exactly 4 entries, each with `shape: "point"` and a distinct `label` (Promenade Park, Glass City Metropark, Junction Park, Danny Thomas Park).

- [ ] **Step 2.4: Spot-check the external-map story (vibrancy-19-grants).**

```bash
cat dashboard/stories/vibrancy-19-grants.json
```

Expected: `locations: []`, `external_map_link: { href: "../index.html", label: "View all 17 properties on the Vibrancy map" }`.

- [ ] **Step 2.5: Spot-check the day-file.**

```bash
cat dashboard/days/2026-05-20.json | python3 -m json.tool | head -30
```

Expected: `date: "2026-05-20"`, `top_story_id` is the current top story ID (e.g., `watershed-weekend-riverwalk`), `sections` is an array of `{title, story_ids}`, `ongoing_story_ids` is non-empty, `watch_list` has ~5 entries, `live_sources` has 12 entries.

- [ ] **Step 2.6: Validate all generated JSON parses.**

```bash
for f in dashboard/stories/*.json dashboard/days/*.json; do
  python3 -c "import json,sys; json.load(open('$f'))" || echo "BAD: $f"
done
```

Expected: no "BAD" lines printed.

- [ ] **Step 2.7: Commit.**

```bash
git add dashboard/stories/ dashboard/days/
git commit -m "Bootstrap stories/ and days/ JSON corpus from current dashboard"
```

---

## Task 3: Add scripts/render_brief.py (markdown renderer)

**Files:**
- Create: `dashboard/scripts/render_brief.py`

**Goal:** Build the renderer that turns a day-file + its referenced stories into the markdown brief format. Don't run it yet — Task 4 runs and commits.

- [ ] **Step 3.1: Write `dashboard/scripts/render_brief.py`.** Full contents:

```python
#!/usr/bin/env python3
"""Render a markdown brief from a day-file + its referenced story JSON files.

Usage:
  python3 dashboard/scripts/render_brief.py 2026-05-20

Writes:
  dashboard/archive/<DATE>_toledo_development_brief.md

Reads:
  dashboard/days/<DATE>.json
  dashboard/stories/<id>.json (for every story_id in the day-file)
"""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # dashboard/
STORIES_DIR = ROOT / "stories"
DAYS_DIR = ROOT / "days"
ARCHIVE_DIR = ROOT / "archive"


def load_story(sid):
    path = STORIES_DIR / f"{sid}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def format_date_long(iso: str) -> str:
    """'2026-05-20' → 'May 20, 2026'."""
    try:
        y, m, d = map(int, iso.split("-"))
        return date(y, m, d).strftime("%B %-d, %Y")
    except Exception:
        return iso


def render_sources_inline(sources):
    """Render a flat 'Sources: [Foo](url) · [Bar](url)' line. Returns empty string if no sources."""
    if not sources:
        return ""
    parts = [f"[{s['title']}]({s['url']})" for s in sources if s.get("url")]
    if not parts:
        return ""
    return "**Sources:** " + " · ".join(parts)


def render_story_block(story, is_top=False):
    """Render one story as a markdown block."""
    out = []
    heading_level = "##" if is_top else "###"
    out.append(f"{heading_level} {story['headline']}")
    if story.get("source_date"):
        out.append(f"_Source: {story['source_date']}_")
    out.append("")
    for p in story.get("paragraphs", []):
        out.append(p)
        out.append("")
    if story.get("why_it_matters"):
        out.append(f"**Why it matters:** {story['why_it_matters']}")
        out.append("")
    src_line = render_sources_inline(story.get("sources", []))
    if src_line:
        out.append(src_line)
        out.append("")
    return "\n".join(out).rstrip() + "\n\n"


def render_brief(date_str):
    day_path = DAYS_DIR / f"{date_str}.json"
    if not day_path.exists():
        sys.exit(f"day-file not found: {day_path}")
    day = json.loads(day_path.read_text(encoding="utf-8"))

    out = []
    out.append(f"# Toledo Economic Development Brief — {format_date_long(date_str)}")
    out.append("")
    out.append(f"**Window covered:** {day.get('window', 'Rolling 48-hour focus')}.  ")
    coverage = []
    for s in day.get("sections", []):
        if s.get("title"):
            coverage.append(s["title"])
    if coverage:
        out.append("**Coverage areas:** " + " · ".join(coverage))
    out.append("")
    out.append("---")
    out.append("")

    # Top story
    top_id = day.get("top_story_id")
    if top_id:
        top = load_story(top_id)
        if top:
            out.append(f"## Top story: {top['headline']}")
            out.append("")
            for p in top.get("paragraphs", []):
                out.append(p)
                out.append("")
            if top.get("why_it_matters"):
                out.append(f"**Why it matters:** {top['why_it_matters']}")
                out.append("")
            src_line = render_sources_inline(top.get("sources", []))
            if src_line:
                out.append(src_line)
                out.append("")
            out.append("---")
            out.append("")

    # Sections — render each, skipping the top story when it appears inside
    for section in day.get("sections", []):
        title = section.get("title")
        if title:
            out.append(f"## {title}")
            out.append("")
        for sid in section.get("story_ids", []):
            if sid == top_id:
                continue  # already rendered above
            story = load_story(sid)
            if not story:
                out.append(f"_(missing story: {sid})_\n\n")
                continue
            out.append(render_story_block(story))
        out.append("---")
        out.append("")

    # Watch list
    if day.get("watch_list"):
        out.append("## What to watch in the next report")
        out.append("")
        for i, item in enumerate(day["watch_list"], 1):
            out.append(f"{i}. {item}")
        out.append("")
        out.append("---")
        out.append("")

    # Sources index — flat list of every source URL referenced across stories
    seen = set()
    all_sources = []
    for sid in {sid for sec in day.get("sections", []) for sid in sec.get("story_ids", [])}:
        story = load_story(sid)
        if not story:
            continue
        for src in story.get("sources", []):
            key = src.get("url", "")
            if key and key not in seen:
                seen.add(key)
                all_sources.append(src)
    if all_sources:
        out.append("## Sources")
        out.append("")
        for s in all_sources:
            out.append(f"- [{s['title']}]({s['url']})")
        out.append("")

    return "\n".join(out)


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: render_brief.py <YYYY-MM-DD>")
    date_str = sys.argv[1]
    md = render_brief(date_str)
    ARCHIVE_DIR.mkdir(exist_ok=True)
    out_path = ARCHIVE_DIR / f"{date_str}_toledo_development_brief.md"
    out_path.write_text(md, encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3.2: Static syntax check.**

```bash
python3 -m py_compile dashboard/scripts/render_brief.py
```

Expected: exit 0, no output.

- [ ] **Step 3.3: Commit.**

```bash
git add dashboard/scripts/render_brief.py
git commit -m "Add render_brief.py: day-file + stories to markdown"
```

---

## Task 4: Regenerate May 20 markdown brief from JSON

**Files:**
- Modify: `dashboard/archive/2026-05-20_toledo_development_brief.md`

**Goal:** Produce the markdown brief from the JSON corpus, replacing the daily-task's hand-written version. Verify structural equivalence with the existing brief.

- [ ] **Step 4.1: Back up the existing brief for diff comparison.**

```bash
cp dashboard/archive/2026-05-20_toledo_development_brief.md /tmp/brief-before.md
```

- [ ] **Step 4.2: Run the renderer.**

```bash
python3 dashboard/scripts/render_brief.py 2026-05-20
```

Expected output:
```
Wrote /Users/michaelvanderpool/Documents/GitHub/Toledo/dashboard/archive/2026-05-20_toledo_development_brief.md
```

- [ ] **Step 4.3: Eyeball the diff.**

```bash
diff /tmp/brief-before.md dashboard/archive/2026-05-20_toledo_development_brief.md | head -100
```

The new brief will not be byte-identical (the daily task writes more flowing prose intros than a mechanical renderer). What you SHOULD see:
- Same headline (`# Toledo Economic Development Brief — May 20, 2026`).
- Same top story headline.
- Same set of section headers.
- Same set of story headlines under each section.
- Source links largely preserved.

What's acceptable:
- Different intro phrasing (the prose intros were hand-written; the renderer is mechanical).
- Different ordering inside a section if the renderer differs from the original — but the renderer respects `day.sections[].story_ids` ordering, which mirrors the original.

If you see whole sections missing or stories dropped, something is wrong with the renderer; debug and re-run before committing.

- [ ] **Step 4.4: Commit.**

```bash
git add dashboard/archive/2026-05-20_toledo_development_brief.md
git commit -m "Regenerate May 20 brief from JSON via render_brief.py"
```

---

## Task 5: Add new dashboard shell as index.new.html (structure + render skeleton)

**Files:**
- Create: `dashboard/index.new.html`

**Goal:** Build the new dashboard shell as a sibling file so the live `dashboard/index.html` keeps working through subsequent tasks. This task lays down the static structure; tasks 6–11 fill in render logic.

- [ ] **Step 5.1: Create `dashboard/index.new.html` by copying the existing dashboard.**

```bash
cp dashboard/index.html dashboard/index.new.html
```

This gives us the same `<head>` (with Leaflet links from the story-maps task), the same CSS, and a starting point for the body rewrite.

- [ ] **Step 5.2: Replace the body content in `dashboard/index.new.html`.**

Open `dashboard/index.new.html`. Find the line `<body>` and the line `</body>`. REPLACE everything between them (exclusive of those two tags) with:

```html
<div class="wrap">

<header>
  <h1>Toledo Economic Development Dashboard</h1>
  <p class="subtitle">Business development · Grants · Downtown · Warehouse District · Vistula/Ostrich Towne · Uptown · Junction</p>
  <div class="meta">
    <span><strong>Last refreshed:</strong> <span id="meta-date">—</span></span>
    <span><strong>Window:</strong> <span id="meta-window">—</span></span>
    <span><strong>Auto-refresh:</strong> <span id="meta-auto-refresh">—</span></span>
    <span id="env-badge" class="badge badge-info">Live site</span>
  </div>
</header>

<div class="banner" id="env-banner">
  Author's followed items are loaded from <code>followed_stories.json</code> and marked with a ★ badge. You can also follow items locally in your browser — those follows stay on this device.
</div>

<div class="follow-panel">
  <h2>★ Following <span class="count" id="follow-count-total">0</span></h2>
  <p class="follow-empty" id="follow-empty">No follows yet. Tap <kbd>★ Follow</kbd> on a story, or click a person chip, to track items locally in your browser.</p>
  <div id="follow-stories-wrap" style="display:none;">
    <div class="follow-subhead">Stories <span class="count" id="follow-count-stories">0</span></div>
    <ul class="follow-list" id="follow-list-stories"></ul>
  </div>
  <div id="follow-people-wrap" style="display:none;">
    <div class="follow-subhead">People <span class="count" id="follow-count-people">0</span></div>
    <ul class="follow-list" id="follow-list-people"></ul>
  </div>
</div>

<div class="past-briefs" id="past-briefs"></div>

<div class="filters" id="filters">
  <button class="filter-btn active" data-filter="all">All</button>
  <button class="filter-btn" data-filter="followed">★ Followed only</button>
  <button class="filter-btn" data-filter="grants">Grants</button>
  <button class="filter-btn" data-filter="downtown">Downtown</button>
  <button class="filter-btn" data-filter="warehouse">Warehouse Dist</button>
  <button class="filter-btn" data-filter="vistula">Vistula / Ostrich Towne</button>
  <button class="filter-btn" data-filter="uptown">Uptown</button>
  <button class="filter-btn" data-filter="junction">Junction</button>
  <button class="filter-btn" data-filter="citywide">Citywide</button>
</div>

<div id="loading-banner" class="banner" style="text-align:center;">Loading stories…</div>
<div id="error-banner" class="banner" style="display:none; background:#fdecea; border-color:#f5c2c0; color:#8c1a1a;"></div>

<main id="stories"></main>

<div class="watch-list" id="watch-list" style="display:none;">
  <h3>What to watch in the next report</h3>
  <ol id="watch-list-items"></ol>
</div>

<div class="live-sources" id="live-sources" style="display:none;">
  <h3>Live source pages (always current)</h3>
  <div class="grid" id="live-sources-grid"></div>
  <a class="archive-link" href="archive/">→ Browse daily markdown archive</a>
</div>

<div class="footer-note">
  Refreshed automatically each morning at 5:00 AM ET. Markdown archives committed daily. <a href="archive/">View daily briefs</a> · <a href="../">View the 2026 Vibrancy Initiative grant map →</a>
</div>

</div>

<script>
(function(){
  'use strict';

  // -- Storage / config (unchanged from previous dashboard) --
  const STORAGE_KEY = 'toledo_dashboard_follows_v2';
  const FILTER_KEY = 'toledo_dashboard_filter';
  const REPO_FOLLOW_FILE = 'followed_stories.json';

  // -- Date routing --
  function targetDate() {
    const url = new URL(window.location.href);
    const param = url.searchParams.get('date');
    if (param && /^\d{4}-\d{2}-\d{2}$/.test(param)) return param;
    // Default = today in local TZ, YYYY-MM-DD
    const d = new Date();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${d.getFullYear()}-${m}-${day}`;
  }

  // Task 6 fills in the rest of the render pipeline.
  console.log('Stories-as-JSON shell loaded, target date:', targetDate());
})();
</script>
</body>
```

Make sure you DELETE everything that was previously between `<body>` and `</body>` — including all the inline story HTML, the `STORY_LOCATIONS` constant, every existing IIFE function, etc. The body you keep is exactly what's shown above.

- [ ] **Step 5.3: Open the file in a browser and confirm.**

```bash
open dashboard/index.new.html
```

Expected: the page loads with header, banner, follow panel, filter pills, "Loading stories…", and the footer note. No stories yet. The "★ Following" panel says "0". Open devtools console — should see `Stories-as-JSON shell loaded, target date: 2026-05-20` (or today's date).

- [ ] **Step 5.4: Commit.**

```bash
git add dashboard/index.new.html
git commit -m "Add new dashboard shell at index.new.html (structure + skeleton)"
```

---

## Task 6: Render JS — fetch day-file, then fetch stories in parallel

**Files:**
- Modify: `dashboard/index.new.html`

**Goal:** Replace the placeholder IIFE in `index.new.html` with a real load pipeline that fetches the day-file and all referenced stories. Cards aren't rendered yet — Task 7 adds that.

- [ ] **Step 6.1: Find the current `<script>` block in `dashboard/index.new.html`.** It currently contains only the `STORAGE_KEY`, `FILTER_KEY`, `REPO_FOLLOW_FILE`, `targetDate()`, and a console.log line.

REPLACE the entire IIFE body (between `(function(){` and `})();`) with:

```js
'use strict';

// -- Storage / config (unchanged from previous dashboard) --
const STORAGE_KEY = 'toledo_dashboard_follows_v2';
const FILTER_KEY = 'toledo_dashboard_filter';
const REPO_FOLLOW_FILE = 'followed_stories.json';

// -- DOM refs --
const loadingBanner = document.getElementById('loading-banner');
const errorBanner = document.getElementById('error-banner');
const storiesEl = document.getElementById('stories');
const watchListWrap = document.getElementById('watch-list');
const watchListItems = document.getElementById('watch-list-items');
const liveSourcesWrap = document.getElementById('live-sources');
const liveSourcesGrid = document.getElementById('live-sources-grid');
const pastBriefsEl = document.getElementById('past-briefs');
const metaDate = document.getElementById('meta-date');
const metaWindow = document.getElementById('meta-window');
const metaAutoRefresh = document.getElementById('meta-auto-refresh');

// -- Date routing --
function targetDate() {
  const url = new URL(window.location.href);
  const param = url.searchParams.get('date');
  if (param && /^\d{4}-\d{2}-\d{2}$/.test(param)) return param;
  const d = new Date();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${d.getFullYear()}-${m}-${day}`;
}

function formatDateLong(iso) {
  // "2026-05-20" -> "May 20, 2026"
  const [y, m, d] = iso.split('-').map(n => parseInt(n, 10));
  const dt = new Date(y, m - 1, d);
  return dt.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
}

function showError(message) {
  errorBanner.textContent = message;
  errorBanner.style.display = 'block';
  loadingBanner.style.display = 'none';
}

// -- Load pipeline --
async function loadDashboard(date) {
  // 1. Fetch day-file
  let day;
  try {
    const res = await fetch(`days/${date}.json`, { cache: 'no-cache' });
    if (res.status === 404) {
      loadingBanner.style.display = 'none';
      storiesEl.innerHTML = `<p class="banner" style="text-align:center;">No brief published for ${date}.</p>`;
      return;
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    day = await res.json();
  } catch (e) {
    showError(`Couldn't load brief for ${date} — ${e.message}. Check your connection.`);
    return;
  }

  // 2. Collect unique story IDs
  const ids = [];
  const seen = new Set();
  for (const section of (day.sections || [])) {
    for (const sid of (section.story_ids || [])) {
      if (!seen.has(sid)) { seen.add(sid); ids.push(sid); }
    }
  }

  // 3. Fetch all stories in parallel. Resolve individually so one 404 doesn't fail the whole page.
  const storyResults = await Promise.all(ids.map(async (id) => {
    try {
      const res = await fetch(`stories/${id}.json`, { cache: 'no-cache' });
      if (!res.ok) return { id, error: `HTTP ${res.status}`, story: null };
      const story = await res.json();
      return { id, error: null, story };
    } catch (e) {
      return { id, error: e.message, story: null };
    }
  }));

  const stories = {};
  for (const r of storyResults) {
    if (r.story) stories[r.id] = r.story;
  }

  // 4. Render — Task 7 fills this in
  renderDashboard(day, stories, storyResults);

  loadingBanner.style.display = 'none';
}

function renderDashboard(_day, _stories, _storyResults) {
  // Task 7: render sections, top story, ongoing
  // Task 8: render past-briefs, watch-list, live-sources, meta
  // Task 10: wire follow/filter/people-chip init pipeline
}

// -- Kick off --
loadDashboard(targetDate());
```

- [ ] **Step 6.2: Open in browser and confirm fetch behavior.**

```bash
open dashboard/index.new.html
```

Devtools → Network tab. Reload. You should see:
- `days/2026-05-20.json` fetched (200).
- After that, ~16 parallel fetches for `stories/*.json` (each 200).
- "Loading stories…" banner disappears once everything resolves.

If you see 404s for `days/<date>.json` because the file:// URL routing is off, try opening with `?date=2026-05-20` appended.

If you see CORS errors loading from `file://`, that's a browser security setting and we'll hit it again later. For now you can either:
- Use Chrome with `--allow-file-access-from-files`
- Or serve the dashboard via a quick local server: `python3 -m http.server -d dashboard 8000` and visit `http://localhost:8000/index.new.html`

The local-server approach matches how Pages serves the live site.

- [ ] **Step 6.3: Commit.**

```bash
git add dashboard/index.new.html
git commit -m "Add fetch pipeline for day-file and stories to new dashboard"
```

---

## Task 7: Render JS — story cards, sections, top story, ongoing

**Files:**
- Modify: `dashboard/index.new.html`

**Goal:** Render the story cards into `<main id="stories">` with correct sections, top-story styling, and is-ongoing styling. Result: the new shell visually matches the live dashboard.

- [ ] **Step 7.1: Replace the stub `renderDashboard` function and add helper functions.** Find the function `function renderDashboard(_day, _stories, _storyResults) { ... }` and REPLACE it (plus add the helpers below) with:

```js
function renderDashboard(day, stories, storyResults) {
  // Header meta strip
  metaDate.textContent = formatDateLong(day.date);
  metaWindow.textContent = day.window || '';
  metaAutoRefresh.textContent = day.auto_refresh || '';
  document.title = `${day.title || 'Toledo Economic Development Dashboard'} — ${formatDateLong(day.date)}`;

  // Build cards by section, in order
  const ongoingSet = new Set(day.ongoing_story_ids || []);
  const topId = day.top_story_id;
  storiesEl.innerHTML = '';

  for (const section of (day.sections || [])) {
    if (section.title) {
      const titleEl = document.createElement('div');
      titleEl.className = 'section-title';
      titleEl.textContent = section.title;
      storiesEl.appendChild(titleEl);
    }
    for (const sid of (section.story_ids || [])) {
      const story = stories[sid];
      if (!story) {
        storiesEl.appendChild(renderErrorCard(sid));
        continue;
      }
      const card = renderStoryCard(story, {
        isTop: sid === topId,
        isOngoing: ongoingSet.has(sid),
      });
      storiesEl.appendChild(card);
    }
  }

  // Task 8 fills in past-briefs / watch-list / live-sources
  // Task 10 fills in init pipeline (follows / filter / story-maps)
}

function renderStoryCard(story, { isTop, isOngoing }) {
  const card = document.createElement('div');
  const classes = ['story-item'];
  if (isTop) classes.push('top-story');
  else classes.push('story');
  if (isOngoing) classes.push('is-ongoing');
  card.className = classes.join(' ');
  card.dataset.storyId = story.id;
  card.dataset.tags = (story.tags || []).join(' ');
  card.dataset.searchTerms = story.search_terms || '';
  card.dataset.sourceDate = story.source_date || '';
  // Encode people into the data-people pipe/semicolon format the existing JS expects
  const peopleStr = (story.people || [])
    .map(p => `${p.name}|${p.role || ''}|${p.search_terms || p.name}`)
    .join(';');
  card.dataset.people = peopleStr;

  // Follow button
  const followBtn = document.createElement('button');
  followBtn.className = 'follow-btn';
  followBtn.dataset.follow = story.id;
  followBtn.innerHTML = '<span class="star">☆</span><span class="label">Follow</span>';
  card.appendChild(followBtn);

  if (isTop) {
    const label = document.createElement('span');
    label.className = 'top-story-label';
    label.textContent = `Top Story · ${formatDateLong(story.posted_date)}`;
    card.appendChild(label);
    const h = document.createElement('h2');
    h.textContent = story.headline;
    card.appendChild(h);
  } else {
    const header = document.createElement('div');
    header.className = 'story-header';
    const h = document.createElement('h3');
    h.textContent = story.headline;
    header.appendChild(h);
    const tags = document.createElement('div');
    tags.className = 'tags';
    for (const t of (story.tags || [])) {
      const tagEl = document.createElement('span');
      tagEl.className = `tag tag-${t}`;
      tagEl.textContent = tagLabel(t);
      tags.appendChild(tagEl);
    }
    header.appendChild(tags);
    card.appendChild(header);
  }

  // Source-date chip (matches the daily-task's recency badges)
  if (story.source_date || isOngoing) {
    const dateChip = document.createElement('span');
    dateChip.className = 'story-date ' + ageClass(story.source_date, isOngoing);
    dateChip.textContent = recencyLabel(story.source_date, isOngoing);
    card.appendChild(dateChip);
  }

  // Paragraphs
  for (const para of (story.paragraphs || [])) {
    const p = document.createElement('p');
    p.innerHTML = para;  // story prose may contain <strong>, <em>, etc.
    card.appendChild(p);
  }

  // Why it matters
  if (story.why_it_matters) {
    const why = document.createElement('div');
    why.className = 'why';
    why.innerHTML = '<strong>Why it matters:</strong> ' + story.why_it_matters;
    card.appendChild(why);
  }

  // Sources
  if (story.sources && story.sources.length) {
    const src = document.createElement('div');
    src.className = 'sources-inline';
    for (const s of story.sources) {
      const a = document.createElement('a');
      a.href = s.url;
      a.target = '_blank';
      a.rel = 'noopener';
      a.textContent = s.title;
      src.appendChild(a);
    }
    card.appendChild(src);
  }

  // External map link (vibrancy-19-grants and similar)
  if (story.external_map_link) {
    const a = document.createElement('a');
    a.className = 'vibrancy-map-link';
    a.href = story.external_map_link.href;
    a.target = '_blank';
    a.rel = 'noopener';
    a.textContent = '→ ' + story.external_map_link.label;
    card.appendChild(a);
  }

  return card;
}

function renderErrorCard(sid) {
  const card = document.createElement('div');
  card.className = 'story story-item';
  card.dataset.storyId = sid;
  card.innerHTML = `<h3 style="color:#8c1a1a;">Story unavailable: <code>${sid}</code></h3><p>Could not load <code>stories/${sid}.json</code>. The brief may reference a story that hasn't been published yet.</p>`;
  return card;
}

function tagLabel(t) {
  // Matches the existing tag pill labels
  const map = {
    downtown: 'Downtown', warehouse: 'Warehouse Dist', vistula: 'Vistula',
    uptown: 'Uptown', junction: 'Junction', grants: 'Grants', citywide: 'Citywide',
  };
  return map[t] || t;
}

function ageClass(sourceDate, isOngoing) {
  // Mirror the existing .story-date.age-* CSS classes
  if (!sourceDate) return isOngoing ? 'age-ongoing' : 'age-recent';
  const days = daysSince(sourceDate);
  if (days < 0) return 'age-future';
  if (days <= 2) return 'age-new';
  if (days <= 7) return 'age-recent';
  return 'age-ongoing';
}

function recencyLabel(sourceDate, isOngoing) {
  if (!sourceDate) {
    return isOngoing ? 'Ongoing · no fresh reporting this window' : 'Recently reported';
  }
  const days = daysSince(sourceDate);
  const niceDate = formatDateShort(sourceDate);
  if (days < 0) return `Announced ${niceDate}`;
  if (days <= 2) return `Reported ${niceDate} · within last 48h`;
  if (days <= 7) return `Reported ${niceDate} · ${days} day${days === 1 ? '' : 's'} ago`;
  const weeks = Math.round(days / 7);
  return `Reported ${niceDate} · ${weeks} week${weeks === 1 ? '' : 's'} ago`;
}

function daysSince(iso) {
  const [y, m, d] = iso.split('-').map(n => parseInt(n, 10));
  const then = Date.UTC(y, m - 1, d);
  const now = Date.now();
  return Math.floor((now - then) / (1000 * 60 * 60 * 24));
}

function formatDateShort(iso) {
  const [y, m, d] = iso.split('-').map(n => parseInt(n, 10));
  const dt = new Date(y, m - 1, d);
  return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}
```

- [ ] **Step 7.2: Reload in browser, confirm cards render.**

```bash
open dashboard/index.new.html
# Or http://localhost:8000/index.new.html if using a local server
```

Expected:
- ~16 story cards appear with correct section headers between them.
- The top story has the yellow gradient banner with "Top Story · May 20, 2026".
- Stories with `is_ongoing` have the gray `#fafaf6` background.
- Tag pills appear in each card header.
- The "→ View all 17 properties on the Vibrancy map" pill button appears on `vibrancy-19-grants`.

Filter pills don't work yet (Task 10). Follow buttons don't work yet (Task 10). Story-map clicks don't work yet (Task 9). That's OK.

- [ ] **Step 7.3: Commit.**

```bash
git add dashboard/index.new.html
git commit -m "Render story cards from JSON in new dashboard"
```

---

## Task 8: Render JS — past-briefs, watch-list, live-sources, archive link

**Files:**
- Modify: `dashboard/index.new.html`

**Goal:** Fill in the header strip (past-briefs pills) and the footer sections (watch-list, live-sources) from the day-file. After this task, the new shell visually matches the live site end-to-end.

- [ ] **Step 8.1: Extend `renderDashboard`.** Find the comment `// Task 8 fills in past-briefs / watch-list / live-sources` and replace it (plus the comment for Task 10 on the next line, which we'll address in Task 10) with these calls — and add the helper functions below `renderStoryCard`:

Inside `renderDashboard` body, after the section/story loop, add:

```js
  renderPastBriefs(day.date);
  renderWatchList(day.watch_list || []);
  renderLiveSources(day.live_sources || []);
```

Then add these helpers somewhere in the IIFE (e.g., right after `renderErrorCard`):

```js
function renderPastBriefs(currentDateIso) {
  // Show pills for the previous 3 day-files that exist (try yesterday, day-before, etc.)
  // Plus a static "All →" link to the archive folder.
  pastBriefsEl.innerHTML = '';
  const label = document.createElement('span');
  label.className = 'past-briefs-label';
  label.textContent = 'Past briefs:';
  pastBriefsEl.appendChild(label);

  // Try the previous 3 days. Each pill links to ?date=...; the dashboard will show
  // a "no brief" message if the day-file doesn't exist, which is graceful.
  const [y, m, d] = currentDateIso.split('-').map(n => parseInt(n, 10));
  const seed = new Date(Date.UTC(y, m - 1, d));
  for (let i = 1; i <= 3; i++) {
    const dt = new Date(seed);
    dt.setUTCDate(seed.getUTCDate() - i);
    const iso = dt.toISOString().slice(0, 10);
    const pill = document.createElement('a');
    pill.className = 'brief-pill';
    pill.href = `?date=${iso}`;
    pill.textContent = dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    pastBriefsEl.appendChild(pill);
  }
  const allLink = document.createElement('a');
  allLink.className = 'brief-pill all-archive';
  allLink.href = 'archive/';
  allLink.textContent = 'All →';
  pastBriefsEl.appendChild(allLink);
}

function renderWatchList(items) {
  if (!items.length) { watchListWrap.style.display = 'none'; return; }
  watchListWrap.style.display = '';
  watchListItems.innerHTML = '';
  for (const item of items) {
    const li = document.createElement('li');
    li.innerHTML = item;  // items may contain inline <strong>/<em>
    watchListItems.appendChild(li);
  }
}

function renderLiveSources(sources) {
  if (!sources.length) { liveSourcesWrap.style.display = 'none'; return; }
  liveSourcesWrap.style.display = '';
  liveSourcesGrid.innerHTML = '';
  for (const s of sources) {
    const a = document.createElement('a');
    a.href = s.url;
    a.target = '_blank';
    a.rel = 'noopener';
    a.textContent = s.title;
    liveSourcesGrid.appendChild(a);
  }
}
```

- [ ] **Step 8.2: Reload and verify in browser.**

Expected:
- "Past briefs:" row appears above the filters, with 3 dated pills (May 19, May 18, May 17) plus an "All →" link.
- The "What to watch in the next report" box appears below the stories, populated with the day-file's `watch_list` entries.
- The "Live source pages" grid appears at the bottom with the day-file's sources.
- The meta strip in the header shows "Last refreshed: May 20, 2026 · Window: Rolling 48-hour focus · Auto-refresh: Daily 5:00 AM".

Past-briefs pills are clickable but their destination pages don't exist yet (May 19's day-file wasn't backfilled per spec) — clicking should land on the "No brief published for 2026-05-19." message.

- [ ] **Step 8.3: Commit.**

```bash
git add dashboard/index.new.html
git commit -m "Render past-briefs, watch-list, live-sources from day-file"
```

---

## Task 9: Render JS — adapt story-map data source to story.locations

**Files:**
- Modify: `dashboard/index.new.html`

**Goal:** Restore the inline mini-map feature (story-maps) on the new shell. The behavior is identical to what the live site does today; the only change is the data source — instead of a single `STORY_LOCATIONS` JS object, each story carries its own `locations: [...]` array and `external_map_link`.

- [ ] **Step 9.1: Find the closing `})();` of the IIFE.** Before it, paste the entire story-maps JS block below. This block is adapted from the live site's existing story-maps code; the only changes are (a) it reads from `STORY_LOCATIONS_BY_ID` built at render time from the loaded stories, and (b) `hydrateStoryTriggers` accepts a callable to fetch the location data.

Add a module-scoped registry near the top of the IIFE (right after the DOM refs):

```js
// Map story-id → its loaded story object (populated at render time)
// Used by the story-maps hydration to look up locations.
const STORY_BY_ID = {};
```

Inside `renderDashboard`, immediately after `for (const r of storyResults)` populates `stories`, also populate `STORY_BY_ID`:

```js
  for (const r of storyResults) {
    if (r.story) {
      stories[r.id] = r.story;
      STORY_BY_ID[r.id] = r.story;
    }
  }
```

Then add the full story-maps code as a sibling to the other helpers (anywhere inside the IIFE before `loadDashboard` is called):

```js
// === Story-maps (inline mini-maps on address clicks) ===
// Behavior matches the live site's existing implementation; the only
// difference is the data source: each story carries its own locations[]
// and external_map_link, rather than a single STORY_LOCATIONS constant.

const cardMaps = new Map();  // story-id → {mapDiv, map, layer, currentTrigger}

function wrapMatchInCard(card, matchText, onClick) {
  const candidates = card.querySelectorAll('p, .why');
  for (const el of candidates) {
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null);
    const textNodes = [];
    while (walker.nextNode()) textNodes.push(walker.currentNode);
    for (const node of textNodes) {
      const idx = node.nodeValue.indexOf(matchText);
      if (idx < 0) continue;
      const before = node.nodeValue.slice(0, idx);
      const after  = node.nodeValue.slice(idx + matchText.length);
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'addr-link';
      btn.textContent = matchText;
      btn.setAttribute('aria-expanded', 'false');
      btn.addEventListener('click', e => { e.stopPropagation(); onClick(btn); });
      const frag = document.createDocumentFragment();
      if (before) frag.appendChild(document.createTextNode(before));
      frag.appendChild(btn);
      if (after) frag.appendChild(document.createTextNode(after));
      node.parentNode.replaceChild(frag, node);
      return btn;
    }
  }
  return null;
}

function appendHeadlineChip(card, label, onClick) {
  const chip = document.createElement('button');
  chip.type = 'button';
  chip.className = 'headline-loc-chip';
  chip.textContent = label;
  chip.setAttribute('aria-expanded', 'false');
  chip.addEventListener('click', e => { e.stopPropagation(); onClick(chip); });
  const header = card.querySelector('.story-header') || card.querySelector('h2');
  if (header) header.insertAdjacentElement('afterend', chip);
  return chip;
}

function hydrateStoryTriggers() {
  document.querySelectorAll('.story-item').forEach(card => {
    const id = card.dataset.storyId;
    const story = STORY_BY_ID[id];
    if (!story) return;
    // External-map stories render the link inside the card already (Task 7 handled this);
    // skip story-map hydration for them.
    if (story.external_map_link) return;
    for (const loc of (story.locations || [])) {
      const onClick = (trigger) => openMapFor(card, loc, trigger);
      let trigger = null;
      if (loc.match) trigger = wrapMatchInCard(card, loc.match, onClick);
      if (!trigger) trigger = appendHeadlineChip(card, loc.label, onClick);
    }
  });
}

function ensureMapContainer(card) {
  let mapDiv = card.querySelector('.story-map');
  if (mapDiv) return mapDiv;
  mapDiv = document.createElement('div');
  mapDiv.className = 'story-map';
  mapDiv.setAttribute('role', 'region');
  card.appendChild(mapDiv);
  return mapDiv;
}

function buildLeafletMap(mapDiv) {
  const map = L.map(mapDiv, {
    zoomControl: true,
    attributionControl: true,
    scrollWheelZoom: false
  }).setView([41.6528, -83.5379], 13);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap, &copy; CARTO',
    subdomains: 'abcd', maxZoom: 19
  }).addTo(map);
  map.on('click', () => map.scrollWheelZoom.enable());
  return map;
}

function clearOverlay(state) {
  if (state.layer) { state.layer.remove(); state.layer = null; }
}

function renderItem(state, item) {
  clearOverlay(state);
  state.mapDiv.setAttribute('aria-label', 'Map of ' + item.label);
  if (item.shape === 'point') {
    const m = L.marker([item.lat, item.lon]).bindTooltip(item.label);
    m.addTo(state.map);
    state.layer = m;
    state.map.setView([item.lat, item.lon], 16, { animate: true });
    updateGmapsLink(state.mapDiv, item.lat, item.lon);
    return;
  }
  if (item.shape === 'line') {
    const line = L.polyline(item.path, { color: '#1a4d8c', weight: 5, opacity: 0.85 })
      .bindTooltip(item.label);
    line.addTo(state.map);
    state.layer = line;
    state.map.fitBounds(line.getBounds(), { padding: [20, 20] });
    const mid = item.path[Math.floor(item.path.length / 2)];
    updateGmapsLink(state.mapDiv, mid[0], mid[1]);
    return;
  }
  if (item.shape === 'polygon') {
    const rect = L.rectangle(item.bbox, {
      color: '#1a4d8c', weight: 1, fillColor: '#1a4d8c', fillOpacity: 0.15
    }).bindTooltip(item.label);
    rect.addTo(state.map);
    state.layer = rect;
    state.map.fitBounds(rect.getBounds(), { padding: [20, 20] });
    const c = rect.getBounds().getCenter();
    updateGmapsLink(state.mapDiv, c.lat, c.lng);
    return;
  }
}

function updateGmapsLink(mapDiv, lat, lon) {
  let a = mapDiv.querySelector('.gmaps-link');
  if (!a) {
    a = document.createElement('a');
    a.className = 'gmaps-link';
    a.target = '_blank';
    a.rel = 'noopener';
    a.textContent = 'Open in Google Maps ↗';
    mapDiv.appendChild(a);
  }
  a.href = `https://www.google.com/maps?q=${lat},${lon}`;
}

function openMapFor(card, item, trigger) {
  // Leaflet-fallback: if Leaflet didn't load, open Google Maps in a new tab.
  if (typeof L === 'undefined') {
    const lat = item.lat ?? (item.path && item.path[0][0]) ?? (item.bbox && item.bbox[0][0]);
    const lon = item.lon ?? (item.path && item.path[0][1]) ?? (item.bbox && item.bbox[0][1]);
    window.open(`https://www.google.com/maps?q=${lat},${lon}`, '_blank', 'noopener');
    return;
  }

  const id = card.dataset.storyId;
  let state = cardMaps.get(id);

  if (state && state.currentTrigger === trigger && state.mapDiv.classList.contains('open')) {
    closeMap(card);
    return;
  }

  const mapDiv = ensureMapContainer(card);
  if (!state) {
    state = { mapDiv, map: null, layer: null, currentTrigger: null };
    cardMaps.set(id, state);
  }

  if (state.currentTrigger && state.currentTrigger !== trigger) {
    state.currentTrigger.setAttribute('aria-expanded', 'false');
  }
  state.currentTrigger = trigger;
  trigger.setAttribute('aria-expanded', 'true');

  mapDiv.classList.add('open');

  const initMap = () => {
    if (!state.map) state.map = buildLeafletMap(mapDiv);
    state.map.invalidateSize();
    renderItem(state, item);
  };
  setTimeout(initMap, 230);
}

function closeMap(card) {
  const id = card.dataset.storyId;
  const state = cardMaps.get(id);
  if (!state) return;
  state.mapDiv.classList.remove('open');
  if (state.currentTrigger) state.currentTrigger.setAttribute('aria-expanded', 'false');
  state.currentTrigger = null;
}

// Esc-to-close on the focused card
document.addEventListener('keydown', e => {
  if (e.key !== 'Escape') return;
  const focused = document.activeElement;
  if (!focused) return;
  const card = focused.closest('.story-item');
  if (!card) return;
  closeMap(card);
});
```

`hydrateStoryTriggers` is called from the init pipeline added in Task 10. For now the functions exist but aren't wired into the render flow yet.

- [ ] **Step 9.2: Reload and verify the code parses.**

Open devtools console, no SyntaxError. Cards still render (Task 7's behavior is preserved). Address links / chips don't appear yet — they're hydrated in Task 10.

- [ ] **Step 9.3: Commit.**

```bash
git add dashboard/index.new.html
git commit -m "Add story-maps code adapted to story.locations on new dashboard"
```

---

## Task 10: Render JS — wire init pipeline (follows, filter, person chips, story-maps)

**Files:**
- Modify: `dashboard/index.new.html`

**Goal:** Port the existing follow/filter/person-chip logic into the new shell and run it AFTER cards are rendered. After this task, every interactive feature works.

- [ ] **Step 10.1: Add the follow/filter/person-chip helpers** by pasting this block into the IIFE, somewhere before `renderDashboard`. It's the existing live-site code, copied verbatim with only minor adjustments noted:

```js
// === Follow panel + filter + person chips (ported from previous dashboard) ===

let authorFollows = { stories: {}, people: {} };

async function loadAuthorFollows() {
  try {
    const res = await fetch(REPO_FOLLOW_FILE, { cache: 'no-cache' });
    if (!res.ok) return;
    const data = await res.json();
    authorFollows = { stories: {}, people: {} };
    (data.stories || data.followed || []).forEach(s => { if (s.id) authorFollows.stories[s.id] = s; });
    (data.people || []).forEach(p => { if (p.id) authorFollows.people[p.id] = p; });
  } catch (e) { /* file may not exist yet */ }
}

function personId(name) {
  return 'person:' + name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}

function parsePeople(card) {
  const raw = card.dataset.people || '';
  if (!raw.trim()) return [];
  return raw.split(';').map(s => s.trim()).filter(Boolean).map(entry => {
    const [name, role, terms] = entry.split('|').map(x => (x || '').trim());
    return { id: personId(name), name, role: role || '', search_terms: terms || name };
  });
}

function loadFollows() {
  try {
    const raw = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    return { stories: raw.stories || {}, people: raw.people || {} };
  } catch (e) { return { stories: {}, people: {} }; }
}

function saveFollows(follows) {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(follows)); } catch (e) {}
}

function storyMetadata(id) {
  const card = document.querySelector('[data-story-id="' + id + '"]');
  if (!card) return null;
  const headlineEl = card.querySelector('h2, h3');
  const tags = (card.dataset.tags || '').split(/\s+/).filter(Boolean);
  const terms = card.dataset.searchTerms || '';
  const sources = Array.from(card.querySelectorAll('.sources-inline a'))
    .map(a => ({ title: a.textContent.trim(), url: a.href }));
  const people = parsePeople(card).map(p => p.name);
  return { id, headline: headlineEl ? headlineEl.textContent.trim() : id, tags, search_terms: terms, sources, people };
}

function renderAuthorBadges() {
  document.querySelectorAll('.story-item').forEach(card => {
    const id = card.dataset.storyId;
    const isAuthor = !!authorFollows.stories[id];
    card.classList.toggle('is-author-followed', isAuthor);
    const existing = card.querySelector('.author-badge');
    if (existing) existing.remove();
    if (isAuthor) {
      const badge = document.createElement('span');
      badge.className = 'author-badge';
      badge.textContent = '★ Followed';
      badge.title = "Followed in author's daily brief";
      card.appendChild(badge);
    }
  });
}

const followCountTotal = document.getElementById('follow-count-total');
const followCountStories = document.getElementById('follow-count-stories');
const followCountPeople = document.getElementById('follow-count-people');
const followStoriesWrap = document.getElementById('follow-stories-wrap');
const followPeopleWrap = document.getElementById('follow-people-wrap');
const followListStories = document.getElementById('follow-list-stories');
const followListPeople = document.getElementById('follow-list-people');
const followEmpty = document.getElementById('follow-empty');

function renderFollowPanel() {
  const follows = loadFollows();
  const storyIds = Object.keys(follows.stories);
  const peopleIds = Object.keys(follows.people);
  const total = storyIds.length + peopleIds.length;
  followCountTotal.textContent = total;
  followCountStories.textContent = storyIds.length;
  followCountPeople.textContent = peopleIds.length;
  followEmpty.style.display = total === 0 ? 'block' : 'none';
  followStoriesWrap.style.display = storyIds.length === 0 ? 'none' : 'block';
  followPeopleWrap.style.display = peopleIds.length === 0 ? 'none' : 'block';

  followListStories.innerHTML = '';
  storyIds.forEach(id => {
    const entry = follows.stories[id];
    const li = document.createElement('li');
    const info = document.createElement('div');
    info.className = 'follow-info';
    const headline = document.createElement('strong');
    headline.textContent = entry.headline || id;
    info.appendChild(headline);
    const date = document.createElement('span');
    date.className = 'followed-on';
    date.textContent = '· followed ' + (entry.followed_at || '').slice(0,10);
    info.appendChild(date);
    const terms = document.createElement('span');
    terms.className = 'terms';
    terms.textContent = 'Search terms: ' + (entry.search_terms || '(none)');
    info.appendChild(terms);
    li.appendChild(info);
    const btn = document.createElement('button');
    btn.className = 'unfollow-btn';
    btn.textContent = 'Unfollow';
    btn.addEventListener('click', () => toggleStoryFollow(id, false));
    li.appendChild(btn);
    followListStories.appendChild(li);
  });

  followListPeople.innerHTML = '';
  peopleIds.forEach(id => {
    const entry = follows.people[id];
    const li = document.createElement('li');
    const info = document.createElement('div');
    info.className = 'follow-info';
    const name = document.createElement('strong');
    name.textContent = entry.name || id;
    info.appendChild(name);
    const role = document.createElement('span');
    role.className = 'followed-on';
    role.textContent = entry.role ? '· ' + entry.role : '';
    info.appendChild(role);
    const terms = document.createElement('span');
    terms.className = 'terms';
    terms.textContent = 'Search terms: ' + (entry.search_terms || entry.name);
    info.appendChild(terms);
    li.appendChild(info);
    const btn = document.createElement('button');
    btn.className = 'unfollow-btn';
    btn.textContent = 'Unfollow';
    btn.addEventListener('click', () => togglePersonFollow(id, null, false));
    li.appendChild(btn);
    followListPeople.appendChild(li);
  });
}

function renderStoryFollowState() {
  const follows = loadFollows();
  document.querySelectorAll('.follow-btn').forEach(btn => {
    const id = btn.dataset.follow;
    const isOn = !!follows.stories[id];
    btn.classList.toggle('is-active', isOn);
    btn.querySelector('.star').textContent = isOn ? '★' : '☆';
    btn.querySelector('.label').textContent = isOn ? 'Following' : 'Follow';
    const card = document.querySelector('[data-story-id="' + id + '"]');
    if (card) card.classList.toggle('is-followed', isOn);
  });
}

function renderPersonChips() {
  const follows = loadFollows();
  document.querySelectorAll('.story-item').forEach(card => {
    const existing = card.querySelector('.people-row');
    if (existing) existing.remove();
    const people = parsePeople(card);
    if (people.length === 0) return;
    const row = document.createElement('div');
    row.className = 'people-row';
    const label = document.createElement('span');
    label.className = 'person-label';
    label.textContent = 'People:';
    row.appendChild(label);
    people.forEach(p => {
      const chip = document.createElement('button');
      chip.className = 'person-chip';
      if (follows.people[p.id]) chip.classList.add('is-followed');
      chip.textContent = p.name;
      chip.title = p.role ? p.role + '  ·  click to ' + (follows.people[p.id] ? 'unfollow' : 'follow') : 'click to ' + (follows.people[p.id] ? 'unfollow' : 'follow');
      chip.addEventListener('click', e => { e.stopPropagation(); togglePersonFollow(p.id, p); });
      row.appendChild(chip);
    });
    const header = card.querySelector('.story-header');
    if (header) header.insertAdjacentElement('afterend', row);
    else {
      const h2 = card.querySelector('h2');
      if (h2) h2.insertAdjacentElement('afterend', row);
    }
  });
}

function toggleStoryFollow(id, force) {
  const follows = loadFollows();
  const meta = storyMetadata(id);
  if (!meta) return;
  const currentlyFollowed = !!follows.stories[id];
  const next = typeof force === 'boolean' ? force : !currentlyFollowed;
  if (next) follows.stories[id] = Object.assign({}, meta, { followed_at: new Date().toISOString() });
  else delete follows.stories[id];
  saveFollows(follows);
  renderStoryFollowState();
  renderFollowPanel();
  applyFilter();
}

function togglePersonFollow(id, personMeta, force) {
  const follows = loadFollows();
  const currentlyFollowed = !!follows.people[id];
  const next = typeof force === 'boolean' ? force : !currentlyFollowed;
  if (next) {
    if (!personMeta) return;
    follows.people[id] = Object.assign({}, personMeta, { followed_at: new Date().toISOString() });
  } else { delete follows.people[id]; }
  saveFollows(follows);
  renderPersonChips();
  renderFollowPanel();
}

let currentFilter = 'all';
const filterButtons = document.querySelectorAll('.filter-btn');
const allItems = () => document.querySelectorAll('.story-item');

function applyFilter(filter) {
  if (filter) currentFilter = filter;
  const follows = loadFollows();
  allItems().forEach(el => {
    const id = el.dataset.storyId;
    const tags = (el.dataset.tags || '').split(/\s+/);
    let show = true;
    if (currentFilter === 'followed') show = !!follows.stories[id] || !!authorFollows.stories[id];
    else if (currentFilter !== 'all') show = tags.includes(currentFilter);
    el.classList.toggle('hidden', !show);
  });
  filterButtons.forEach(b => b.classList.toggle('active', b.dataset.filter === currentFilter));
  try { localStorage.setItem(FILTER_KEY, currentFilter); } catch (e) {}
}

filterButtons.forEach(b => b.addEventListener('click', () => applyFilter(b.dataset.filter)));
try { currentFilter = localStorage.getItem(FILTER_KEY) || 'all'; } catch (e) {}

function bindFollowButtons() {
  document.querySelectorAll('.follow-btn').forEach(btn => {
    btn.addEventListener('click', e => { e.stopPropagation(); toggleStoryFollow(btn.dataset.follow); });
  });
}
```

- [ ] **Step 10.2: Wire the init pipeline into renderDashboard.** Find the line `// Task 10 fills in init pipeline (follows / filter / story-maps)` and REPLACE it with:

```js
  // Pipeline ordering matters: rendering must finish, then follows/chips/maps hydrate.
  loadAuthorFollows().then(() => {
    renderAuthorBadges();
    renderPersonChips();
    renderStoryFollowState();
    bindFollowButtons();
    renderFollowPanel();
    hydrateStoryTriggers();
    applyFilter();
  });
```

- [ ] **Step 10.3: Reload and verify every interactive feature.**

Expected:
- ★ Follow button on a story works: clicking adds it to the Following panel, button flips to "★ Following", localStorage persists.
- Person chips below story headers, clickable to follow/unfollow.
- Filter pills (All / Followed only / Grants / Downtown / Warehouse Dist / Vistula / Uptown / Junction / Citywide) all hide/show cards correctly.
- Address links in story prose (e.g., "📍 28 N. Erie St." in Huron Yards) open inline mini-maps.
- Headline chips (e.g., "📍 Owens Corning HQ") open mini-maps.
- ConnecToledo's 4 park names click through to the same recentering map.
- RAISE polygon renders, Vistula Metropark polyline renders.
- "→ View all 17 properties on the Vibrancy map" button on vibrancy-19-grants opens the root map in a new tab.
- Escape closes an open mini-map.
- Followed filter pill shows only followed stories.

- [ ] **Step 10.4: Commit.**

```bash
git add dashboard/index.new.html
git commit -m "Wire follow/filter/people/story-maps init pipeline post-render"
```

---

## Task 11: Render JS — error handling polish

**Files:**
- Modify: `dashboard/index.new.html`

**Goal:** Polish the failure paths so the page never just silently breaks. Most error paths are already wired (Task 6's `showError`, Task 7's `renderErrorCard`, story-maps' Leaflet-fallback). This task tightens any gaps.

- [ ] **Step 11.1: Add a no-section fallback.** If a day-file has empty `sections` (a malformed file), the page would currently show only "Loading stories…" forever. After Task 6's loadDashboard finishes, check for this. Find the line `loadingBanner.style.display = 'none';` at the end of `loadDashboard` and replace it with:

```js
  // Show a graceful message if a day-file is structurally empty.
  if (!day.sections || day.sections.length === 0) {
    storiesEl.innerHTML = `<p class="banner" style="text-align:center;">Brief for ${date} is empty — no sections.</p>`;
  }
  loadingBanner.style.display = 'none';
```

- [ ] **Step 11.2: Verify 404 day-file path.**

Open `dashboard/index.new.html?date=2026-01-01` (definitely no day-file for that date). Expected: a banner "No brief published for 2026-01-01." in the cards area. Loading banner gone. No console errors.

- [ ] **Step 11.3: Verify 404 story path.**

Temporarily edit `dashboard/days/2026-05-20.json` to add a fake story id (e.g., `"fake-story"`) to any section. Reload. Expected: an error placeholder card appears for `fake-story` with a "Story unavailable" heading. Other stories render fine.

REVERT that change before committing.

- [ ] **Step 11.4: Verify network-failure path.**

Block all requests in devtools (Network tab → "Offline"). Hard reload. Expected: a red error banner at the top: "Couldn't load brief for 2026-05-20 — Failed to fetch. Check your connection." Loading banner gone.

- [ ] **Step 11.5: Verify Leaflet-fallback (existing behavior preserved).**

```js
// In devtools console BEFORE clicking any address link, run:
delete window.L;
```

Click an address link — expected: opens Google Maps in a new tab at those coordinates.

- [ ] **Step 11.6: Commit.**

```bash
git add dashboard/index.new.html
git commit -m "Add empty-day-file guard and verify error paths in new shell"
```

---

## Task 12: Local browser verification of index.new.html (full feature parity)

**Files:** none modified.

**Goal:** Side-by-side comparison against the live `dashboard/index.html` to confirm zero feature regression before cutover.

- [ ] **Step 12.1: Open both pages in adjacent browser tabs.**

```bash
open dashboard/index.html
open dashboard/index.new.html
```

Or via local server: `http://localhost:8000/index.html` and `http://localhost:8000/index.new.html`.

- [ ] **Step 12.2: Compare visually, top to bottom.**

For each item below, both tabs should match (no text/layout/color differences):

- Header title, subtitle, meta strip
- Banner text
- Follow panel header + count
- Past briefs row (the new shell has 3 pills for the previous 3 dates; the live shell shows whatever the daily task added — at least visually styled the same way)
- Filter pill row
- Top story card (yellow banner, headline, paragraphs, "Why it matters", sources, "→ View all 17 properties..." pill where applicable)
- Each section title + each story card in the same order
- Watch-list box
- Live-sources grid + archive link
- Footer note

- [ ] **Step 12.3: Side-by-side interactive test.**

For each interactive feature, test on both tabs and confirm matching behavior:

- ★ Follow on a story — appears in Following panel on both.
- ★ Unfollow — disappears from panel on both.
- Person chip click — chip flips, appears in Following People list, persists in localStorage on both.
- Filter pills — same cards hidden/shown on both.
- "★ Followed only" filter shows the right cards on both.
- Story-map inline expand on address click — same map, same pin location on both.
- Esc closes — same behavior on both.

- [ ] **Step 12.4: Mobile viewport test.**

In devtools, set viewport to 375px (iPhone SE). Reload both tabs. Expected: same single-column layout, same mini-map height (180px), no horizontal overflow on either.

- [ ] **Step 12.5: Past-day routing.**

Open `dashboard/index.new.html?date=2026-05-19` — expected "No brief published for 2026-05-19." banner.

Open `dashboard/index.new.html?date=2026-05-20` — same content as today.

- [ ] **Step 12.6: Resolve any discrepancies.**

If you spot a mismatch in step 12.2 (visual) or 12.3 (interactive), trace it back to which task introduced it and fix in-place. Then re-verify. Do NOT cut over until 12.2 and 12.3 match.

This step has no commit unless a fix is needed; if you make a fix:

```bash
git add dashboard/index.new.html
git commit -m "Fix parity issue with live dashboard: <description>"
```

---

## Task 13: Cutover — replace index.html with index.new.html

**Files:**
- Delete: `dashboard/index.html`
- Rename: `dashboard/index.new.html` → `dashboard/index.html`

**Goal:** The atomic moment. Replace the live dashboard with the new shell. From this commit forward, the dashboard reads from JSON.

- [ ] **Step 13.1: Confirm Task 12 verification passed.** If you skipped step 12.6 fixes, do them now.

- [ ] **Step 13.2: Perform the rename.**

```bash
rm dashboard/index.html
mv dashboard/index.new.html dashboard/index.html
git status --short
```

Expected status:
```
 D dashboard/index.html        (old, deleted)
?? dashboard/index.html        (new, the renamed file)
```

Actually git will likely show this as a single modification once you `git add` because the file paths are identical:

```bash
git add dashboard/index.html
git status --short
```

Expected:
```
M  dashboard/index.html
 D dashboard/index.new.html    (if any stale ref)
```

If `dashboard/index.new.html` is still showing in `git status`, that's because the rename was done outside of git's tracking — make sure both states are staged:

```bash
git add dashboard/index.html dashboard/index.new.html
git status --short
```

Final expected:
```
M  dashboard/index.html
```

(The deletion of `index.new.html` is captured by the rename git infers from content similarity.)

- [ ] **Step 13.3: Final pre-commit sanity check.**

```bash
grep -c "STORY_LOCATIONS = " dashboard/index.html
```

Expected: `0` (the old constant is fully gone).

```bash
grep -c "fetch('days/" dashboard/index.html
grep -c "fetch(\`stories/" dashboard/index.html
```

Expected: each ≥1 (the new fetch calls are present).

- [ ] **Step 13.4: Open the file directly to confirm it's the new shell.**

```bash
open dashboard/index.html
```

Verify the dashboard loads from JSON exactly like `index.new.html` did. (Same URL, same content.)

- [ ] **Step 13.5: Commit.**

```bash
git commit -m "Cut dashboard over to JSON-driven render (replace HTML page with thin shell)"
```

This is the one commit that, if reverted, restores the old HTML-driven dashboard.

---

## Task 14: Update deploy.sh with jq pre-commit JSON validation

**Files:**
- Modify: `dashboard/deploy.sh`

**Goal:** Prevent the daily task from committing broken JSON.

- [ ] **Step 14.1: Confirm jq is installed.**

```bash
jq --version
```

Expected: something like `jq-1.6` or newer. If missing, `brew install jq`.

- [ ] **Step 14.2: Edit `dashboard/deploy.sh`.** Find the line `git add dashboard/` and insert validation BEFORE the commit. Replace this block:

```sh
# Stage dashboard changes only (don't accidentally commit the Vibrancy map)
git add dashboard/

# If nothing to commit, exit cleanly
if git diff --staged --quiet; then
  echo "No changes to deploy."
  exit 0
fi
```

With:

```sh
# Stage dashboard changes only (don't accidentally commit the Vibrancy map)
git add dashboard/

# If nothing to commit, exit cleanly
if git diff --staged --quiet; then
  echo "No changes to deploy."
  exit 0
fi

# Validate every JSON file under dashboard/ before committing. A broken JSON
# would 404-poison the dashboard until the next manual fix.
if command -v jq >/dev/null 2>&1; then
  bad_files=()
  while IFS= read -r f; do
    if ! jq empty "$f" >/dev/null 2>&1; then
      bad_files+=("$f")
    fi
  done < <(find dashboard -name '*.json' -type f)
  if [ ${#bad_files[@]} -gt 0 ]; then
    echo "Invalid JSON in:"
    printf '  %s\n' "${bad_files[@]}"
    echo "Aborting deploy."
    exit 1
  fi
else
  echo "WARNING: jq not installed; skipping JSON validation."
fi
```

- [ ] **Step 14.3: Test the validation.** Temporarily corrupt a JSON file:

```bash
echo "not valid json" > /tmp/test.json
cp dashboard/stories/huron-yards-phase-two.json /tmp/test-backup.json
echo "not valid json" > dashboard/stories/huron-yards-phase-two.json
./dashboard/deploy.sh "test bad json" 2>&1 | head -10
```

Expected output:
```
Invalid JSON in:
  dashboard/stories/huron-yards-phase-two.json
Aborting deploy.
```

Restore the file:

```bash
mv /tmp/test-backup.json dashboard/stories/huron-yards-phase-two.json
git checkout dashboard/stories/huron-yards-phase-two.json
```

- [ ] **Step 14.4: Commit.**

```bash
git add dashboard/deploy.sh
git commit -m "Validate JSON in deploy.sh before commit"
```

---

## Task 15: Push and verify the live site

**Files:** none modified.

**Goal:** Ship to GitHub Pages and confirm the live dashboard renders from JSON.

- [ ] **Step 15.1: Review the local commit log before pushing.**

```bash
git log --oneline origin/main..HEAD
```

Expected: roughly these 11 commits (your SHAs will differ, plus daily-task commits may be interleaved if the 5 AM task fired during work):

```
Validate JSON in deploy.sh before commit
Cut dashboard over to JSON-driven render (replace HTML page with thin shell)
Add empty-day-file guard and verify error paths in new shell
Wire follow/filter/people/story-maps init pipeline post-render
Add story-maps code adapted to story.locations on new dashboard
Render past-briefs, watch-list, live-sources from day-file
Render story cards from JSON in new dashboard
Add fetch pipeline for day-file and stories to new dashboard
Add new dashboard shell at index.new.html (structure + skeleton)
Regenerate May 20 brief from JSON via render_brief.py
Add render_brief.py: day-file + stories to markdown
Bootstrap stories/ and days/ JSON corpus from current dashboard
Add extract_today.py: one-time HTML to JSON bootstrap
```

- [ ] **Step 15.2: Push.** If the remote has new commits from the daily task, rebase first:

```bash
git fetch origin
if [ "$(git rev-list --count HEAD..origin/main)" -gt 0 ]; then
  git pull --rebase origin main
fi
git push origin main
```

- [ ] **Step 15.3: Wait 1–2 min for Pages to rebuild, then open the live site.**

```bash
sleep 90 && open https://vanderpoolteacher.github.io/toledo-vibrancy-2026/dashboard/
```

Expected: identical content to the local file. Devtools network tab shows fetches to `days/2026-05-20.json` and `stories/*.json` (all 200).

- [ ] **Step 15.4: Verify past-day routing on live site.**

`https://vanderpoolteacher.github.io/toledo-vibrancy-2026/dashboard/?date=2026-05-19` → "No brief published for 2026-05-19." (We didn't backfill, per spec.)

- [ ] **Step 15.5: Verify story-maps still work on live site.**

Click an inline address link on, say, Huron Yards. The mini-map should expand with the Warehouse District pin. CARTO Voyager tiles should load.

- [ ] **Step 15.6: Document the manual step still owed.** No commit; just a reminder:

> **TODO (manual):** Update the 5 AM scheduled agent's prompt via `/schedule` to emit JSON files per the daily-task contract in the spec. This is not part of the implementation plan; it's a configuration change on the user's side.

The cutover is complete. Future daily-task runs that follow the new contract will continue to populate `dashboard/stories/` and `dashboard/days/` and re-render the markdown brief. The dashboard renders whatever's there.

---

## Self-review notes

**Spec coverage:**

- File layout (spec § Architecture, File layout) → Tasks 1–4 (scripts + JSON corpus) and Task 5–13 (new shell).
- Story JSON schema (spec § Story JSON schema) → embedded in Task 1's script logic; written to disk in Task 2.
- Day JSON schema (spec § Day JSON schema) → built and written in Task 2; consumed in Tasks 6–10.
- Render pipeline (spec § Render pipeline) → Tasks 5–11.
- Story-card rendering, data-attribute mirroring (spec § Story-card rendering) → Task 7 + Task 9.
- Date routing (spec § Date routing) → Task 6 (`targetDate()`) + Task 8 (past-briefs pills).
- Init-pipeline timing (spec § Render pipeline step 10) → Task 10's `renderDashboard` `.then(...)` block.
- Daily task contract (spec § Daily task contract) → noted as out-of-band manual step at Task 15.6 (the user updates the scheduled agent separately).
- Markdown renderer (spec § Markdown renderer) → Task 3, Task 4.
- Migration plan (spec § Migration plan steps 1–6) → Tasks 1–14 cover steps 1–5; step 6 (retroactive May 19 backfill) is explicitly out of scope per the spec.
- Error handling (spec § Error handling table) → Task 6 (404 day, network failure), Task 7 (404 story → error card), Task 9 (Leaflet fallback), Task 11 (empty day-file guard + verification), Task 14 (invalid JSON in deploy).
- Testing (spec § Testing) → Task 12 (full local verification) + Task 15 (live-site verification).

**Placeholder scan:**

- No TBDs / TODOs that block implementation.
- The Task 15.6 "TODO (manual)" is intentional — it's a configuration change outside this repo (the user updates the scheduled agent via `/schedule`), not unfinished code.

**Type consistency:**

- Story schema `locations[]` and `external_map_link` are used consistently in extract_today.py (Task 1), the day-file structure (Task 2), the render JS (Tasks 7, 9), and the daily-task contract documentation.
- Day-file fields `date`, `top_story_id`, `sections[].title`, `sections[].story_ids[]`, `ongoing_story_ids`, `watch_list`, `live_sources` — all referenced with the same names in extract_today.py, render_brief.py, and the render JS.
- Function names match across tasks: `wrapMatchInCard`, `appendHeadlineChip`, `openMapFor`, `closeMap`, `renderItem`, `hydrateStoryTriggers`, `applyFilter`, `renderFollowPanel`, etc. — all carry forward from the existing story-maps implementation.

**Sequencing risk:** The riskiest commit is Task 13 (cutover). Before it, the live site is unaffected. After it, if a parity bug slips through, the fix is `git revert <SHA>` to restore the old HTML page; the JSON corpus, scripts, and validation are all safe to leave in place.
