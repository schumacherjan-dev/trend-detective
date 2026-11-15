"""
fetch_cache.py - only downloads monthly series from NASA POWER into ./cache (no results files are touched).

Used to extend the analysis to the period 1981-2024 (sensitivity check on the start year).
Already downloaded points are skipped, so the script can be re-run after an interruption.

Written with AI assistance (Claude).
Examples:
  python fetch_cache.py --var T2M --step 2.5 --start 1981
  python fetch_cache.py --var PRECTOTCORR --step 2.5 --start 1981
  python fetch_cache.py --var GWETROOT --step 2.5 --start 1981
"""
import argparse
import numpy as np
from trend_grid import series_for_point

ap = argparse.ArgumentParser()
ap.add_argument("--var", required=True)
ap.add_argument("--step", type=float, default=2.5)
ap.add_argument("--start", type=int, default=1981)
ap.add_argument("--end", type=int, default=2024)
ap.add_argument("--lat-min", type=float, default=35)
ap.add_argument("--lat-max", type=float, default=70)
ap.add_argument("--lon-min", type=float, default=-10)
ap.add_argument("--lon-max", type=float, default=40)
ap.add_argument("--cache", default="cache")
a = ap.parse_args()

lats = np.arange(a.lat_min, a.lat_max + 1e-9, a.step)
lons = np.arange(a.lon_min, a.lon_max + 1e-9, a.step)
pts = [(la, lo) for la in lats for lo in lons]
failed = []
for i, (la, lo) in enumerate(pts, 1):
    try:
        series_for_point(a.var, la, lo, a.start, a.end, a.cache)
    except RuntimeError as e:
        failed.append((la, lo))
        print(f"  skipped {la}/{lo}: {e}")
    if i % 10 == 0 or i == len(pts):
        print(f"  {i}/{len(pts)}")
print(f"{a.var}: done, {len(pts) - len(failed)} points available, {len(failed)} skipped (e.g. soil moisture over sea is expected).")
