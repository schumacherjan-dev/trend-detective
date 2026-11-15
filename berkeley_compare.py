"""
berkeley_compare.py - plausibility check for temperature in southern Europe: NASA POWER T2M vs. Berkeley Earth country series.

Berkeley Earth: land-surface temperature, regional summaries for Spain, Italy and Greece
(berkeley-earth-temperature.s3.us-west-1.amazonaws.com/Regional/TAVG/<country>-TAVG-Trend.txt, analysis run 06-Jan-2021,
so the series ends in 2020). Annual means of the 12 monthly anomalies, copied into berkeley_south_europe_annual.csv
(values checked against sums computed from the source files).
POWER: mean of the annual anomalies of the grid points that lie on land in each country (2.5 degree grid, listed below).
Both are anomalies, so only the year-to-year pattern and the trend are compared, not the level.
Written with AI assistance (Claude).
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_data import annual_anomalies, window_trend

ref = pd.read_csv("berkeley_south_europe_annual.csv", index_col=0)
POINTS = {
    "spain": [(37.5, -5.0), (37.5, -2.5), (40.0, -5.0), (40.0, -2.5), (40.0, 0.0), (42.5, -5.0), (42.5, -2.5), (42.5, 0.0)],
    "italy": [(45.0, 7.5), (45.0, 10.0), (42.5, 12.5), (40.0, 15.0), (40.0, 17.5), (37.5, 15.0)],
    "greece": [(40.0, 22.5), (37.5, 22.5)],
}
START, END = 1981, 2020
print(f"NASA POWER T2M vs Berkeley Earth, {START}-{END}, Theil-Sen slope per decade (p = Mann-Kendall)\n")
for c, pts in POINTS.items():
    ser = [annual_anomalies(pd.read_csv(f"cache/T2M_{la:.2f}_{lo:.2f}_1981_2024.csv", index_col=0, parse_dates=True).iloc[:, 0]) for la, lo in pts]
    pw = pd.concat(ser, axis=1).mean(axis=1).loc[START:END]
    b = ref[c].loc[START:END]
    sb, pb = window_trend(b.index.values.astype(float), b.values.astype(float))
    sp, pp = window_trend(pw.index.values.astype(float), pw.values.astype(float))
    r = np.corrcoef(b.values, pw.values)[0, 1]
    print(f"{c:7s} ({len(pts)} grid points): Berkeley {sb:+.2f} C/decade (p={pb:.3f}) | POWER {sp:+.2f} C/decade (p={pp:.3f}) | r = {r:.2f}")
