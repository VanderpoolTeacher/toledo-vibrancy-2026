# Story Chain Tracking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the visual layer for per-story update chains to `dashboard/index.html` — a `NEW UPDATE` badge on followed stories that have a fresh chapter, a `See updates (N)` trigger that expands an inline timeline of prior chapters inside the same card.

**Architecture:** Single static HTML file. All CSS added to the existing `<style>` block. All JS added to the existing IIFE in the `<script>` block. Chain data is read from a `STORY_CHAINS` JS constant (a temporary stub for demo while the JSON data layer is built separately per `2026-05-20-stories-as-json-design.md`); the rendering code is structured so swapping the stub for a real `getChainFor(storyId)` is a one-function change later.

**Tech Stack:** Vanilla JS, no framework, no build step. No automated tests (consistent with the rest of this project — verification is manual in a browser).

**Source spec:** `docs/superpowers/specs/2026-05-20-story-chain-tracking-design.md`

**Project convention reminders:**
- One file: every change in `dashboard/index.html`.
- No automated tests: each task's verification is "open the page and confirm X in the browser."
- Small commits per task — match the existing commit cadence in `git log`.

---

## File Structure

Only one file is modified throughout this plan:

- **Modify:** `dashboard/index.html`
  - Add CSS rules inside the existing `<style>` block, near the existing follow styles (Task 1)
  - Add static demo markup inside one story card to visually validate CSS (Task 2)
  - Add `STORY_CHAINS` constant + chain-rendering JS inside the existing IIFE (Tasks 3–6)
  - Wire new render calls into `init()` and `renderStoryFollowState()` (Task 7)

No other files are touched.

---

## Task 1: Add CSS for badge, trigger, and expanded chain

**Goal:** Land the three CSS blocks the visual spec requires, with no markup using them yet. Existing dashboard renders unchanged.

**Files:**
- Modify: `dashboard/index.html` — insert in the `<style>` block, immediately after the existing `.story-date.age-future` rule near line 177.

- [ ] **Step 1.1: Open the file and find the insertion point**

Open `dashboard/index.html`. Locate the existing `.story-date.age-future` rule near line 177:

```css
.story-date.age-future   { background: #e6f0fb; color: #1a4d8c; } /* future event */
```

- [ ] **Step 1.2: Insert the new CSS block immediately after `.story-date.age-future`**

```css
/* ---------- Story chain tracking (see docs/superpowers/specs/2026-05-20-story-chain-tracking-design.md) ---------- */

.story-new-badge {
  background: #d4831f; color: #fff; font-size: 10px; padding: 2px 7px;
  border-radius: 8px; font-weight: 700; letter-spacing: 0.04em;
  text-transform: uppercase; vertical-align: middle; margin-left: 4px;
}

.chain-trigger {
  display: inline-block; margin-top: 10px; padding: 0; border: none;
  background: transparent; font: inherit; cursor: pointer;
}
.chain-trigger.is-followed { font-size: 12px; font-weight: 600; color: #8c6a1a; }
.chain-trigger.is-unfollowed { font-size: 11px; font-weight: 400; color: #888; }
.chain-trigger:hover { text-decoration: underline; }

.chain-expanded { margin-top: 10px; border-top: 1px dotted #e5cba3; padding-top: 10px; }
.chain-expanded[hidden] { display: none; }
.chain-label {
  font-size: 10px; color: #888; text-transform: uppercase;
  letter-spacing: 0.06em; font-weight: 700; margin: 0 0 8px;
}
.chain-list { border-left: 2px solid #d4831f; padding-left: 12px; margin: 0; }
.chain-entry { position: relative; margin-bottom: 10px; }
.chain-entry:last-child { margin-bottom: 0; }
.chain-entry::before {
  content: ""; position: absolute; left: -18px; top: 4px;
  width: 10px; height: 10px; border-radius: 50%; background: #d4831f;
}
.chain-entry .chain-date {
  display: block; font-size: 11px; font-weight: 700;
  color: #8c6a1a; text-transform: uppercase;
}
.chain-entry .chain-headline {
  display: block; font-size: 12px; font-weight: 600; color: #1a1a1a;
}
.chain-entry .chain-snippet {
  display: block; font-size: 11px; color: #666; margin-top: 2px;
}
```

- [ ] **Step 1.3: Verify the page still renders unchanged**

Open `dashboard/index.html` in a browser (double-click the file or use `open dashboard/index.html`). Confirm no visible difference from before — cards look identical, no console errors.

- [ ] **Step 1.4: Commit**

```bash
git add dashboard/index.html
git commit -m "Add CSS for story chain tracking badge, trigger, and timeline"
```

---

## Task 2: Static demo markup on the Soccer Stadium card to verify CSS

**Goal:** Hardcode the badge + trigger + expanded chain HTML on one card so the CSS from Task 1 is visually confirmed before any JS is involved.

**Files:**
- Modify: `dashboard/index.html` — inside the `soccer-stadium-vistula` story card (currently around lines 454–471).

- [ ] **Step 2.1: Find the Soccer Stadium card**

Locate the card. It starts at the line containing:

```html
<div class="story story-item is-ongoing" data-story-id="soccer-stadium-vistula" data-tags="vistula"
```

The card ends at its closing `</div>` (currently line 471), with the `<div class="sources-inline">` block just above the closing tag.

- [ ] **Step 2.2: Add `is-followed` to the card and a `NEW UPDATE` badge into the `<h3>`**

Change the opening `<div>` so the class list begins `class="story story-item is-followed is-ongoing"` — keep all other attributes. Then inside the `<h3>` (the line containing `Soccer stadium proposal …`), append a span immediately after the headline text and before the closing `</h3>`:

```html
<span class="story-new-badge" aria-label="new update available in this brief">New Update</span>
```

- [ ] **Step 2.3: Insert the trigger button and expanded chain block before the card's closing `</div>`**

Immediately after the `<div class="sources-inline">…</div>` block and before the card's closing `</div>`, paste:

```html
<button type="button" class="chain-trigger is-followed"
        aria-expanded="true" aria-controls="chain-soccer-stadium-vistula">
  ▲ Hide updates (3)
</button>
<div class="chain-expanded" id="chain-soccer-stadium-vistula" role="region"
     aria-label="Earlier in this story">
  <p class="chain-label">Earlier in this story</p>
  <ul class="chain-list">
    <li class="chain-entry">
      <span class="chain-date">May 14, 2026</span>
      <span class="chain-headline">Filings reviewed by The Blade clarify proposal</span>
      <span class="chain-snippet">"$83.6M, 7,500-seat stadium on dormant land off Summit Street…"</span>
    </li>
    <li class="chain-entry">
      <span class="chain-date">Apr 18, 2026</span>
      <span class="chain-headline">Group applies for state sports facility fund</span>
      <span class="chain-snippet">"Summit Street Sports and Mud Hens both applied for share of $1B fund…"</span>
    </li>
    <li class="chain-entry">
      <span class="chain-date">Mar 02, 2026</span>
      <span class="chain-headline">Trial-balloon stage</span>
      <span class="chain-snippet">"Dormant land off Summit Street being considered for stadium use…"</span>
    </li>
  </ul>
</div>
```

- [ ] **Step 2.4: Verify in the browser**

Reload `dashboard/index.html`. Find the Soccer Stadium card. Confirm:
- Card has the orange left border + outline (existing `.is-followed` styling — already in place from line 114).
- Headline shows the orange `New Update` pill on the right of the text.
- Below the prose + sources, the `▲ Hide updates (3)` trigger appears in bold orange.
- Below the trigger, the `EARLIER IN THIS STORY` label appears, then a vertical orange rail with three entries: each has an orange dot, date, headline, snippet.
- No console errors.

- [ ] **Step 2.5: Commit**

```bash
git add dashboard/index.html
git commit -m "Add static chain UI demo on Soccer Stadium card to verify CSS"
```

---

## Task 3: Replace static demo with `STORY_CHAINS` data stub

**Goal:** Strip the hardcoded HTML from Task 2 and back the same visual result with a JS data structure. Visual result is identical; the markup is now generated.

**Files:**
- Modify: `dashboard/index.html`
  - Revert the Soccer Stadium card to its original markup (remove badge, trigger, expanded chain — keep `is-followed` for now; it will be controlled by follow state, not hardcoded, after Task 6).
  - Add a `STORY_CHAINS` constant and rendering JS inside the existing IIFE.

- [ ] **Step 3.1: Revert the Soccer Stadium card to its original markup**

Remove the `is-followed` class added in Step 2.2 (the card should be `class="story story-item is-ongoing"` again). Remove the `<span class="story-new-badge">…</span>` from inside the `<h3>`. Remove the `<button class="chain-trigger">…</button>` and `<div class="chain-expanded">…</div>` blocks added in Step 2.3. The card is now byte-identical to its pre-Task-2 state.

- [ ] **Step 3.2: Add `STORY_CHAINS` constant inside the existing IIFE**

Open the `<script>` block. The IIFE begins around line 649 with `(function(){`. Find the existing `STORY_LOCATIONS` constant inside it (search for `STORY_LOCATIONS =` — it's a large object). Immediately above `STORY_LOCATIONS`, add:

```js
// STORY_CHAINS — temporary stub. Replaced by data-layer fetcher once
// docs/superpowers/specs/2026-05-20-stories-as-json-design.md ships.
// Schema: STORY_CHAINS[storyId] = { isFreshChapter: bool, entries: [{date, headline, snippet}, ...] }
// `entries` is ordered most-recent-first. Empty entries array = no prior chain.
const STORY_CHAINS = {
  "soccer-stadium-vistula": {
    isFreshChapter: true,
    entries: [
      { date: "May 14, 2026", headline: "Filings reviewed by The Blade clarify proposal",
        snippet: "\"$83.6M, 7,500-seat stadium on dormant land off Summit Street…\"" },
      { date: "Apr 18, 2026", headline: "Group applies for state sports facility fund",
        snippet: "\"Summit Street Sports and Mud Hens both applied for share of $1B fund…\"" },
      { date: "Mar 02, 2026", headline: "Trial-balloon stage",
        snippet: "\"Dormant land off Summit Street being considered for stadium use…\"" }
    ]
  },
  "vibrancy-19-grants": {
    isFreshChapter: false,
    entries: [
      { date: "May 15, 2026", headline: "Mayor announces 19 awards",
        snippet: "\"$630K to 17 properties across 10 neighborhoods, est. $13.5M leveraged…\"" },
      { date: "Apr 02, 2026", headline: "Application window closes",
        snippet: "\"82 applications submitted across three programs…\"" }
    ]
  }
};

function getChainFor(storyId) {
  return STORY_CHAINS[storyId] || { isFreshChapter: false, entries: [] };
}
```

- [ ] **Step 3.3: Add `renderChainTriggers` function inside the IIFE, just below `renderStoryFollowState` (currently lines 857–868)**

```js
function renderChainTriggers() {
  document.querySelectorAll('.story-item').forEach(card => {
    const id = card.dataset.storyId;
    if (!id) return;
    const chain = getChainFor(id);
    // Remove any previously-rendered trigger + expanded block so this function is idempotent.
    const oldTrigger = card.querySelector(':scope > .chain-trigger');
    const oldExpanded = card.querySelector(':scope > .chain-expanded');
    if (oldTrigger) oldTrigger.remove();
    if (oldExpanded) oldExpanded.remove();
    if (!chain.entries.length) return;

    const isFollowed = card.classList.contains('is-followed');
    const expandedId = 'chain-' + id;

    const trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.className = 'chain-trigger ' + (isFollowed ? 'is-followed' : 'is-unfollowed');
    trigger.setAttribute('aria-expanded', 'false');
    trigger.setAttribute('aria-controls', expandedId);
    trigger.textContent = (isFollowed ? '▼' : '▾') + ' See updates (' + chain.entries.length + ')';

    const expanded = document.createElement('div');
    expanded.className = 'chain-expanded';
    expanded.id = expandedId;
    expanded.setAttribute('role', 'region');
    expanded.setAttribute('aria-label', 'Earlier in this story');
    expanded.setAttribute('aria-live', 'polite');
    expanded.hidden = true;

    const label = document.createElement('p');
    label.className = 'chain-label';
    label.textContent = 'Earlier in this story';
    expanded.appendChild(label);

    const list = document.createElement('ul');
    list.className = 'chain-list';
    chain.entries.forEach(entry => {
      const li = document.createElement('li');
      li.className = 'chain-entry';
      const d = document.createElement('span'); d.className = 'chain-date'; d.textContent = entry.date;
      const h = document.createElement('span'); h.className = 'chain-headline'; h.textContent = entry.headline;
      const s = document.createElement('span'); s.className = 'chain-snippet'; s.textContent = entry.snippet;
      li.appendChild(d); li.appendChild(h); li.appendChild(s);
      list.appendChild(li);
    });
    expanded.appendChild(list);

    card.appendChild(trigger);
    card.appendChild(expanded);
  });
}
```

- [ ] **Step 3.4: Call `renderChainTriggers()` from `init()`**

Find the `init()` IIFE at the bottom of the script (currently starts around line 1189: `(async function init(){`). After the existing `renderStoryFollowState();` call (currently line 1193), add:

```js
    renderChainTriggers();
```

So the init block becomes (relevant lines only):

```js
    renderAuthorBadges();
    renderPersonChips();
    renderStoryFollowState();
    renderChainTriggers();
    renderFollowPanel();
    hydrateStoryTriggers();
```

- [ ] **Step 3.5: Verify in the browser**

Reload `dashboard/index.html`. Confirm:
- Soccer Stadium card now shows a subdued gray `▾ See updates (3)` trigger below sources (card is not yet followed, so styling is the unfollowed variant).
- Vibrancy 19 Grants card shows a subdued gray `▾ See updates (2)` trigger.
- All other cards are unchanged — no trigger.
- No console errors.

- [ ] **Step 3.6: Commit**

```bash
git add dashboard/index.html
git commit -m "Render chain triggers from STORY_CHAINS stub"
```

---

## Task 4: Wire click handler — expand and collapse

**Goal:** Clicking the trigger reveals the chain; clicking again hides it. `aria-expanded` flips; caret swaps `▼` ↔ `▲` (or `▾` ↔ `▴` for the unfollowed variant).

**Files:**
- Modify: `dashboard/index.html` — extend `renderChainTriggers` with a click handler; no other changes.

- [ ] **Step 4.1: Add the click handler inside `renderChainTriggers`**

In `renderChainTriggers` (added in Step 3.3), immediately after the line `card.appendChild(expanded);` and before the closing `});` of the `.forEach`, insert:

```js
    trigger.addEventListener('click', () => {
      const open = trigger.getAttribute('aria-expanded') === 'true';
      const next = !open;
      trigger.setAttribute('aria-expanded', String(next));
      expanded.hidden = !next;
      const downCaret = isFollowed ? '▼' : '▾';
      const upCaret = isFollowed ? '▲' : '▴';
      trigger.textContent = (next ? upCaret : downCaret) + ' '
        + (next ? 'Hide updates (' : 'See updates (')
        + chain.entries.length + ')';
    });
```

- [ ] **Step 4.2: Verify in the browser**

Reload. On the Soccer Stadium card:
- Click `▾ See updates (3)` → trigger flips to `▴ Hide updates (3)`, the chain rail expands below with the three entries, vertical rail and orange dots visible.
- Click again → trigger flips back to `▾ See updates (3)`, chain hides.
- Inspect element on the trigger and confirm `aria-expanded="true"` / `"false"` toggles correctly.

Repeat for the Vibrancy 19 Grants card.

- [ ] **Step 4.3: Commit**

```bash
git add dashboard/index.html
git commit -m "Expand and collapse story chain on trigger click"
```

---

## Task 5: Add `NEW UPDATE` badge for followed stories with a fresh chapter

**Goal:** Define a `renderNewUpdateBadge` function that adds the badge to a card if the story is followed AND `getChainFor(storyId).isFreshChapter` is true. Idempotent — removes any prior badge before deciding whether to re-add.

**Files:**
- Modify: `dashboard/index.html` — add one function inside the IIFE.

- [ ] **Step 5.1: Add the function immediately below `renderChainTriggers` inside the IIFE**

```js
function renderNewUpdateBadge() {
  document.querySelectorAll('.story-item').forEach(card => {
    const id = card.dataset.storyId;
    if (!id) return;
    const old = card.querySelector(':scope .story-new-badge');
    if (old) old.remove();
    const chain = getChainFor(id);
    if (!card.classList.contains('is-followed')) return;
    if (!chain.isFreshChapter) return;
    const headline = card.querySelector('.story-header h3, .top-story h2');
    if (!headline) return;
    const badge = document.createElement('span');
    badge.className = 'story-new-badge';
    badge.setAttribute('aria-label', 'new update available in this brief');
    badge.textContent = 'New Update';
    headline.appendChild(badge);
  });
}
```

- [ ] **Step 5.2: Manual one-time verification by following a story**

Reload the page. Click `☆ Follow` on the Soccer Stadium card. With nothing else wired up yet, no badge appears — because `renderNewUpdateBadge` isn't being called on follow changes. That wiring is the next task. For now just confirm the function exists by opening devtools and running:

```js
renderNewUpdateBadge();
```

The badge should appear next to the Soccer Stadium headline. Click `★ Following` to unfollow, run `renderNewUpdateBadge();` again — badge disappears.

- [ ] **Step 5.3: Commit**

```bash
git add dashboard/index.html
git commit -m "Add renderNewUpdateBadge for followed stories with fresh chapter"
```

---

## Task 6: Re-render chain trigger style and badge when follow state changes

**Goal:** Hook `renderChainTriggers` and `renderNewUpdateBadge` into the existing `renderStoryFollowState` flow so following/unfollowing a story instantly updates both the trigger style (orange vs. gray) and the badge.

**Files:**
- Modify: `dashboard/index.html` — two-line addition inside `renderStoryFollowState`.

- [ ] **Step 6.1: Find `renderStoryFollowState` (currently lines 857–868)**

It currently ends like this:

```js
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
```

- [ ] **Step 6.2: Add the two re-render calls at the end of the function**

Inside the same function body, immediately before the closing `}`, add:

```js
  renderChainTriggers();
  renderNewUpdateBadge();
```

So the function now ends:

```js
    if (card) card.classList.toggle('is-followed', isOn);
  });
  renderChainTriggers();
  renderNewUpdateBadge();
}
```

- [ ] **Step 6.3: Also call `renderNewUpdateBadge()` from `init()`**

In the `init()` IIFE, immediately after the `renderChainTriggers();` line added in Step 3.4, add:

```js
    renderNewUpdateBadge();
```

So init now reads:

```js
    renderStoryFollowState();
    renderChainTriggers();
    renderNewUpdateBadge();
    renderFollowPanel();
```

- [ ] **Step 6.4: Verify in the browser**

Reload. With no follows set:
- Soccer Stadium card: gray `▾ See updates (3)` trigger, no badge.
- Vibrancy 19 Grants card: gray `▾ See updates (2)` trigger, no badge.

Click `☆ Follow` on Soccer Stadium:
- Card gets the orange border (existing follow styling).
- The trigger immediately restyles to bold orange `▼ See updates (3)`.
- The orange `New Update` badge appears next to the headline.

Click `★ Following` to unfollow:
- Card loses the orange border.
- Trigger reverts to gray `▾ See updates (3)`.
- Badge disappears.

Follow the Vibrancy 19 Grants card:
- Trigger restyles to orange.
- No badge appears (because `isFreshChapter: false` for that story).

If a chain entry was expanded before the follow toggle, it collapses (current behavior — `renderChainTriggers` rebuilds the trigger and expanded block fresh, so per-session expansion state is not preserved across follow toggles). This matches the spec: expanded state is per-session and not persisted; this is a minor edge case to be aware of.

- [ ] **Step 6.5: Commit**

```bash
git add dashboard/index.html
git commit -m "Re-render chain trigger and badge on follow toggle"
```

---

## Task 7: Final verification matrix and mobile pass

**Goal:** Walk every state in the spec to confirm the implementation matches. Capture anything that misses and patch it.

**Files:**
- Possibly modify: `dashboard/index.html` only if a verification step fails.

- [ ] **Step 7.1: Desktop verification matrix**

Open `dashboard/index.html` in a desktop browser, then go through each row:

| Scenario | Expected |
|---|---|
| Soccer Stadium, not followed | gray `▾ See updates (3)`; no badge; click expands; click hides |
| Soccer Stadium, followed | bold orange `▼ See updates (3)`; orange `New Update` badge by headline; card has orange border |
| Vibrancy 19 Grants, not followed | gray `▾ See updates (2)`; no badge |
| Vibrancy 19 Grants, followed | bold orange `▼ See updates (2)`; **no** badge (isFreshChapter false); orange border |
| Any other story (e.g., Swanky Scoops), not followed | no trigger, no badge — card identical to pre-feature |
| Any other story, followed | no trigger, no badge (no chain data); only the existing orange follow border appears |
| Chain expanded view | vertical orange rail with three (or two) dots, each entry shows date / headline / snippet in the typography spec |

If any row fails, the broken behavior usually traces to one of: missing `:scope` selector behavior, missing call site in `renderStoryFollowState`, or stale CSS specificity against `.story-item *`. Patch the smallest thing that makes the row pass.

- [ ] **Step 7.2: Mobile verification**

In devtools, switch to a narrow viewport (e.g., 375×667, iPhone SE). Confirm on the followed Soccer Stadium card:
- Header chips and the `New Update` badge fit on the same line as the headline, or wrap gracefully if not.
- The follow `★ Following` label moves to its own line below the headline (this is existing mobile behavior from CSS rule near line 284 — `.follow-btn { position: static; margin-top: 8px; }`).
- The expand still works and the chain rail/dots render correctly inside the narrow card.

If the badge crowds the headline, the badge can take `display: inline-block` and `margin-top: 4px` — patch the CSS rule from Task 1.2 minimally if needed.

- [ ] **Step 7.3: Keyboard / accessibility spot check**

- Tab to the chain trigger button → focus ring visible (browser default is fine).
- Press Enter or Space → chain expands; `aria-expanded` flips to `"true"`.
- Press again → collapses; `aria-expanded` flips back.
- Inspect the badge: `aria-label="new update available in this brief"` is present.
- Inspect the expanded region: `role="region"`, `aria-label="Earlier in this story"`, `aria-live="polite"` are present.

- [ ] **Step 7.4: Commit any patches**

If Steps 7.1–7.3 required tweaks:

```bash
git add dashboard/index.html
git commit -m "Patch story chain verification edge cases"
```

If nothing needed patching, skip this step — the feature is already committed task-by-task.

- [ ] **Step 7.5: Confirm the feature is dormant for stories without chain data**

Open the page with the network panel open. The page should make zero additional requests for chain data (everything is in-process from the `STORY_CHAINS` constant). All stories not listed in `STORY_CHAINS` should render byte-identical to pre-feature.

---

## Out-of-scope (intentionally deferred)

The following items are explicitly NOT in this plan and should NOT be added during execution:

- **Wiring `STORY_CHAINS` to real data.** The stub is intentional. When the JSON data layer from `2026-05-20-stories-as-json-design.md` ships, `getChainFor(storyId)` is the single function to update.
- **Persisting expanded state across reloads or follow toggles.** Spec calls this out as per-session.
- **Linking chain entries to their original archived briefs.** Future polish.
- **Animation on expand/collapse.** Spec says optional; not in scope.
- **Cross-story "related stories" UI.** Different feature, separate spec.
