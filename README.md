# Trend Detective

![Years needed for a significant warming trend across Europe](screenshots/map_years_needed.png)

**Live page:** https://schumacherjan-dev.github.io/trend-detective/

![15-second demo: play the time window, click a place, enter a birth year](screenshots/demo.gif)

**Most tools show what changed. Trend Detective shows how long you need to wait before you can trust it.** In the Oslo cell the 10 years 2015–2024 show cooling (−0.27 °C per decade, not significant) while 44 years show +0.31 °C per decade. The page shows, for 315 grid cells over Europe, how many years of NASA POWER data a trend needs before it is significant and stays so. Validation against station data is reported openly, including where it fails (for example German precipitation: r = 0.85 with the stations, but the direction of the trend can differ).

**Experience the 3 key findings in 3 clicks** (every view has its own link):
1. [The 10-year illusion: Oslo, 2015–2024](https://schumacherjan-dev.github.io/trend-detective/#v=T2M&s=year&view=trend&y=2015&fdr=1&c=60,10) shows cooling, the full 1981–2024 record shows warming.
2. [Extremes shift faster than averages: unusually hot days](https://schumacherjan-dev.github.io/trend-detective/#v=D_TX90&s=year&view=trend&y=1981&fdr=1) (experimental, modelled daily data).
3. [Your lifetime: Berlin](https://schumacherjan-dev.github.io/trend-detective/#v=T2M&s=year&view=trend&y=1981&fdr=1&c=52.5,12.5) (or [Hamburg](https://schumacherjan-dev.github.io/trend-detective/#v=T2M&s=year&view=trend&y=1981&fdr=1&c=52.5,10)): in the detail panel enter your birth year under "Your lifetime".

How the data files are made: see "Run it" below (`fetch_cache.py` → `build_data.py` → static `data.js`).

## Quickstart (for users)
1. Open the live page (no installation, no account, runs in your browser).
2. Click one of the "Start with a case" buttons, for example "Warming: how fast is it detectable?".
3. Click any grid cell on the map to see its yearly values, the trend and whether it is significant.
4. Switch the view: trend per decade, years needed, or the year the trend became detectable.
5. Use "Copy link to this view" to share exactly what you see.

| Trend per decade | Year the trend became detectable |
|---|---|
| ![](screenshots/map_trend.png) | ![](screenshots/map_emergence.png) |

## License
Code: MIT (see LICENSE). The data files keep the licences of their sources (see "Data, licences and references"): this applies in particular to the Berkeley Earth file, which is CC BY-NC 4.0 and not covered by the MIT licence.


**Most tools show what changed. Trend Detective shows how long you need to wait before you can trust it.**

Solo entry for the NASA Space Apps Challenge 2026, challenge *Be An Earth System Trend Detective!* (local event: Hamburg, virtual).

- Live page: `https://schumacherjan-dev.github.io/trend-detective/`
- Offline copy: `trend_detective_standalone.html` (one file, about 11 MB, no internet needed)
- Data: NASA POWER (MERRA-2 meteorology; satellite sunshine from SRB and CERES), monthly, 1981–2024, 315 grid points over Europe (35–70°N, 10°W–40°E, every 2.5°)

## What it does

For every grid point the tool asks not only *is there a trend?* but *how many years of data did we need before the trend became clear, and when did it emerge?* A trend over a few years can point in the wrong direction. The page shows where that happens and where 44 years are still not enough.

| The challenge asks | Where to find it |
| --- | --- |
| What is changing? | Variable menu: air temperature, precipitation, root-zone soil moisture, specific humidity, relative humidity, sunshine at the ground, plus four "unusual months" counts (warm, cold, wet, dry) and three experimental daily extremes (unusually hot days, days of 30 °C or more, heavy-rain days). Glossary with units. |
| Where? | Map of 315 cells, season switch (year, winter, spring, summer, autumn), six regional averages (north, centre, south, land, sea, all), city search, compare two places |
| How much? | Trend per decade (Theil–Sen) with 95 % range, fitted total change, records, "in plain words" sentence in the detail panel |
| Is it significant? | Mann–Kendall test, FDR-corrected over cells (black dots), robustness table, autocorrelation check |
| Does it differ between regions? | Regional table, "Warming vs. precipitation" map, compare mode. Example: winter precipitation falls south of 45°N and rises north of it in the median (−0.033 and +0.05 mm/day per decade), but not significantly in either |
| *Extra:* my lifetime | In "Your place", enter a birth year (1981 or later) and read how much warmer the place became since then; warming stripes can be downloaded as a PNG |
| *Extra:* two maps | "Compare two maps": a second live map with its own variable, season, view and window; zoom is linked, a click selects the cell on both; swap A and B; the state is in the URL. Example: warming vs. rain side by side. Hover tooltips show a small line chart of the yearly values with the fitted trend; a "Surprise me" button jumps to a notable place. Map extras: hover frame, town labels that increase with zoom, "Land only" (fades sea cells), "Play windows" (steps the start year from the shortest window to the full record and shows how many cells are significant). Also: timelapse of the year the trend became detectable, map as PNG, dark mode, keyboard use of the map. |
| *Extra:* my own place | Search a town (8,278 places) or click a cell: "Your place" summary in plain words (warming, detectable since, unusual months, new normal, rain) with a copy button, and warming stripes (one bar per year) |
| *Extra:* how long until we know? | "Years needed" map, "Year the trend became detectable" map, "How long would I have to measure here?" planner |

## Who it is for

- **Water managers and farmers:** a grey rainfall cell does not mean "no change". In the typical cell a precipitation trend would have to reach about ±0.096 mm/day per decade to be detected over 44 years; the typical fitted trend is 0.030. The planner turns this around: choose a change you care about, read how many years of measurement you would need there.
- **City planners:** unusually warm months (warmest 10 % of each calendar month in 1981–2010) rose from 0.9 per year (1981–1990) to 3.8 (2015–2024), 3.2 times the normal 1.2. In 172 of 315 cells the average year of 2015–2024 is warmer than the warmest single year of 1981–2000.
- **Teachers and journalists:** two buttons make the point on their own. In the Oslo cell the 10 years 2015–2024 show cooling (−0.27 °C per decade, not significant) while 44 years show +0.31. Dublin (+0.19 °C per decade) needs 38 years to be sure, Warsaw (+0.51) only 19.

## Which parts of the Earth system, which NASA data

| Part | Variable (NASA POWER code) | Source behind it |
| --- | --- | --- |
| Atmosphere | air temperature at 2 m (T2M), specific humidity (QV2M), relative humidity (RH2M) | MERRA-2 reanalysis (NASA GMAO) |
| Water cycle | precipitation (PRECTOTCORR) | MERRA-2, bias-corrected |
| Land | root-zone soil moisture (GWETROOT; not defined over sea) | MERRA-2 land model |
| Energy | sunshine at the ground (ALLSKY_SFC_SW_DWN) | SRB satellite product to 2000, CERES from 2001 |

Not covered: ocean, ice and vegetation. The data are delivered through NASA POWER; other NASA products were out of reach for this project.

## Method

1. Monthly values per grid point; the mean seasonal cycle is removed (anomalies). Annual and seasonal means (DJF, MAM, JJA, SON).
2. Trend: Theil–Sen slope per decade. Significance: Mann–Kendall test (Kendall's tau).
3. Many cells are tested at once, so the Benjamini–Hochberg false discovery rate correction is applied across cells for every window.
4. **Years needed:** all windows ending in 2024 from 44 years down to 10 years are tested. The result is the shortest window from which the trend stays significant for every longer window. This avoids picking a lucky window.
5. **Year of emergence:** the start stays at 1981 and the end year moves from 1990 to 2024; the result is the first end year from which the trend stays significant.
6. **Unusual months:** per calendar month the 10 % warmest/coldest (wettest/driest) months of 1981–2010 set the threshold; the yearly count of months beyond it is analysed like any other series.
7. **Daily extremes (experimental):** from NASA POWER daily values (`T2M_MAX`, `PRECTOTCORR`, 1981–2024). *Unusually hot days* = days above the 90th percentile of the same calendar day (±7 days) in 1981–2010; *hot days* = daily maximum ≥ 30 °C; *heavy-rain days* = more rain than the 95th percentile of rainy days (≥ 1 mm) in 1981–2010 at that cell. The yearly counts go through the same trend, FDR, years-needed and emergence pipeline. Result: unusually hot days rise significantly in 314 of 315 cells (typical cell needs 27 years, longer than the mean temperature because single days are noisier); heavy-rain days in only 10 cells. These are modelled grid-cell values and were not validated against stations.
8. **Smallest detectable trend (MDT):** 2.8 · σ / √(n(n²−1)/12), per decade, with σ the swing of the yearly values around the fitted line (80 % power, 5 % level, independent years assumed). The planner solves the same formula for n.
9. **Signal to noise:** total change over 44 years divided by σ. Cells with a higher ratio emerged earlier (rank correlation −0.61); the ratio is above 2 in 264 of 315 cells for temperature.

## Main results (whole year, 1981–2024, FDR)

| Variable | Significant cells | After autocorrelation correction |
| --- | --- | --- |
| Air temperature | 315 / 315 (median 21 years needed, maximum 41 years at 65°N/15°E) | 305 |
| Specific humidity | 309 / 315 | 301 |
| Sunshine at the ground | 213 / 315 | 199 |
| Relative humidity | 62 / 315 | 5 |
| Precipitation | 11 / 315 | 9 |
| Root-zone soil moisture | 26 / 232 | 2 |

- Land warms faster than sea: +0.44 against +0.33 °C per decade.
- Temperature with data to 2005 is detectable in 20 % of cells, to 2010 in 49 %, to 2015 in 86 %, to 2020 in 96 %, to 2024 in 100 %.
- In 140 of 315 temperature cells shorter windows are significant while not all longer ones are ("flicker"): an early result is not a stable result.
- Averaging helps: only 11 of 315 single cells show a significant precipitation trend, but the average over all land cells changes by +0.034 mm/day per decade (significant, stable from 33 years). For planning, regional averages are a firmer basis than one cell.
- Water vapour rises in all 315 cells, relative humidity falls in 198, soil moisture shows no common direction (118 of 232 falling). We report the pattern and do not test its causes.

## Validation: where it works and where it fails

Compared with measured country series (Germany DWD, Sweden SMHI, plus Berkeley Earth for southern Europe, Finland, Norway, Latvia and Lithuania). These are country means, not single stations.

| Series | Correlation of yearly values | Trend, measured / POWER (per decade) |
| --- | --- | --- |
| Temperature Germany | 0.99 | 0.47 / 0.51 |
| Temperature Sweden | 0.98 | 0.42 / 0.40 |
| Temperature Spain | 0.93 | 0.26 / 0.21 |
| Temperature Italy | 0.96 | 0.39 / 0.30 |
| Temperature Greece | 0.98 | 0.41 / 0.41 |
| Precipitation Ireland (8 stations, 1981-2022) | 0.89 | +20.6 / +10.7 mm per year |
| Temperature Finland | 0.99 | 0.56 / 0.54 |
| Temperature Norway | 0.94 | 0.48 / 0.32 |
| Temperature Latvia and Lithuania | 0.99 | 0.45 / 0.40 |

**Where we fail.** For German precipitation the yearly swings match (r = 0.85) but the trend has the opposite sign (measured −15.6, POWER +11.0 mm per year and decade). For German sunshine the swings match (r = 0.91) but POWER's trend is smaller (2.4 against 3.8 % of the mean per decade, DWD sunshine duration against POWER surface radiation), which is probably related to the change of satellite product in 2001. We show both on the page because a tool that only shows its successes cannot be checked. Colour direction for precipitation should be read with care.

## Robustness

- **Autocorrelation:** significance recomputed with an effective sample size (`autocorr_check.py`, results in the robustness table on the page).
- **Placebo test** (`null_test.py`): with the years shuffled in time, raw tests flag about 5 % of cells (the expected rate); after FDR correction on average at most 0.3 cells remain. With a shared shuffle across cells, clusters appear occasionally (specific humidity: at most 156 cells in 1 of 100 runs), which shows that neighbouring cells are not independent.
- **Start-year test:** starting in 1991 instead of 1981 changes air temperature little (median years needed 21 against 20, cell correlation 0.94, significant cells 315 against 309), but soil moisture depends strongly on the start year (26 significant cells against 1). We therefore treat soil moisture as fragile.

## What we tested and deliberately excluded

- **Change-point test:** more attack surface than insight with 44 yearly values. We show the one known break, the source change in sunshine in 2001, as a marker.
- **"Rain paradox" (wetter air, drier soil):** not supported. Soil moisture trends are mixed (118 of 232 cells negative, 18 significantly falling, 8 rising; 2 significant after autocorrelation correction).
- **Heat–drought coupling by half-periods:** 22 years are too short, and MERRA-2 soil moisture is a model product, so the coupling could partly be a model artefact.
- **Counting compound hot and dry years:** rare events, 22 years too short, soil moisture fragile.
- **"Winter warming is steeper":** in this data the winter trend is smaller than the summer trend (median +0.32 against +0.44 °C per decade); winters swing more from year to year, so they need more years to be significant.
- **"Winter wetter, summer drier cancel out in the annual mean":** not supported. Winter precipitation has 0 significant cells, summer 1; the median trend is slightly positive in both, and only 56 cells show opposite signs.
- **Station markers on the map:** the validation uses country means, so station markers would suggest a precision we did not test.
- **Forecasts:** the page describes the past. A formula that extrapolates the "years needed" correlated only about 0.5–0.6 with the real value, and grey precipitation cells have a median of 98 years.
- **Causes:** no attribution (for example North Atlantic Oscillation, aerosols). We do not test them.
- **Smaller grid:** finer than 2.5° would add cells that see the same weather, not independent evidence.

## Limits

- Reanalysis and satellite products, not direct measurements. Cells are single points about 100–280 km apart; mountains and coasts are smoothed. Not for local decisions: for a site use station data.
- Only linear trends. The main variables are monthly means; the "unusual months" look at the extremes of the monthly values; the daily extremes are experimental (modelled grid-cell daily values, not validated against stations, and a grid-cell maximum is usually lower than a station's).
- All windows end in 2024, except the "year of emergence" view (start fixed at 1981, end moving).
- The FDR correction handles many tests, not the dependence between neighbouring cells. The smallest-detectable-trend and planner estimates assume independent years and are therefore somewhat optimistic.
- Land and sea: the regional "land" and "sea" averages use the land flag of the grid point (Natural Earth polygons). Two cells in northwest Russia (67.5°N 30°E and 32.5°E, lakes) are flagged as sea although they are land; moving them changes the regional means by about 0.003 °C per decade. The "Land only" display uses the land share of the whole cell instead (under 10 % land = mostly sea).
- Sunshine has a source change in 2001; treat its trend as less certain.
- Station scale, and a Mediterranean precipitation validation, are not tested.

## Run it

Everything runs in the browser. Keep `index.html`, `data.js`, `land.js`, `cellinfo.js`, `cities.js` and `validation_series.js` in one folder and open `index.html`, or open `trend_detective_standalone.html`. The URL hash stores the current view, so links can be shared.

To rebuild the data (Python 3 with `numpy`, `pandas`, `scipy`):

```
pip install -r requirements.txt
python fetch_cache.py --var T2M --step 2.5 --start 1981        # repeat for PRECTOTCORR, GWETROOT, QV2M, RH2M, ALLSKY_SFC_SW_DWN
python fetch_daily.py                                           # optional: daily T2M_MAX and PRECTOTCORR (about 10 minutes), into cache_daily/
python daily_metrics.py                                         # yearly day counts -> daily_counts.json (included in the repository)
python build_data.py --start 1981 --step 2.5 --min-window 10    # writes parts/*.json and data.js (all five seasons, about 2 minutes)
python autocorr_check.py && python null_test.py                 # robustness checks
```

`fetch_cache.py` downloads monthly series from NASA POWER into `cache/` and skips points already downloaded, so an interrupted run can be repeated; failed requests are retried three times and then skipped. The cache is not part of the repository (27 MB, 2,669 files); it was downloaded on 14 November 2026, and POWER is reprocessed from time to time, so a new download may differ slightly. Validation scripts: `dwd_compare*.py`, `smhi_compare.py`, `berkeley_compare.py`, `validation_series.py`.

## Data, licences and references

All external data are used with attribution. The author processed them (country means or averages of grid points, yearly values, trends); the files in this repository are such derived series, not the original products.

| Source | Used for | Licence / terms |
|---|---|---|
| NASA POWER (MERRA-2 meteorology from NASA GMAO; SRB and CERES solar data), https://power.larc.nasa.gov | all maps and trends | open NASA data; acknowledgement: "These data were obtained from the NASA Langley Research Center (LaRC) POWER Project funded through the NASA Earth Science/Applied Science Program." |
| Deutscher Wetterdienst (DWD), Climate Data Center | Germany: temperature, precipitation, sunshine (validation) | CC BY 4.0 / GeoNutzV; "Datenbasis: Deutscher Wetterdienst, eigene Bearbeitung" |
| SMHI open data | Sweden: temperature (validation) | CC BY 4.0; source: SMHI, data processed |
| Met Office (UK and regional series, HadUK-Grid) | UK: temperature, precipitation, sunshine (validation) | Open Government Licence v3.0; (c) Crown copyright; contains public sector information licensed under the OGL v3.0 |
| Met Éireann via CSO PxStat table MTM01 | Ireland: rainfall, 8 stations (validation) | CC BY 4.0; source: Met Éireann / CSO |
| Berkeley Earth, regional temperature series | Spain, Italy, Greece, Finland, Norway, Latvia, Lithuania (validation) | CC BY-NC 4.0 (non-commercial; this project is non-commercial); attribution: Berkeley Earth, www.berkeleyearth.org |
| Natural Earth | land outlines, country assignment | public domain |
| GeoNames | place names for city search and cell descriptions | CC BY 4.0 |
| Python libraries NumPy, pandas, SciPy | analysis | BSD licences |

Reference values for the world and Europe on the page (about 1.4 °C, "twice as fast") come from the Copernicus Climate Change Service / WMO report *European State of the Climate 2025* and are linked, not copied.

## Use of AI

The question, the concept and every decision on what to build or exclude are mine. The code was written with Claude (Anthropic); the concept and plan were partly discussed with another AI assistant. All statements in the text were checked against our own data; claims that the data did not support were removed (see the list above). Where a number appears on the page it is computed from `data.js`.

## Author

Jan Schumacher, solo participant.


## Update: dry spells and context
- New experimental daily index: longest dry spell per year (consecutive days < 1 mm). Result: almost no detectable trend (1 of 315 cells significant after FDR), reported as is.
- New "Putting it in context" card: pre-industrial (1850-1900) figures from Copernicus/WMO European State of the Climate 2025, clearly marked as not computed from our 1981-2024 data.
- Per-cell CSV download (yearly values) next to the stripes picture.
- Colour-vision check (simulated protan/deutan/tritan, CIELAB distance): palettes stay distinguishable; the combined-map colour for "both significant" was darkened because it was too close to the precipitation blue for red-green colour vision.

- Validation extended with the Met Office UK series (HadUK-Grid areal series, Open Government Licence): temperature r = 0.99, precipitation r = 0.90 (trend direction agrees, both not significant), sunshine r = 0.75. Data: uk_metoffice_annual.csv; code: validation_series.py.
