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
