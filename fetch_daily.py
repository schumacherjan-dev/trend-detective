#!/usr/bin/env python3
"""
fetch_daily.py - downloads DAILY values from NASA POWER for the 315-cell grid used by Trend Detective
(35-70 N, 10 W - 40 E, every 2.5 degrees) and stores them in ./cache_daily/<lat>_<lon>.csv.gz.

Variables: T2M_MAX (daily maximum air temperature at 2 m) and PRECTOTCORR (daily precipitation), 1981-2024.
Already downloaded cells are skipped, so the script can be stopped and started again at any time.
Failed requests are retried several times and then skipped (they are listed at the end).

Run in a Terminal on your own computer (the network must reach power.larc.nasa.gov):
  python3 fetch_daily.py --test        # one cell, shows how long a request takes
  caffeinate -i python3 fetch_daily.py # everything (caffeinate keeps a Mac awake)

Written with AI assistance (Claude).
"""
import argparse
import gzip
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
VARS = ["T2M_MAX", "PRECTOTCORR"]
OUT = "cache_daily"


def grid():
    lats = [35 + 2.5 * i for i in range(15)]          # 35 ... 70
    lons = [-10 + 2.5 * i for i in range(21)]         # -10 ... 40
    return [(la, lo) for la in lats for lo in lons]


def get_json(lat, lon, start, end):
    params = {"parameters": ",".join(VARS), "community": "AG", "longitude": lon, "latitude": lat,
              "start": start, "end": end, "format": "JSON"}
    try:
        import requests
        r = requests.get(URL, params=params, timeout=120)
        if r.status_code in (429, 500, 502, 503, 504):
            raise RuntimeError("HTTP %d" % r.status_code)
        r.raise_for_status()
        return r.json()
    except ImportError:
        import json
        import urllib.parse
        import urllib.request
        with urllib.request.urlopen(URL + "?" + urllib.parse.urlencode(params), timeout=120) as r:
            return json.loads(r.read())


def fetch_cell(lat, lon, start, end):
    path = os.path.join(OUT, "%.2f_%.2f.csv.gz" % (lat, lon))
    if os.path.exists(path):
        return path, 0.0, "skipped"
    last = None
    for attempt, wait in enumerate((0, 5, 15, 40, 90)):
        if wait:
            time.sleep(wait)
        t0 = time.time()
        try:
            P = get_json(lat, lon, start, end)["properties"]["parameter"]
            days = sorted(P[VARS[0]].keys())
            if len(days) < 15000:
                raise RuntimeError("only %d days returned" % len(days))
            tmp = path + ".part"
            with gzip.open(tmp, "wt") as f:
                f.write("date," + ",".join(VARS) + "\n")
                for d in days:
                    row = []
                    for v in VARS:
                        x = P[v].get(d)
                        row.append("" if x is None or x == -999 else "%g" % x)
                    f.write(d + "," + ",".join(row) + "\n")
            os.replace(tmp, path)
            return path, time.time() - t0, "ok"
        except Exception as e:                        # noqa: BLE001 - we retry on any problem
            last = repr(e)[:160]
    return path, 0.0, "FAILED: " + last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true", help="download one cell (52.5 N, 10 E) and stop")
    ap.add_argument("--workers", type=int, default=3, help="parallel requests (default 3, please stay polite)")
    ap.add_argument("--start", default="19810101")
    ap.add_argument("--end", default="20241231")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cells = [(52.5, 10.0)] if a.test else grid()
    todo = [c for c in cells if not os.path.exists(os.path.join(OUT, "%.2f_%.2f.csv.gz" % c))]
    print("cells total %d, still to download %d" % (len(cells), len(todo)), flush=True)
    t_start, done, failed = time.time(), 0, []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(fetch_cell, la, lo, a.start, a.end): (la, lo) for la, lo in todo}
        for fu in as_completed(futs):
            la, lo = futs[fu]
            path, sec, status = fu.result()
            done += 1
            if status.startswith("FAILED"):
                failed.append((la, lo, status))
            el = time.time() - t_start
            eta = el / done * (len(todo) - done)
            print("%3d/%d  %5.1fN %6.1fE  %-8s %5.1fs   elapsed %4.1f min, about %4.1f min left"
                  % (done, len(todo), la, lo, status[:8], sec, el / 60, eta / 60), flush=True)
    print("finished. downloaded: %d, failed: %d" % (done - len(failed), len(failed)))
    for la, lo, st in failed:
        print("  failed:", la, lo, st)
    if failed:
        print("Run the script again to retry the failed cells.")
        sys.exit(1)


if __name__ == "__main__":
    main()
