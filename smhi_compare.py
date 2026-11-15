"""
smhi_compare.py - plausibility check for Scandinavia: NASA POWER T2M vs. SMHI observed Sweden annual mean temperature.

SMHI data: Swedish Meteorological and Hydrological Institute, climate indicator "Temperatur", annual mean temperature
for Sweden (about 450 homogenised station series; https://www.smhi.se/klimat/klimatet-da-och-nu/klimatindikatorer/temperatur),
table view read on 2026-11-14, copied into smhi_sweden_annual.csv. Copyright SMHI.
POWER: mean of the yearly anomalies of the 20 grid points at 57.5-67.5 N and 12.5-20 E (an approximate box,
NOT the Swedish border: it contains sea, Norway and Finland).
Written with AI assistance (Claude).
"""
import os, sys
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_data import annual_anomalies, window_trend

dwd = pd.read_csv("smhi_sweden_annual.csv", index_col=0).iloc[:, 0]
LATS = [57.5, 60.0, 62.5, 65.0, 67.5]; LONS = [12.5, 15.0, 17.5, 20.0]
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

print("SMHI Sweden vs NASA POWER box (57.5-67.5N, 12.5-20E), Theil-Sen slope per decade, p = Mann-Kendall\n")
for start in (1991, 1981):
    w = dwd.loc[start:END]
    s, p = window_trend(w.index.values.astype(float), w.values.astype(float))
    line = f"{start}-{END}: SMHI {s:+.2f} C/decade (p={p:.1e})"
    pm = powermean(start)
    if pm is None:
        line += " | POWER: no cache for this start year yet"
    else:
        pm = pm.loc[start:END]
        s2, p2 = window_trend(pm.index.values.astype(float), pm.values.astype(float))
        r = np.corrcoef(w.values, pm.values)[0, 1]
        line += f" | POWER {s2:+.2f} C/decade (p={p2:.1e}) | correlation of yearly values r={r:.2f} | difference {s2 - s:+.2f}"
    print(line)
