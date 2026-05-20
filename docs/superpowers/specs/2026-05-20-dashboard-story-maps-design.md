# Dashboard story maps — design

**Date:** 2026-05-20
**Scope:** Add clickable, inline mini-maps to story cards on `dashboard/index.html`. Identify the geographic anchor in each story and let the reader click an address (or a 📍 chip) to expand a small Leaflet map showing that location, without leaving the dashboard.

## Goal

Make the dashboard's economic-development stories spatially legible. The stories already reference real places — "28 N. Erie St", the Vistula riverfront, four downtown parks, a 38-block RAISE redevelopment area — but those are only words on a page. Surfacing them on a map turns "where is that?" into one click.

This complements (does not replace) the root `index.html` Vibrancy grant map. The top story links to that map; everything else gets a per-card inline mini-map.

## Non-goals

- Live geocoding service. All coordinates are curated and hardcoded.
- Editing existing copy. Address text in stories stays as written; we wrap it.
- Map persistence (open map state across reloads, deep links to a specific story's map).
- Maps on the daily markdown archive pages.

## Architecture

Single static HTML file (`dashboard/index.html`), no build step, no framework — consistent with the rest of the project.

- **Leaflet 1.9.4** added to `<head>` via the same CDN URLs used by the root map. Eager load. ~50KB gzipped CSS+JS. Acceptable on an interactive dashboard.
- **Data:** A `STORY_LOCATIONS` object at the bottom of the existing dashboard `<script>` block, keyed by `data-story-id` (the same IDs the follow system already uses).
- **Hydration:** On init, for each `.story-item`, look up its locations and:
  - For each location whose `match` string appears in the story body text, wrap that text in a `<button class="addr-link">` toggle.
  - For each location with `match: null` (address not in prose), append a 📍 chip near the headline.
  - For the top story (`vibrancy-19-grants`), append an "→ View 17 properties on the Vibrancy map" link to its source row instead of any mini-map.
- **Mini-map:** A hidden `<div class="story-map">` slot is appended to each card with at least one local location. Clicking a trigger toggles `.story-map.open`, which expands via CSS transition. Leaflet is **lazy-instantiated per card** on first open and then reused (calling `invalidateSize()` after the transition).

### Data shape

```js
const STORY_LOCATIONS = {
  "huron-yards-phase-two": {
    points: [
      { label: "28 N. Erie St", match: "28 N. Erie St", lat: 41.6516, lon: -83.5395 }
    ]
  },
  "connectoledo-music-grant": {
    points: [
      { label: "Promenade Park",        match: "Promenade Park",        lat: ..., lon: ... },
      { label: "Glass City Metropark",  match: "Glass City Metropark",  lat: ..., lon: ... },
      { label: "Junction Park",         match: "Junction Park",         lat: ..., lon: ... },
      { label: "Danny Thomas Park",     match: "Danny Thomas Park",     lat: ..., lon: ... }
    ]
  },
  "raise-uptown-junction": {
    polygon: {
      label: "13th–21st St, Adams to Monroe",
      match: "13th–21st Street, Adams to Monroe",
      bbox: [[lat_sw, lon_sw], [lat_ne, lon_ne]]
    }
  },
  "owens-corning-250m": {
    points: [
      { label: "Owens Corning HQ", match: null, lat: ..., lon: ... }
    ]
  },
  "vistula-metropark": {
    line: {
      label: "Water St (Olive to Magnolia)",
      match: "Water Street between Olive and Magnolia",
      path: [[lat1, lon1], [lat2, lon2]]
    }
  },
  // ...
  "vibrancy-19-grants": { externalMap: "../index.html" }
};
```

Each card uses one shared mini-map instance. For multi-point stories (4 parks), clicking a different inline link recenters the **same** mini-map instead of opening four separate maps.

## UX

- **Mini-map slot.** Fixed height ~220px desktop, ~180px mobile. CSS height transition on open/close.
- **Map content:**
  - Single point → marker centered, zoom 16.
  - Multi-point → markers + `fitBounds` with padding.
  - Polygon → translucent rectangle (`L.rectangle`, `weight: 1, fillOpacity: 0.15`) + centroid label marker, `fitBounds` to it.
  - Line → polyline + `fitBounds` to it.
  - Each marker carries a tooltip with the location label.
- **Basemap:** CARTO Voyager (same as the root map) — visual continuity.
- **"Open in Google Maps ↗" link** in the mini-map's bottom-right corner, using `https://www.google.com/maps?q=<lat>,<lon>` — escape hatch for directions/street view.
- **Address link styling:** pin-blue (`#1a4d8c`), dotted underline (matching `.sources-inline a`), tiny 📍 prefix glyph. Hover deepens the underline.
- **Headline chip styling:** existing `.tag` pill idiom + 📍 prefix, pin-blue.
- **Close gestures:** click the trigger again, or press Escape with focus inside that card.
- **Accessibility:** triggers are `<button>` (not `<a>`); `aria-expanded` flips on toggle; the map div gets `aria-label="Map of <location label>"`.

## Coverage

| Story | Locations | Trigger | Notes |
|---|---|---|---|
| `vibrancy-19-grants` (top) | (link out) | "→ View 17 properties on the Vibrancy map" link in source row | Opens `../index.html` new tab. No mini-map. |
| `huron-yards-phase-two` | 28 N. Erie St | Inline link | Warehouse District. |
| `port-warehouse-liquid-terminal` | Toledo-Lucas County Port Authority HQ | 📍 headline chip | Address not in prose. |
| `ostrich-towne-tenants` | Ostrich Towne district centroid | Inline link on "Ostrich Towne" | Vistula. |
| `vistula-metropark` | Water St (Olive to Magnolia) — polyline | Inline link | Line, not point. |
| `soccer-stadium-vistula` | Vistula riverfront, across from Glass City Metropark | Inline link on "Vistula riverfront" | Label notes "proposed". |
| `raise-uptown-junction` | 13th–21st St, Adams to Monroe — polygon | Inline link | Translucent rectangle. |
| `owens-corning-250m` | Owens Corning World HQ (1 Owens Corning Pkwy) | 📍 headline chip | Address not in prose. |
| `connectoledo-music-grant` | 4 parks | Inline link on each park name | fitBounds to all 4. |
| `mind-and-soul-gallery` | Gardner Building (506 Madison Ave) | Inline link | |
| `small-business-app-growth` | — | none | Citywide framing, no location. |
| `promedica-medical-mutual` | — | none | No specific location. |

10 of 12 stories get maps. Top story is link-out only.

## Geocoding source

- For locations already on the root Vibrancy map, reuse the lat/lon from `index.html`'s `properties` array (verbatim, so they stay in sync if the root data is corrected).
- For known landmarks (parks, Owens Corning HQ, Gardner Building, Port Authority), use coordinates from public sources (City of Toledo, Metroparks). Cite each in a code comment.
- For vague locations (Ostrich Towne centroid, Vistula soccer site, RAISE polygon bbox), hand-pick from the City's published maps and cite the source URL in a code comment.

## Error handling

- **Leaflet CDN failure:** click handler detects `typeof L === 'undefined'` and opens Google Maps for that location in a new tab. No console errors, no broken UI.
- **Story ID not in `STORY_LOCATIONS`:** no triggers injected. Silent — that story simply has no map.
- **`match` string not found in story body:** location is rendered as a 📍 headline chip instead of an inline link. Locations are never silently dropped.
- **Tile failure:** handled by Leaflet. CARTO Voyager has been reliable for the root map's lifetime.

## Testing

Manual, in a browser. No automated tests (consistent with the rest of the project).

1. Open `dashboard/index.html` from `file://`. 10 stories show a trigger; 2 don't.
2. Click each inline address link → mini-map expands, marker correct, Google Maps link works.
3. Click the same trigger again → collapses.
4. Click a chip → same behavior.
5. Multi-site (ConnecToledo): clicking each of the 4 park names recenters the shared mini-map, doesn't open four maps.
6. Polygon (RAISE): rectangle visible, fitBounds covers the 38 blocks.
7. Top story link opens `../index.html` in a new tab.
8. Mobile width (≤600px): mini-map narrower, no horizontal overflow.
9. Keyboard: Tab to trigger, Enter opens, Esc closes.
10. Throttled network: Leaflet still loads within a few seconds; click queue behaves.

## Out-of-scope follow-ups (don't do now)

- Deep links: `?story=huron-yards-phase-two&map=1` to open a specific card's map on load.
- Mini-map for stories added in future daily briefs without coordinates yet — they just won't get a trigger until coordinates are added to `STORY_LOCATIONS`.
- Persisting which maps are open across reloads.
