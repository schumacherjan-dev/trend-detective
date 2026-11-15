"""
dwd_compare_precip.py - plausibility check for precipitation: NASA POWER PRECTOTCORR vs. DWD observed Germany mean.

DWD data: Deutscher Wetterdienst, Climate Data Center, regional averages Germany, annual precipitation sum
(opendata.dwd.de/climate_environment/CDC/regional_averages_DE/annual/precipitation/regional_averages_rr_year.txt,
file dated 2026-11-02), column "Deutschland", copied into dwd_germany_annual_precip.csv (mm per year).
POWER: mean over the same 16 grid points as in dwd_compare.py (47.5-55 N, 7.5-15 E), mm/day anomalies x 365 = mm/year.
Written with AI assistance (Claude).
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_data import annual_anomalies, window_trend

dwd = pd.read_csv("dwd_germany_annual_precip.csv", index_col=0).iloc[:, 0]
LATS = [47.5, 50.0, 52.5, 55.0]; LONS = [7.5, 10.0, 12.5, 15.0]; END = 2024

def powermean(start):
    ser = []
    for la in LATS:
        for lo in LONS:
            f = f"cache/PRECTOTCORR_{la:.2f}_{lo:.2f}_{start}_{END}.csv"
            if not os.path.exists(f): return None
            ser.append(annual_anomalies(pd.read_csv(f, index_col=0, parse_dates=True).iloc[:, 0]) * 365.25)
    return pd.concat(ser, axis=1).mean(axis=1)

print("DWD Germany vs NASA POWER box: precipitation, Theil-Sen slope in mm/year per decade, p = Mann-Kendall\n")
for start in (1991, 1981):
    w = dwd.loc[start:END]
    s, p = window_trend(w.index.values.astype(float), w.values.astype(float))
    line = f"{start}-{END}: DWD {s:+.1f} mm/decade (p={p:.2f})"
    pm = powermean(start)
    if pm is None:
        line += " | POWER: no cache for this start year yet"
    else:
        pm = pm.loc[start:END]
        s2, p2 = window_trend(pm.index.values.astype(float), pm.values.astype(float))
        r = np.corrcoef(w.values, pm.values)[0, 1]
        line += f" | POWER {s2:+.1f} mm/decade (p={p2:.2f}) | correlation of yearly values r={r:.2f} | mean level: DWD {w.mean():.0f} mm vs POWER {pm.mean() + 0:.0f} (anomaly mean)"
    print(line)
