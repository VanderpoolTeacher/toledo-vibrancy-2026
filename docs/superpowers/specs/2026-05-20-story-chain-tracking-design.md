# Story Chain Tracking — visual design

**Date:** 2026-05-20
**Scope:** Visual design only. The data layer is being defined in [2026-05-20-stories-as-json-design.md](./2026-05-20-stories-as-json-design.md); this spec describes what the dashboard renders on top of it.

## Goal

A reader follows a story (★ Follow) today. When tomorrow's brief contains a new chapter for that same story, the dashboard signals it visibly, and a one-click expand reveals the full chain of prior mentions in order — inline, in place, without leaving the card.

## Out of scope

- The data model that produces story chains. Assumed to be available from the JSON corpus.
- Cross-story connection visualization (the "this story relates to that story" web).
- Search, filtering, or cross-day query UI.
- Mobile vs desktop divergence beyond what's noted under Mobile.

## Data assumption

The renderer assumes each story card has access to:

- The story's stable `id` (already in the data spec).
- The story's prior chain: an ordered list of `{date, headline, snippet}` entries from earlier days where this same `story_id` appeared. Empty list means no prior chain (story is new).
- A boolean "is today's appearance a fresh chapter" — i.e., the story appeared in at least one prior day and is appearing again today with updated content.

How those three things get derived from `stories/<id>.json` + `days/<date>.json` is a data-layer concern. This visual spec doesn't dictate it.

## Visual design

### Three card states

**State 1 — Followed story with a fresh chapter today (collapsed)**

- Card retains today's followed treatment (orange left border, "★ Following" label at top-right).
- Header row gains a second chip beside the existing date chip: **`NEW UPDATE`** — orange pill (`#d4831f` background, white text, 10px, 700-weight, uppercase, `letter-spacing: 0.04em`, `padding: 2px 7px`, `border-radius: 8px`).
- Below the prose, a bold orange trigger row: **`▼ See updates (N)`** — 12px, 600-weight, color `#8c6a1a`, cursor pointer. `N` is the count of prior chapters.

**State 2 — Same card, expanded**

- Trigger flips to **`▲ Hide updates (N)`**.
- A dotted top divider (`1px dotted #e5cba3`) separates the prose from the chain.
- Small uppercase label above the chain: `EARLIER IN THIS STORY` (10px, 700-weight, `color: #888`, `letter-spacing: 0.06em`, `text-transform: uppercase`).
- Chain renders as a vertical rail: `border-left: 2px solid #d4831f`, `padding-left: 12px`.
- Each chain entry:
  - Orange dot marker absolutely positioned on the rail (10px diameter circle, `background: #d4831f`, `left: -18px` relative to the rail).
  - Date line: 11px, 700-weight, `color: #8c6a1a`, uppercase (e.g., `MAY 14, 2026`).
  - Headline line: 12px, 600-weight, `color: #1a1a1a`.
  - Snippet line: 11px, `color: #666`, 1-line ideal, wrap allowed.
  - Vertical gap between entries: 10px.
- No links/clicks on chain entries in v1 — read-only. (Linking to the archived brief for that date is an out-of-scope follow-up.)

**State 3 — Non-followed card that has a chain**

- Card is unchanged from today's design (no orange border, no header chip changes).
- Trigger row appears at the same position as on followed cards, but subdued: **`▾ See updates (N)`** — 11px, normal-weight, `color: #888`.
- No `NEW UPDATE` badge. The chain exists but the reader hasn't elected to track it; we show the affordance without shouting.
- Expand behavior is identical to State 2 — same rail, dots, typography.

**Cards with no chain**

- No trigger, no badge, no visual change. Identical to today.

### Color and typography rules

- Reuse the existing follow accent color `#d4831f` and its 600-weight variant `#8c6a1a`. No new palette entries.
- Reuse existing date-chip dimensions and chip typography for the `NEW UPDATE` badge so the header chip row reads as one rhythm.
- Reuse existing card border radius (6px), padding (12px), and prose typography. Nothing in this spec restyles the card itself.

### Interaction

- Click `See updates` → card expands in place (no animation required for v1; a CSS transition on max-height is acceptable polish but not required).
- Click `Hide updates` → card collapses.
- Expanded state is per-session in-memory only — not persisted across page reloads.
- Toggling a story's follow state does not auto-expand or collapse the chain.

### Mobile (≤600px)

- Card width unchanged from today.
- Header row may wrap to a second line if the date chip + `NEW UPDATE` chip + `★ Following` label don't fit. The follow label drops to the right edge on its own line; chips stay together on the first.
- Expanded chain uses the same rail/dot/typography rules. No mobile-specific divergence.

### Accessibility

- Trigger row is a `<button>` (not a `<div>`), focusable, with `aria-expanded` reflecting state.
- Chain container is `aria-live="polite"` so screen readers announce when the chain appears.
- `NEW UPDATE` badge includes `aria-label="new update available in this brief"` so it's not just a color signal.
- Color contrast: `#8c6a1a` on `#fff8e7` and `#fff` both pass WCAG AA at the sizes used.

## Reference mockup

The browser mockup at `.superpowers/brainstorm/64760-1779316888/content/full-design.html` shows States 1, 2, and 3 rendered. That artifact is the visual source of truth; written rules above describe it for implementers who can't open the mockup.

## Explicit decisions worth flagging

- **Chain trigger appears on non-followed cards too** (State 3), in subdued styling. A strict reading of "follow → see chain" would hide the trigger entirely on unfollowed cards. The decision here is to show it as a discovery affordance: a reader can see "this story has 3 prior chapters" without having to follow it first. Reverse this if you want chains gated strictly behind follow.
- **No animation on expand/collapse.** A CSS `max-height` transition is acceptable polish but not required. Skipping animation keeps the layout shift instant and predictable in a card grid.
- **Expanded state is per-session, not persisted.** Reloading the page collapses everything. Persisting expansion across reloads is a future polish item.

## Open questions

None blocking. The data-derivation rules (specifically, what defines "fresh chapter today") are owned by the stories-as-JSON spec and its chain-tracking follow-up.
