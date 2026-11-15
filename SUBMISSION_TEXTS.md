# Texts for the submission form (all English)

## Project title
Trend Detective: how long must we wait before a climate trend can be trusted?

## Short summary (one to two sentences)
Most tools show what changed. Trend Detective shows how long you need to wait before you can trust it: for 315 grid points over Europe it maps NASA POWER trends, tests their significance, and shows how many years of data, and which end year, were needed before the signal stood out from natural variability.

## Detailed description
Trend Detective is an interactive web page (no server, no login) built on NASA POWER monthly data for 1981–2024: air temperature, precipitation, root-zone soil moisture, specific and relative humidity, and sunshine at the ground, plus counts of unusually warm, cold, wet and dry months. For each of 315 grid points it shows what changes, where, how much, and whether the change is significant (Theil–Sen trend per decade, Mann–Kendall test, Benjamini–Hochberg correction over cells).

The new part is the time dimension of certainty. "Years needed" is the shortest window from which a trend stays significant for every longer window. "Year the trend became detectable" fixes the start in 1981 and moves the end year, so one sees when the signal emerged: for air temperature 20 % of the cells by 2005, 86 % by 2015, 100 % by 2024; for precipitation almost none. A planner turns this around for decision makers: choose the size of change you care about and read how many years of measurement you would need at that place. The smallest detectable trend explains why "not significant" does not mean "no change": for precipitation in the typical cell a trend would have to exceed ±0.096 mm/day per decade to be detected over 44 years, while the typical fitted trend is 0.030.

We validated against measured series (DWD, SMHI, Berkeley Earth) and show where it fails: German precipitation matches in its yearly swings (r = 0.85) but not in the direction of the trend. Robustness checks (autocorrelation, placebo test, start-year test) are reported on the page, together with a list of ideas we tested and deliberately excluded. Nothing on the page is a forecast.

## How it addresses the challenge
It examines variables produced by NASA models and satellites (NASA POWER: MERRA-2, SRB, CERES), visualises how they change over time, and determines what is changing, where, how much, and whether the change is significant. It covers several parts of the Earth system (atmosphere, water cycle, land, energy) and shows regional differences, for example opposite signs of the median winter precipitation trend north and south of 45°N, none of them significant.

## Use of Super Intelligence (AI use)
The question, the concept and every decision on what to build or to exclude are mine. The code was written with Claude (Anthropic), and the concept and plan were partly discussed with another AI assistant. I checked all statements on the page against our own data and removed claims the data did not support. Numbers on the page are computed from the data file; the scripts to rebuild it are in the repository.

## References (external resources)
- NASA POWER (Prediction Of Worldwide Energy Resources), monthly point data, https://power.larc.nasa.gov (open NASA data; acknowledgement: data obtained from the NASA Langley Research Center (LaRC) POWER Project funded through the NASA Earth Science/Applied Science Program)
- MERRA-2 reanalysis (NASA Global Modeling and Assimilation Office), via NASA POWER
- SRB (Surface Radiation Budget) and CERES satellite products, via NASA POWER
- Deutscher Wetterdienst (DWD) open climate data (CC BY 4.0): Germany annual temperature, precipitation, sunshine duration
- SMHI open data (CC BY 4.0): Sweden annual temperature
- Met Office UK and regional series (Open Government Licence v3.0, Crown copyright): UK temperature, precipitation, sunshine
- Met Éireann via CSO PxStat table MTM01 (CC BY 4.0): Ireland monthly rainfall, 8 stations
- Berkeley Earth regional temperature series (CC BY-NC 4.0, non-commercial use; www.berkeleyearth.org): Spain, Italy, Greece, Finland, Norway, Latvia, Lithuania
- Natural Earth land outlines (public domain)
- GeoNames place names (CC BY 4.0)
- Python libraries NumPy, pandas, SciPy (BSD licences)
- Statistical methods: Theil–Sen estimator, Mann–Kendall test, Benjamini–Hochberg procedure
- AI assistants: Claude (Anthropic) for code; another AI assistant for concept discussion
No unlicensed copyrighted material was used.

## Demo: 7 slides (maximum)
1. **Question:** "Most tools show what changed. We show how long you need to wait before you can trust it." One map, one number (315 cells).
2. **Why it matters:** Oslo 2015–2024: −0.27 °C per decade (cooling, not significant); 44 years: +0.31. Short windows mislead.
3. **Data and method:** NASA POWER (MERRA-2, SRB/CERES), Theil–Sen, Mann–Kendall, FDR; Years needed definition in one sentence.
4. **Finding 1:** Temperature emerges early and everywhere (20 % of cells by 2005, 86 % by 2015); precipitation, soil moisture almost nowhere. Screenshot of the emergence map and the line chart.
5. **Finding 2 (new):** Unusually hot days (daily maximum above the local warmest 10 %): about 28 per year in 1981–1990, 68 in 2015–2024; significant in 314 of 315 cells, typical cell needs 27 years. Experimental: modelled, not validated against stations.
5b. **Finding 2:** Unusual months: warm months 0.9 to 3.8 per year (3.2 times normal); "new normal" sentence (172 of 315 cells).
6. **For decisions:** smallest detectable trend and the planner (precipitation ±0.096 mm/day per decade vs 0.030 fitted); three users: water managers, city planners, teachers.
7. **Honesty and limits:** German precipitation validation fails in direction (r = 0.85); autocorrelation: 305 / 9 / 2 / 301 / 5 / 199; no forecast; link to the page and repository.
