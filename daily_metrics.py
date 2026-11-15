"""
daily_metrics.py - yearly counts of daily extremes from the NASA POWER daily files (cache_daily/, T2M_MAX and PRECTOTCORR).
Output: daily_counts.json  {metric: {"<lat>_<lon>": [count per year 1981..2024]}}

  HOT30   days per year with daily maximum temperature >= 30 degC (absolute; zero in most of northern Europe)
  TX90    days per year above the 90th percentile of the daily maximum of the same calendar day (+-7 days window), baseline 1981-2010
          (by construction about 36.5 days per year in the baseline)
  HEAVY   days per year with precipitation above the 95th percentile of wet days (>= 1 mm) in 1981-2010 (per cell)
  CDD     longest run of consecutive dry days (< 1 mm) within a calendar year

Written with AI assistance (Claude).
"""
import gzip, json, os, sys
import numpy as np
import pandas as pd

Y0, Y1, B0, B1 = 1981, 2024, 1981, 2010
YEARS = list(range(Y0, Y1 + 1))
CUM = np.cumsum([0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30])   # leap-year calendar index (Feb 29 = slot 59)

def cal_index(dates):
    m = dates.month.values; d = dates.day.values
    return CUM[m - 1] + d - 1                                        # 0..365

def calendar_matrix(vals, years, idx):
    M = np.full((len(YEARS), 366), np.nan)
    M[years - Y0, idx] = vals
    return M

def tx90_threshold(M):
    base = M[: B1 - B0 + 1]
    thr = np.full(366, np.nan)
    for d in range(366):
        w = [(d + k) % 366 for k in range(-7, 8)]
        pool = base[:, w].ravel(); pool = pool[~np.isnan(pool)]
        thr[d] = np.percentile(pool, 90)
    return thr

def main():
    files = sorted(f for f in os.listdir("cache_daily") if f.endswith(".csv.gz"))
    out = {"HOT30": {}, "TX90": {}, "HEAVY": {}, "CDD": {}}
    for n, f in enumerate(files):
        lat, lon = f[:-7].split("_")
        key = "%g_%g" % (float(lat), float(lon))
        df = pd.read_csv(os.path.join("cache_daily", f), dtype={"date": str})
        dt = pd.to_datetime(df["date"], format="%Y%m%d")
        years = dt.dt.year.values; idx = cal_index(dt.dt)
        tx = df["T2M_MAX"].values.astype(float); pr = df["PRECTOTCORR"].values.astype(float)
        cnt = lambda flag: [int(flag[years == y].sum()) for y in YEARS]
        out["HOT30"][key] = cnt(tx >= 30)
        thr = tx90_threshold(calendar_matrix(tx, years, idx))
        out["TX90"][key] = cnt(tx > thr[idx])
        def longest_dry(y):
            run = best = 0
            for x in pr[years == y]:
                if x < 1: run += 1; best = max(best, run)
                else: run = 0
            return best
        out["CDD"][key] = [longest_dry(y) for y in YEARS]
        base = (years >= B0) & (years <= B1) & (pr >= 1)
        if base.sum() >= 100:
            p95 = np.percentile(pr[base], 95)
            out["HEAVY"][key] = cnt(pr > p95)
        else:
            out["HEAVY"][key] = None
    json.dump(out, open("daily_counts.json", "w"), separators=(",", ":"))
    print("cells", len(files))
    for m in out:
        a = np.array([v for v in out[m].values() if v is not None], dtype=float)
        print(m, "cells", len(a), "mean/yr 1981-90: %.1f  2015-24: %.1f" % (a[:, :10].mean(), a[:, -10:].mean()),
              " baseline 1981-2010 mean: %.1f" % a[:, :30].mean())

main()
