# Toledo Vibrancy Initiative 2026 — Grant Award Map

A reusable summary of what was built, why, and how — written so it can be excerpted for LinkedIn, blog posts, slides, video scripts, or press inquiries.

## One-liner

An interactive single-page web map of the 17 properties receiving grants from the City of Toledo's 2026 Vibrancy Initiative — so anyone in Toledo can see where the city is investing, what's being built, and what recipients agreed to.

## The story in one paragraph

The City of Toledo announced $630,000 in 2026 Vibrancy grants — 19 awards across 17 properties in 10 neighborhoods, expected to leverage roughly $13.5 million in private investment. The information was public, but it lived across a press release, an ArcGIS feature service, and three program pages. This map pulls those threads together into a single visual: every property pinned and color-coded by grant type, each with a photo, a project description, the applicant's estimated investment, and a one-click "About this grant" panel that explains the program and the deadlines awardees actually signed up for.

## The numbers (straight from the City's press release)

- **$630,000** awarded in 2026
- **19 grants** to **17 properties** across **10 neighborhoods**
- **~$13.5 million** in private investment expected to be leveraged
- **82 applications** submitted

## The three grant programs

- **Façade Improvement Grant** — Up to $30K per building/year, reimbursing 50% of eligible exterior costs (75% in a designated Legacy Commercial Corridor).
- **White Box Grant** — Up to $75K per building/year, reimbursing interior code upgrades and tenant build-out at the same 50% / 75% rates.
- **Planning Grant** — Funds architectural and design work to activate ground-floor commercial spaces, particularly in legacy commercial corridors.

## 2026 deadlines awardees agreed to

- **May 22, 2026** — Grant agreement executed
- **Aug 14, 2026** — Construction must commence (failure to begin can terminate the agreement)
- **Dec 4, 2026** — Full project completion

Recipients also execute a Restrictive Covenant with the Lucas County Recorder — the property may not be sold without the City's approval before December 1, 2028.

## What the map does

- **Color-coded markers** for all 17 properties, one color per grant type, plus a "Multiple" color for properties that received more than one grant.
- **Filter pills** to show only one grant type at a time (or just the multi-grant properties).
- **Click a marker (or a list entry)** to open a popup with:
  - A photo of the property
  - Business name, address, neighborhood
  - Grant type pill(s)
  - Project description and estimated investment
  - A footnoted source citation linking back to the City's public dashboard
- **Click the photo** inside the popup to expand it into a wide banner that fills the card; click again to shrink it back.
- **"About this grant" link** in the header opens a wide centered modal with the three programs laid out side-by-side, the 2026 deadlines, and the post-award obligations recipients agreed to.
- **Mobile layout** swaps the desktop sidebar for a slide-up bottom sheet and a horizontal filter strip, so the map takes the screen.

## Under the hood

- **Single static HTML file.** No build step, no framework, no backend. The whole app is one document you can right-click "View Source" on.
- **Leaflet** for the map, **CARTO Voyager** tiles for a clean Google-Maps-style basemap.
- **Vanilla CSS** with mobile-first responsive rules and a dark theme.
- **Data** from the City of Toledo's [Vibrancy Projects feature service](https://gis.toledo.oh.gov/arcgis/rest/services/Hosted/Vibrancy_Projects/FeatureServer/2), the [May 15, 2026 press release](https://toledo.oh.gov/news/2026/05/15/mayor-kapszukiewicz-announces-19-vibrancy-initiative-grant-awards-expected-to-spur-13-5-million-in-investment-across-10-neighborhoods), and the [Vibrancy program page](https://toledo.oh.gov/business/how-to-do-business-in-the-city/incentive-programs/vibrancy) (plus the [Façade](https://toledo.oh.gov/business/how-to-do-business-in-the-city/incentive-programs/vibrancy/fig) and [White Box](https://toledo.oh.gov/business/how-to-do-business-in-the-city/incentive-programs/vibrancy/wbg) sub-pages).
- **Property photos** are the city's own hosted images from the Vibrancy page.

## How it grew

Each step was its own small commit — the map didn't try to be everything on day one.

1. Start with a basic Leaflet pin board and sidebar list.
2. Add a reset-map button.
3. Add business names, owners, and project descriptions to each marker.
4. Swap the basemap to CARTO Voyager for a cleaner look.
5. Center the map on a marker when the user clicks it; pan so the popup is fully visible.
6. Add source-citation footnotes for every dollar amount in the popups.
7. Make the mobile layout usable — map on top, popup fits in view.
8. Refactor mobile UX into a proper bottom sheet (filter strip stays on top; tapping a marker slides the sheet up).
9. Add property photos, side-by-side with details on desktop, full-width banner on mobile.
10. Click-to-expand toggle on each photo.
11. "About this grant" modal explaining the program, deadlines, and recipient obligations — laid out in columns on desktop.

## Why it matters

Public-data transparency only works if the public can actually read it. A row in an ArcGIS feature service is technically open data, but only a developer can use it. Putting the same data into a map your neighbor can click through is the difference between *publicly available* and *actually visible.*

## Quotable lines

Drop straight into a post, caption, or slide:

- "$630K is going into 17 properties across 10 Toledo neighborhoods — expected to spark roughly $13.5M in private investment."
- "Public-data transparency only works if the public can actually read it."
- "The information existed. It just wasn't visible."
- "A single static HTML file. No build step, no backend, no framework. The whole app is one document you can right-click 'View Source' on."
- "Color-coded markers, photos of every property, and the actual deadlines awardees agreed to — in one view."
- "The difference between *publicly available* and *actually visible.*"

## Angles for different audiences

- **Civic engagement / neighborhood organizations** — focus on transparency, neighborhood-level visibility, who got what, and the deadlines the city is holding awardees to.
- **Small-business / property owners** — focus on the three programs, the dollar caps and match rates, and the post-award timeline.
- **Education / civics classroom** — a real-world example of taking municipal open data and turning it into something people can use.
- **Tech / dev-curious** — zero-dependency single-file map, Leaflet, ArcGIS feature service, mobile-responsive without a framework.

## Repo

[github.com/VanderpoolTeacher/toledo-vibrancy-2026](https://github.com/VanderpoolTeacher/toledo-vibrancy-2026)
