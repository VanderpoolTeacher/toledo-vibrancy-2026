# Dashboard Story Maps Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add inline mini-maps to story cards on `dashboard/index.html`. Clicking an address in the prose (or a 📍 chip near the headline) expands a small Leaflet map for that location inside the card.

**Architecture:** Single static HTML file. Eager-load Leaflet 1.9.4 from CDN. Hardcoded `STORY_LOCATIONS` JS object keyed by `data-story-id`. Lazy-init one Leaflet map per card on first open; reuse on subsequent opens. CARTO Voyager basemap to match the root Vibrancy map.

**Tech Stack:** Vanilla JS, Leaflet 1.9.4, CARTO Voyager tiles. No build step, no framework, no automated tests (consistent with the rest of this project).

**Source spec:** `docs/superpowers/specs/2026-05-20-dashboard-story-maps-design.md`

**Project convention reminders:**
- One file: every change in `dashboard/index.html`.
- No automated tests: each task's verification is "open the page and confirm X in the browser."
- Small commits per task — match the existing commit cadence in `git log`.

---

## File Structure

Only one file is modified throughout this plan:

- **Modify:** `dashboard/index.html`
  - Add Leaflet `<link>` + `<script>` in `<head>` (Task 2)
  - Add CSS rules inside the existing `<style>` block (Task 3)
  - Add a `STORY_LOCATIONS` constant and hydration/toggle JS at the bottom of the existing IIFE script (Tasks 4–10)

No other files are touched.

---

## Task 1: Gather and verify coordinates

**Goal:** Produce a verified coordinate table that Task 4 will paste into `STORY_LOCATIONS`. No code change yet — this is the data-gathering step.

**Files:** none modified — produces an in-plan table the engineer pastes in Task 4.

**Sources of truth:**
- Vibrancy properties already on the root map: reuse `properties` array from `/index.html` lines 271–425.
- Toledo Metroparks page for parks: <https://metroparkstoledo.com/explore-your-parks/>
- City of Toledo RAISE page for polygon bbox: <https://toledo.oh.gov/raise>
- Google Maps for known landmarks (open street view to confirm parcel).

- [ ] **Step 1.1: Start with best-effort coordinates below.** Each will be verified in Step 1.2.

   ```
   # Format: <story id> | <label> | <lat> | <lon> | <source URL>

   huron-yards-phase-two | 28 N. Erie St | 41.6493 | -83.5379 | https://maps.google.com/?q=28+N+Erie+St+Toledo+OH
   port-warehouse-liquid-terminal | Toledo-Lucas County Port Authority HQ (One Maritime Plaza) | 41.6526 | -83.5305 | https://www.toledoport.org
   ostrich-towne-tenants | Ostrich Towne (Vistula warehouse district) | 41.6610 | -83.5380 | https://ostrichtowne.com/
   soccer-stadium-vistula | Proposed Vistula riverfront stadium site | 41.6539 | -83.5215 | https://maps.google.com (riverfront, across from Glass City Metropark)
   owens-corning-250m | Owens Corning World HQ, 1 Owens Corning Pkwy | 41.6438 | -83.5375 | https://maps.google.com/?q=1+Owens+Corning+Pkwy+Toledo+OH
   mind-and-soul-gallery | Gardner Building, 506 Madison Ave | 41.6522 | -83.5377 | https://maps.google.com/?q=506+Madison+Ave+Toledo+OH

   # ConnecToledo music series — 4 parks
   connectoledo-music-grant.promenade  | Promenade Park, 400 Water St | 41.6479 | -83.5343 | https://maps.google.com/?q=Promenade+Park+Toledo+OH
   connectoledo-music-grant.glasscity  | Glass City Metropark, 1300 Front St | 41.6499 | -83.5236 | https://metroparkstoledo.com/glass-city-metropark/
   connectoledo-music-grant.junction   | Junction Park (Junction Ave / Nebraska Ave area) | 41.6411 | -83.5611 | https://maps.google.com/?q=Junction+Park+Toledo+OH
   connectoledo-music-grant.dthomas    | Danny Thomas Park | 41.6589 | -83.5444 | https://maps.google.com/?q=Danny+Thomas+Park+Toledo+OH

   # Polyline: Vistula Metropark — Water St between Olive and Magnolia
   vistula-metropark.olive    | Water St & Olive St | 41.6647 | -83.5320 | https://maps.google.com (intersection)
   vistula-metropark.magnolia | Water St & Magnolia St | 41.6663 | -83.5310 | https://maps.google.com (intersection)

   # Polygon: RAISE 38-block area, 13th–21st St × Adams–Monroe
   raise-uptown-junction.sw | SW corner: 13th St & Monroe St | 41.6537 | -83.5520 | https://maps.google.com
   raise-uptown-junction.ne | NE corner: 21st St & Adams St | 41.6580 | -83.5610 | https://maps.google.com
   ```

- [ ] **Step 1.2: Verify each coordinate.** For each row above, paste the lat/lon into <https://www.google.com/maps?q=LAT,LON> and confirm the pin lands on the named parcel/intersection. If off by more than ~50 meters for a precise point (or the corner is wrong for a polygon corner), adjust the value to the verified one. Note the corrected value back in this table.

- [ ] **Step 1.3: Cross-check the Vibrancy 17.** The top story (`vibrancy-19-grants`) does NOT need a mini-map — only a link out. Confirm no coordinate work is required for it.

- [ ] **Step 1.4: Commit the verified table as a reference file** (so the next task can grep it; also a paper trail).

   Create `dashboard/coords-source.md` with the verified table from 1.1 plus a one-line header. Then:

   ```bash
   git add dashboard/coords-source.md
   git commit -m "Add verified coordinate sources for dashboard story maps"
   ```

---

## Task 2: Load Leaflet on the dashboard

**Goal:** Make `L` (Leaflet's global) available on `dashboard/index.html`. No visible change yet.

**Files:**
- Modify: `dashboard/index.html` (head, lines 3–8 area)

- [ ] **Step 2.1: Add Leaflet CSS + JS to `<head>`**, immediately after the existing `<title>` and `<meta name="description">` lines. Use the same CDN URLs and SRI hashes as the root map (`/index.html` lines 7–8 — paste verbatim to avoid drift).

   Insert after line 7 of `dashboard/index.html`:

   ```html
   <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">
   <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
   ```

- [ ] **Step 2.2: Verify Leaflet loads.** Open `dashboard/index.html` from `file://` in a browser. Open devtools console and run:

   ```js
   L.version
   ```

   Expected output: `"1.9.4"`. If undefined, the script tag is wrong — check the URL and the `crossorigin` attribute.

- [ ] **Step 2.3: Commit.**

   ```bash
   git add dashboard/index.html
   git commit -m "Load Leaflet on the dashboard"
   ```

---

## Task 3: Add CSS for mini-maps, address links, and headline chips

**Goal:** Style hooks ready before behavior is wired. After this task, you can manually add a fake `.story-map.open` div to a card and see the right shape — but nothing is interactive yet.

**Files:**
- Modify: `dashboard/index.html` (inside the existing `<style>` block, before the closing `</style>` near line 211)

- [ ] **Step 3.1: Append these rules inside the existing `<style>` block** (just before `@media (max-width: 600px)`):

   ```css
   /* Inline address links inside story text */
   .addr-link {
     font-family: inherit; font-size: inherit; line-height: inherit;
     background: transparent; border: none; padding: 0; cursor: pointer;
     color: #1a4d8c; border-bottom: 1px dotted #1a4d8c;
     padding-bottom: 1px; text-align: inherit;
   }
   .addr-link::before {
     content: "📍"; font-size: 0.85em; margin-right: 3px;
     filter: grayscale(0.2);
   }
   .addr-link:hover { border-bottom-style: solid; }
   .addr-link[aria-expanded="true"] {
     background: #eaf1f9; border-radius: 3px; padding: 0 4px;
   }

   /* Headline chip for stories whose address isn't in the prose */
   .headline-loc-chip {
     display: inline-flex; align-items: center; gap: 4px;
     font-family: inherit; background: #eaf1f9; border: 1px solid #c5d6ea;
     color: #1a4d8c; padding: 2px 9px; border-radius: 12px;
     font-size: 11px; font-weight: 600; cursor: pointer;
     margin-top: 4px;
   }
   .headline-loc-chip::before { content: "📍"; font-size: 11px; }
   .headline-loc-chip:hover { background: #d8e6f4; }
   .headline-loc-chip[aria-expanded="true"] { background: #d8e6f4; }

   /* Mini-map slot — collapsed by default, expands on .open */
   .story-map {
     height: 0; overflow: hidden;
     transition: height 0.22s ease;
     margin-top: 0; border-radius: 6px;
     position: relative;
   }
   .story-map.open {
     height: 220px;
     margin-top: 12px;
     border: 1px solid #d8d8d3;
   }
   .story-map .leaflet-container { height: 100%; width: 100%; border-radius: 6px; }

   /* "Open in Google Maps" escape hatch on each mini-map */
   .story-map .gmaps-link {
     position: absolute; right: 8px; bottom: 8px; z-index: 500;
     background: rgba(255,255,255,0.92); color: #1a4d8c;
     border: 1px solid #c5d6ea; border-radius: 4px;
     font-size: 11px; padding: 3px 8px; text-decoration: none;
   }
   .story-map .gmaps-link:hover { background: #fff; }

   /* "View 17 properties on the Vibrancy map" external link on top story */
   .top-story .vibrancy-map-link {
     display: inline-block; margin-top: 10px; padding: 6px 12px;
     background: #1a4d8c; color: #fff; border-radius: 4px;
     text-decoration: none; font-size: 13px; font-weight: 600;
   }
   .top-story .vibrancy-map-link:hover { background: #0f3a73; }
   ```

- [ ] **Step 3.2: Append a mobile rule inside the existing `@media (max-width: 600px)` block** (around line 184):

   ```css
   .story-map.open { height: 180px; margin-top: 10px; }
   ```

- [ ] **Step 3.3: Quick shape check.** Open the dashboard. Open devtools, pick any story card, and run in the console:

   ```js
   const card = document.querySelector('.story-item');
   const div = document.createElement('div');
   div.className = 'story-map open';
   div.style.background = '#eee';
   card.appendChild(div);
   ```

   Expected: a 220px tall grey box appears at the bottom of that card. Remove it (or refresh) before continuing.

- [ ] **Step 3.4: Commit.**

   ```bash
   git add dashboard/index.html
   git commit -m "Add CSS for story mini-maps, address links, and chips"
   ```

---

## Task 4: Add the STORY_LOCATIONS data

**Goal:** Add the hardcoded location data the rest of the JS will consume. No behavior change yet — just data.

**Files:**
- Modify: `dashboard/index.html` (inside the existing IIFE `<script>` block at the bottom; insert near the top of the IIFE, after the existing `const STORAGE_KEY` / `FILTER_KEY` declarations around line 449)

- [ ] **Step 4.1: Insert the `STORY_LOCATIONS` object** immediately after `const REPO_FOLLOW_FILE = 'followed_stories.json';` (around line 451):

   Use the verified coordinates from Task 1, Step 1.2 (replacing the best-effort values below with any corrections you made).

   ```js
   // Geocoded locations referenced in each story. Coordinates verified against
   // sources listed in dashboard/coords-source.md.
   //   - `points`: array of single markers
   //   - `polygon.bbox`: [[lat_sw, lon_sw], [lat_ne, lon_ne]]
   //   - `line.path`:   [[lat1, lon1], [lat2, lon2], ...]
   //   - `match`: substring in the story body to convert to an inline link.
   //              If null, a headline chip is rendered instead.
   //   - `externalMap`: top-story-only — render an outbound link, no Leaflet.
   const STORY_LOCATIONS = {
     "vibrancy-19-grants": {
       externalMap: { href: "../index.html", label: "View all 17 properties on the Vibrancy map" }
     },
     "huron-yards-phase-two": {
       points: [{ label: "28 N. Erie St", match: "28 N. Erie St.", lat: 41.6493, lon: -83.5379 }]
     },
     "port-warehouse-liquid-terminal": {
       points: [{ label: "Toledo-Lucas County Port Authority", match: null, lat: 41.6526, lon: -83.5305 }]
     },
     "ostrich-towne-tenants": {
       points: [{ label: "Ostrich Towne (Vistula)", match: "Ostrich Towne", lat: 41.6610, lon: -83.5380 }]
     },
     "vistula-metropark": {
       line: {
         label: "Water St (Olive to Magnolia)",
         match: "Water Street between Olive and Magnolia",
         path: [[41.6647, -83.5320], [41.6663, -83.5310]]
       }
     },
     "soccer-stadium-vistula": {
       points: [{ label: "Proposed stadium — Vistula riverfront", match: "Vistula riverfront", lat: 41.6539, lon: -83.5215 }]
     },
     "raise-uptown-junction": {
       polygon: {
         label: "RAISE area — 13th–21st St × Adams–Monroe",
         match: "13th–21st Street, Adams to Monroe",
         bbox: [[41.6537, -83.5520], [41.6580, -83.5610]]
       }
     },
     "owens-corning-250m": {
       points: [{ label: "Owens Corning HQ", match: null, lat: 41.6438, lon: -83.5375 }]
     },
     "connectoledo-music-grant": {
       points: [
         { label: "Promenade Park",        match: "Promenade Park",        lat: 41.6479, lon: -83.5343 },
         { label: "Glass City Metropark",  match: "Glass City Metropark",  lat: 41.6499, lon: -83.5236 },
         { label: "Junction Park",         match: "Junction Park",         lat: 41.6411, lon: -83.5611 },
         { label: "Danny Thomas Park",     match: "Danny Thomas Park",     lat: 41.6589, lon: -83.5444 }
       ]
     },
     "mind-and-soul-gallery": {
       points: [{ label: "Gardner Building (506 Madison Ave)", match: "Gardner Building", lat: 41.6522, lon: -83.5377 }]
     }
   };
   ```

- [ ] **Step 4.2: Verify the data parses.** Reload the dashboard. In the console:

   ```js
   Object.keys(STORY_LOCATIONS).length
   ```

   Expected: `10`.

- [ ] **Step 4.3: Commit.**

   ```bash
   git add dashboard/index.html
   git commit -m "Add STORY_LOCATIONS data for dashboard story maps"
   ```

---

## Task 5: Hydrate triggers (inline links + headline chips)

**Goal:** Every applicable story now shows clickable address links inside its prose (and chips near the headline for stories whose address isn't in the prose). Clicks don't open anything yet — that's Task 6.

**Files:**
- Modify: `dashboard/index.html` (inside the existing IIFE, add new functions; wire them into `init()` around line 711)

- [ ] **Step 5.1: Add the hydration function** to the IIFE, just before the `(async function init(){ ... })();` block:

   ```js
   // Wrap a substring inside a card's textual content with a clickable button.
   // Walks text nodes inside the card's <p> and .why elements so we don't disturb
   // other elements (tags, sources, people chips).
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
         return btn; // wrap only the first occurrence
       }
     }
     return null;
   }

   // Append a headline chip for a location whose address isn't in the prose.
   function appendHeadlineChip(card, label, onClick) {
     const chip = document.createElement('button');
     chip.type = 'button';
     chip.className = 'headline-loc-chip';
     chip.textContent = label;
     chip.setAttribute('aria-expanded', 'false');
     chip.addEventListener('click', e => { e.stopPropagation(); onClick(chip); });
     // Slip it right under the story header (or h2 for top story)
     const header = card.querySelector('.story-header') || card.querySelector('h2');
     if (header) header.insertAdjacentElement('afterend', chip);
     return chip;
   }

   // Hydrate every story's triggers, but don't wire opening yet — Task 6 fills in onClick.
   function hydrateStoryTriggers() {
     document.querySelectorAll('.story-item').forEach(card => {
       const id = card.dataset.storyId;
       const loc = STORY_LOCATIONS[id];
       if (!loc) return;
       if (loc.externalMap) return; // handled in Task 9
       const items = collectLocationItems(loc);
       items.forEach(item => {
         const onClick = (trigger) => openMapFor(card, item, trigger);
         let trigger = null;
         if (item.match) trigger = wrapMatchInCard(card, item.match, onClick);
         if (!trigger) trigger = appendHeadlineChip(card, item.label, onClick);
       });
     });
   }

   // Flatten a STORY_LOCATIONS entry into a uniform list of {label, match, shape, ...}.
   function collectLocationItems(loc) {
     const out = [];
     if (loc.points) loc.points.forEach(p => out.push({ shape: 'point', ...p }));
     if (loc.line)   out.push({ shape: 'line',    ...loc.line });
     if (loc.polygon) out.push({ shape: 'polygon', ...loc.polygon });
     return out;
   }

   // Placeholder for Task 6 — leaves chips/links inert for now.
   function openMapFor(_card, _item, _trigger) { /* TODO Task 6 */ }
   ```

- [ ] **Step 5.2: Wire `hydrateStoryTriggers()` into init.** Edit the existing init IIFE (around line 711) to call it after the existing setup:

   ```js
   (async function init(){
     await loadAuthorFollows();
     renderAuthorBadges();
     renderPersonChips();
     renderStoryFollowState();
     renderFollowPanel();
     hydrateStoryTriggers();   // <-- add this line
     applyFilter();
   })();
   ```

- [ ] **Step 5.3: Verify in the browser.** Reload `dashboard/index.html` and confirm visually:

   - The Huron Yards card shows "📍 28 N. Erie St." as a dotted-underline link in the prose.
   - The Owens Corning card shows a "📍 Owens Corning HQ" chip right under the headline.
   - The ConnecToledo card shows 4 dotted-underline links (Promenade Park, Glass City Metropark, Junction Park, Danny Thomas Park).
   - The top story has NO new affordance yet (Task 9 adds the external link).
   - Clicking any of these does nothing — that's expected for now.
   - The 2 non-geographic stories (Small Business growth, ProMedica) have no new affordances.

- [ ] **Step 5.4: Commit.**

   ```bash
   git add dashboard/index.html
   git commit -m "Hydrate clickable address links and headline chips on story cards"
   ```

---

## Task 6: Implement toggle + lazy Leaflet init for single-point stories

**Goal:** Clicking an address link or chip opens an inline mini-map with a marker. Closes on second click. Multi-point stories (4 parks) recenter the same map.

**Files:**
- Modify: `dashboard/index.html` (replace the placeholder `openMapFor` from Task 5)

- [ ] **Step 6.1: Add a per-card map registry, Leaflet builder, and the real `openMapFor`.** Replace the placeholder `openMapFor` (and add the helpers below it) inside the IIFE:

   ```js
   // Per-card map state, keyed by data-story-id.
   //   { mapDiv, map, layer, currentTrigger }
   const cardMaps = new Map();

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
       scrollWheelZoom: false  // wheel zoom on a small card is disorienting
     }).setView([41.6528, -83.5379], 13);
     L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
       attribution: '&copy; OpenStreetMap, &copy; CARTO',
       subdomains: 'abcd', maxZoom: 19
     }).addTo(map);
     // Click to re-enable wheel zoom (Leaflet UX best practice for inline maps)
     map.on('click', () => map.scrollWheelZoom.enable());
     return map;
   }

   function clearOverlay(state) {
     if (state.layer) { state.layer.remove(); state.layer = null; }
   }

   function renderItem(state, item) {
     clearOverlay(state);
     if (item.shape === 'point') {
       const m = L.marker([item.lat, item.lon]).bindTooltip(item.label);
       m.addTo(state.map);
       state.layer = m;
       state.map.setView([item.lat, item.lon], 16, { animate: true });
       updateGmapsLink(state.mapDiv, item.lat, item.lon);
     }
     // Task 8 fills in 'line' and 'polygon' branches
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
     const id = card.dataset.storyId;
     let state = cardMaps.get(id);

     // Toggle off if the same trigger was already active
     if (state && state.currentTrigger === trigger && state.mapDiv.classList.contains('open')) {
       closeMap(card);
       return;
     }

     const mapDiv = ensureMapContainer(card);
     if (!state) {
       state = { mapDiv, map: null, layer: null, currentTrigger: null };
       cardMaps.set(id, state);
     }

     // Reset aria on previous trigger (if any)
     if (state.currentTrigger && state.currentTrigger !== trigger) {
       state.currentTrigger.setAttribute('aria-expanded', 'false');
     }
     state.currentTrigger = trigger;
     trigger.setAttribute('aria-expanded', 'true');

     mapDiv.classList.add('open');

     // Lazy-init Leaflet on first open for this card
     const initMap = () => {
       if (!state.map) state.map = buildLeafletMap(mapDiv);
       state.map.invalidateSize();
       renderItem(state, item);
     };
     // Wait for the CSS height transition before invalidateSize, otherwise
     // Leaflet measures a 0-height container and tiles never load.
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
   ```

- [ ] **Step 6.2: Verify single-point stories.** Reload the dashboard.

   - Click "📍 28 N. Erie St." on Huron Yards → a 220px tall map slides open with a marker pin and Voyager tiles.
   - Click the same link again → the map collapses.
   - Click the "Owens Corning HQ" chip → map opens with the marker on the HQ parcel.
   - Hover the marker → tooltip shows the label.
   - Click "Open in Google Maps ↗" in the corner → opens Google Maps in a new tab at those coords.
   - Mind & Soul, Soccer Stadium, Ostrich Towne, Port Authority: all open correctly.

- [ ] **Step 6.3: Verify multi-point recenter on ConnecToledo.**

   - On the ConnecToledo card, click "Promenade Park" → map opens, marker on Promenade.
   - Without closing, click "Junction Park" → the SAME map (the existing open one) pans/zooms to Junction Park, marker moves. No second map appears.
   - Click "Junction Park" a second time → the map closes (toggle-off behavior).

- [ ] **Step 6.4: Commit.**

   ```bash
   git add dashboard/index.html
   git commit -m "Open inline mini-maps on address-link clicks"
   ```

---

## Task 7: Polygon and polyline support

**Goal:** RAISE 38-block area renders as a translucent rectangle. Vistula Metropark renders as a polyline along Water St.

**Files:**
- Modify: `dashboard/index.html` (extend the `renderItem` function from Task 6)

- [ ] **Step 7.1: Extend `renderItem`** with `line` and `polygon` branches. Replace the existing `renderItem` from Task 6 with:

   ```js
   function renderItem(state, item) {
     clearOverlay(state);
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
   ```

- [ ] **Step 7.2: Verify polyline on Vistula Metropark card.** Click "Water Street between Olive and Magnolia" → map opens, a thick blue line runs along Water St between the two intersections. fitBounds frames the whole segment with padding.

- [ ] **Step 7.3: Verify polygon on RAISE card.** Click "13th–21st Street, Adams to Monroe" → map opens, a translucent blue rectangle covers the 38-block area. fitBounds frames it.

- [ ] **Step 7.4: Commit.**

   ```bash
   git add dashboard/index.html
   git commit -m "Render polylines and polygons on story mini-maps"
   ```

---

## Task 8: Top-story external link

**Goal:** The Vibrancy 19 top story gets an "→ View all 17 properties on the Vibrancy map" button that opens `../index.html` in a new tab. No mini-map.

**Files:**
- Modify: `dashboard/index.html` (extend `hydrateStoryTriggers` to handle the `externalMap` branch)

- [ ] **Step 8.1: Extend `hydrateStoryTriggers`** to render the external link. Replace the function with:

   ```js
   function hydrateStoryTriggers() {
     document.querySelectorAll('.story-item').forEach(card => {
       const id = card.dataset.storyId;
       const loc = STORY_LOCATIONS[id];
       if (!loc) return;
       if (loc.externalMap) {
         renderExternalMapLink(card, loc.externalMap);
         return;
       }
       const items = collectLocationItems(loc);
       items.forEach(item => {
         const onClick = (trigger) => openMapFor(card, item, trigger);
         let trigger = null;
         if (item.match) trigger = wrapMatchInCard(card, item.match, onClick);
         if (!trigger) trigger = appendHeadlineChip(card, item.label, onClick);
       });
     });
   }

   function renderExternalMapLink(card, ext) {
     const a = document.createElement('a');
     a.className = 'vibrancy-map-link';
     a.href = ext.href;
     a.target = '_blank';
     a.rel = 'noopener';
     a.textContent = '→ ' + ext.label;
     const sources = card.querySelector('.sources-inline');
     if (sources) sources.insertAdjacentElement('afterend', a);
     else card.appendChild(a);
   }
   ```

- [ ] **Step 8.2: Verify.** Reload the dashboard. The top story now shows a blue pill-button beneath its source links: "→ View all 17 properties on the Vibrancy map". Click it → opens `index.html` (the root Vibrancy map) in a new tab.

- [ ] **Step 8.3: Commit.**

   ```bash
   git add dashboard/index.html
   git commit -m "Link top story to the root Vibrancy map"
   ```

---

## Task 9: Error handling and accessibility

**Goal:** Graceful fallback when Leaflet fails to load. Esc closes the open map for the focused card. Aria already wired in Task 6 — verify it.

**Files:**
- Modify: `dashboard/index.html` (extend `openMapFor` and add a keydown listener)

- [ ] **Step 9.1: Replace `openMapFor` with a Leaflet-availability check** at the top:

   ```js
   function openMapFor(card, item, trigger) {
     // If Leaflet failed to load (CDN failure), bail out to Google Maps.
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
   ```

- [ ] **Step 9.2: Add Esc-to-close at the document level.** Append just before the `(async function init(){ ... })();` block:

   ```js
   document.addEventListener('keydown', e => {
     if (e.key !== 'Escape') return;
     const focused = document.activeElement;
     if (!focused) return;
     const card = focused.closest('.story-item');
     if (!card) return;
     closeMap(card);
   });
   ```

- [ ] **Step 9.3: Verify Leaflet-fallback.** In devtools console BEFORE reloading:

   ```js
   // Block Leaflet from loading
   document.querySelectorAll('script[src*="leaflet"]').forEach(s => s.remove());
   delete window.L;
   ```

   Then click an address link in any story. Expected: a new tab opens to Google Maps at that location. No console errors. The dashboard UI remains usable.

- [ ] **Step 9.4: Verify Esc-to-close.** Reload (so Leaflet loads). Click an address to open a map, then with focus inside the card (the address button is still focused), press Esc → the map collapses, aria-expanded flips to false.

- [ ] **Step 9.5: Verify aria-expanded.** With the map closed, the trigger has `aria-expanded="false"`. Open the map → `aria-expanded="true"` on that trigger only. Open a different trigger on the same card (ConnecToledo's 4 parks) → previous trigger flips back to `false`, new one is `true`.

- [ ] **Step 9.6: Commit.**

   ```bash
   git add dashboard/index.html
   git commit -m "Handle Leaflet load failure and Esc-to-close on story maps"
   ```

---

## Task 10: Mobile layout verification

**Goal:** Confirm the mini-maps work on mobile widths.

**Files:** none modified (CSS for mobile already added in Task 3).

- [ ] **Step 10.1: Open devtools → toggle device toolbar → set width to 375px (iPhone SE).** Reload.

- [ ] **Step 10.2: Check each story type.**

   - Huron Yards (single point): mini-map opens to 180px tall (mobile rule), no horizontal overflow.
   - ConnecToledo (4 parks): each park link is tappable; clicking a different one recenters.
   - RAISE (polygon): rectangle visible inside the smaller viewport, fitBounds adjusts.
   - Owens Corning (chip): chip is tappable, map opens below.
   - Address links wrap correctly inside paragraphs at narrow widths (no line-overflow).

- [ ] **Step 10.3: If any visual regression appears**, add targeted rules inside the existing `@media (max-width: 600px)` block. (Do NOT commit a separate task for this — fold it into this task's commit.)

- [ ] **Step 10.4: Commit (only if changes were needed).**

   ```bash
   git add dashboard/index.html
   git commit -m "Tighten mobile layout for story mini-maps"
   ```

---

## Task 11: Final verification against the spec's testing checklist

**Goal:** Walk through every item in the spec's testing section and confirm it passes.

**Files:** none modified.

- [ ] **Step 11.1:** Open `dashboard/index.html` from `file://`. 10 stories show a trigger; 2 (small-business-app-growth, promedica-medical-mutual) don't.

- [ ] **Step 11.2:** Click each inline address link → mini-map expands, marker correct, "Open in Google Maps ↗" link works.

- [ ] **Step 11.3:** Click the same trigger again → collapses.

- [ ] **Step 11.4:** Click a chip → same behavior as inline link.

- [ ] **Step 11.5:** Multi-site (ConnecToledo): clicking each of the 4 park names recenters the shared mini-map; doesn't open four separate maps.

- [ ] **Step 11.6:** Polygon (RAISE): rectangle visible, fitBounds covers the 38 blocks.

- [ ] **Step 11.7:** Top story: "→ View all 17 properties on the Vibrancy map" link opens `../index.html` in a new tab.

- [ ] **Step 11.8:** Mobile width (≤600px): mini-map narrower (180px tall), no horizontal overflow.

- [ ] **Step 11.9:** Keyboard: Tab to a trigger, Enter opens, Esc closes.

- [ ] **Step 11.10:** Throttled network (devtools → Network → Slow 3G), hard reload, confirm Leaflet still loads within a few seconds and queued clicks behave correctly.

- [ ] **Step 11.11:** Optional polish if anything looks off (Leaflet attribution placement, font sizing in popups on mobile, marker icon visibility on dark areas of the Voyager basemap). Roll any polish into a single commit.

- [ ] **Step 11.12: Final commit (only if Step 11.11 made changes).**

   ```bash
   git add dashboard/index.html
   git commit -m "Polish from final verification pass"
   ```

- [ ] **Step 11.13: Push to origin/main** (matches the existing dashboard deploy pattern — the live Pages site updates automatically).

   ```bash
   git push origin main
   ```

   Wait 1–2 minutes, then visit <https://vanderpoolteacher.github.io/toledo-vibrancy-2026/dashboard/> and confirm the live site behaves identically to the local file.

---

## Self-review notes

- **Spec coverage:** Architecture/data shape (Task 4) ✓, eager Leaflet load (Task 2) ✓, mini-map UX (Tasks 3, 6) ✓, all 12 stories' coverage (Tasks 4, 5, 7, 8 + Task 11 verification) ✓, geocoding source policy (Task 1) ✓, error handling (Task 9) ✓, accessibility (Tasks 6, 9) ✓, mobile (Tasks 3, 10) ✓.
- **Placeholders:** the only `TODO` in the plan is the Task 5 `openMapFor` placeholder, which is filled in by Task 6 within the same plan — that's a deliberate sequencing artifact, not a planning gap.
- **Type consistency:** the `STORY_LOCATIONS` shape (`points`, `line`, `polygon`, `externalMap`, `match`) is the same in Tasks 4, 5, 6, 7, and 8. The `state` shape `{ mapDiv, map, layer, currentTrigger }` is identical in Tasks 6 and 9. `renderItem` is replaced wholesale in Task 7 (not extended), avoiding a partial-state bug.
