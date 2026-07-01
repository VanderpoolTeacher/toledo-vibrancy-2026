# Verified coordinate sources for dashboard story mini-maps
# Each row will be pasted into STORY_LOCATIONS in Task 4.
# Format: <story id> | <label> | <lat> | <lon> | <source>
# Verification method: OpenStreetMap Nominatim (2026-05-20, email=mvanderpool.edu@gmail.com)

## Points

huron-yards-phase-two | 28 N. Erie St | 41.6492 | -83.5407 | Nominatim: "28, North Erie Street, Warehouse District, Toledo" — adjusted lon from -83.5379 (~230 m west correction)

port-warehouse-liquid-terminal | Toledo-Lucas County Port Authority HQ (One Maritime Plaza) | 41.6538 | -83.5283 | Nominatim: "One Maritime Plaza, Glass City Riverwalk, Vistula Historic District, Toledo" — adjusted lat from 41.6526, lon from -83.5305 (~220 m correction)

ostrich-towne-tenants | Ostrich Towne (219 N. Superior St, Vistula warehouse district) | 41.6509 | -83.5367 | Nominatim: "219, North Superior Street, Saint Clair Street Historic District, Toledo" — major correction from best-effort 41.6610/-83.5380 (~1100 m); original centroid was for the broader Vistula neighbourhood, not the building
ostrich-towne-tenants | AUDIT 2026-05-21: corrected to 915 N Summit St per story prose (Riverside BBQ address). Old coords 41.6509/-83.5367 were ~750 m west of actual building. New coords 41.6566/-83.5269 from Nominatim: "915, North Summit Street, Vistula Historic District, Toledo" (OSM way 173954609). Label updated to "Ostrich Towne — 915 N Summit St".

soccer-stadium-vistula | Proposed Vistula riverfront stadium site (across from Glass City Metropark) | 41.6539 | -83.5215 | no Nominatim hit for proposed site — kept best-effort; label notes "proposed"

owens-corning-250m | Owens Corning World HQ (1 Owens Corning Pkwy) | 41.6476 | -83.5350 | Nominatim: "1, Owens Corning Parkway, Saint Clair Street Historic District, Toledo" — adjusted lat from 41.6438, lon from -83.5375 (~450 m correction)

mind-and-soul-gallery | Gardner Building (506 Madison Ave) | 41.6520 | -83.5359 | Nominatim: "506, Madison Avenue, Downtown, Toledo" — adjusted lon from -83.5377 (~160 m correction)

foundation-steel-hq-move | Foundation Steel / Ohio Plate Glass — 303 Morris St | 41.6412 | -83.5389 | Nominatim: "303, Morris Street, Middle Grounds, Toledo" (OSM way 8785428) — 2026-05-21

## ConnecToledo music series — 4 parks

connectoledo-music-grant.promenade | Promenade Park (400 Water St) | 41.6503 | -83.5333 | Nominatim park centroid: "Promenade Park, Toledo" — adjusted lat from 41.6479, lon from -83.5343

connectoledo-music-grant.glasscity | Glass City Metropark | 41.6547 | -83.5168 | Nominatim park centroid: "Glass City Metropark, Toledo" — adjusted lat from 41.6499, lon from -83.5236 (~600 m correction; park is further east than best-effort)

connectoledo-music-grant.junction | Junction Park (Junction Ave / Nebraska Ave area) | 41.6411 | -83.5611 | no Nominatim hit for "Junction Park Toledo" — kept best-effort; "Junction Avenue, Air Line Junction, Toledo" returned lat 41.6493/-83.5772 (wrong area), so best-effort retained

connectoledo-music-grant.dthomas | Danny Thomas Park | 41.6254 | -83.5650 | Nominatim: "Danny Thomas Park, Toledo" lat 41.6254/-83.5650 — MAJOR correction from best-effort 41.6589/-83.5444 (~3700 m); park is in South Toledo, not near downtown

## Polyline: Vistula Metropark — Water St between Olive and Magnolia

vistula-metropark.olive | Water St & Olive St (SW end) | 41.6535 | -83.5293 | OSM Water Street, Vistula Historic District bbox SW corner (41.6535, -83.5293) — adjusted from best-effort 41.6647/-83.5320 (~1250 m north); original was outside the Vistula district entirely. Task 4 note: these are approximate bbox endpoints of the OSM way; field-check if possible.

vistula-metropark.magnolia | Water St & Magnolia St (NE end) | 41.6572 | -83.5237 | OSM Water Street, Vistula Historic District bbox NE corner (41.6572, -83.5237) — adjusted from best-effort 41.6663/-83.5310 (~1050 m north)

## Polygon: RAISE 38-block area, 13th–21st St × Adams–Monroe

raise-uptown-junction.se | SE corner: 13th St & Monroe St | 41.6537 | -83.5520 | no Nominatim hit for intersection — kept best-effort; https://toledo.oh.gov/raise

raise-uptown-junction.nw | NW corner: 21st St & Adams St | 41.6580 | -83.5610 | no Nominatim hit for intersection — kept best-effort; https://toledo.oh.gov/raise

glass-city-jazzfest-2026.glasscity | Glass City Metropark (free day, Aug 15) | 41.6547 | -83.5168 | reused verified coords from connectoledo-music-grant.glasscity (Nominatim 2026-05-20)
glass-city-jazzfest-2026.zoo | Toledo Zoo Amphitheater (2 Hippo Way) | 41.6459 | -83.5680 | best-effort; no Nominatim hit for amphitheater specifically; zoo complex centroid from OSM "Toledo Zoo" node — field-check recommended

---

## Vibrancy 17 cross-check (Step 1.3)

None of the 17 root-map Vibrancy grant properties exactly matches any dashboard story location above. The closest overlap is "Okun Market — 33 N Huron St" (lat 41.6488938, lon -83.5398874), which is one block from Huron Yards' 28 N. Erie St — a different building. All other Vibrancy properties are in distinct neighborhoods (South Toledo, East Toledo, North Toledo, Old West End) with no geographic overlap with the story coordinates.
