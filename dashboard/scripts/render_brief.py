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
