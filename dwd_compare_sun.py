"""
dwd_compare_sun.py - plausibility check for solar radiation: NASA POWER ALLSKY_SFC_SW_DWN vs. DWD sunshine duration.

DWD data: Deutscher Wetterdienst, Climate Data Center, regional averages Germany, annual sunshine duration in hours
(opendata.dwd.de/climate_environment/CDC/regional_averages_DE/annual/sunshine_duration/regional_averages_sd_year.txt,
file dated 2026-11-02), column "Deutschland", copied into dwd_germany_annual_sunshine.csv.
Sunshine duration and radiation are different quantities (hours of direct sun vs. energy), so the comparison is
about the year-to-year pattern (correlation) and the relative trend (% of the mean per decade), not about the level.
POWER: mean over the same 16 grid points as in dwd_compare.py (47.5-55 N, 7.5-15 E); POWER radiation starts in 1984.
Written with AI assistance (Claude).
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_data import window_trend

dwd = pd.read_csv("dwd_germany_annual_sunshine.csv", index_col=0).iloc[:, 0]
LATS = [47.5, 50.0, 52.5, 55.0]; LONS = [7.5, 10.0, 12.5, 15.0]; END = 2024; START = 1984
ser = []
for la in LATS:
    for lo in LONS:
        m = pd.read_csv(f"cache/ALLSKY_SFC_SW_DWN_{la:.2f}_{lo:.2f}_1981_2024.csv", index_col=0, parse_dates=True).iloc[:, 0]
        g = m.groupby(m.index.year); ser.append(g.mean()[g.count() == 12])
pw = pd.concat(ser, axis=1).mean(axis=1).loc[START:END]
w = dwd.loc[START:END]
print(f"Germany {START}-{END}, DWD sunshine duration vs NASA POWER surface solar radiation\n")
for name, x, unit in (("DWD sunshine duration", w, "h"), ("POWER radiation", pw, "MJ/m2/day")):
    s, p = window_trend(x.index.values.astype(float), x.values.astype(float))
    print(f"{name}: mean {x.mean():.2f} {unit}, trend {s:+.3f} {unit}/decade = {100*s/x.mean():+.1f} % of the mean per decade (p={p:.3f})")
print(f"correlation of yearly values r = {np.corrcoef(w.values, pw.values)[0,1]:.2f}")
for a, b in ((START, 1999), (2000, END)):
    print(f"  {a}-{b}: r = {np.corrcoef(w.loc[a:b].values, pw.loc[a:b].values)[0,1]:.2f}")
