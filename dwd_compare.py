"""
dwd_compare.py - plausibility check: NASA POWER (MERRA-2 based) T2M trend vs. DWD observed Germany mean.

DWD data: Deutscher Wetterdienst, Climate Data Center, regional averages Germany, annual air temperature mean
(opendata.dwd.de/climate_environment/CDC/regional_averages_DE/annual/air_temperature_mean/regional_averages_tm_year.txt,
file dated 2026-11-02), column "Deutschland", copied into dwd_germany_annual.csv.
POWER: mean of the yearly anomalies of all 2.5-degree grid points at 47.5-55 N and 7.5-15 E (an approximate box,
NOT the German border: it contains some sea and neighbouring countries).
Written with AI assistance (Claude).
"""
import os, sys
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_data import annual_anomalies, window_trend

dwd = pd.read_csv("dwd_germany_annual.csv", index_col=0).iloc[:, 0]
LATS = [47.5, 50.0, 52.5, 55.0]; LONS = [7.5, 10.0, 12.5, 15.0]
END = 2024

def powermean(start):
    ser = []
    for la in LATS:
        for lo in LONS:
            f = f"cache/T2M_{la:.2f}_{lo:.2f}_{start}_{END}.csv"
            if not os.path.exists(f): return None
            m = pd.read_csv(f, index_col=0, parse_dates=True).iloc[:, 0]
            ser.append(annual_anomalies(m))
    return pd.concat(ser, axis=1).mean(axis=1)

print("DWD Germany vs NASA POWER box (47.5-55N, 7.5-15E), Theil-Sen slope per decade, p = Mann-Kendall\n")
for start in (1991, 1981):
    w = dwd.loc[start:END]
    s, p = window_trend(w.index.values.astype(float), w.values.astype(float))
    line = f"{start}-{END}: DWD {s:+.2f} C/decade (p={p:.1e})"
    pm = powermean(start)
    if pm is None:
        line += " | POWER: no cache for this start year yet"
    else:
        pm = pm.loc[start:END]
        s2, p2 = window_trend(pm.index.values.astype(float), pm.values.astype(float))
        r = np.corrcoef(w.values, pm.values)[0, 1]
        line += f" | POWER {s2:+.2f} C/decade (p={p2:.1e}) | correlation of yearly values r={r:.2f} | difference {s2 - s:+.2f}"
    print(line)
