"""
build_data.py - Schritt 3: Daten fuer die HTML-Seite vorberechnen

Liest die zwischengespeicherten Monatsreihen (Ordner "cache", NASA POWER) und berechnet fuer jede
Gitterzelle und jede Variable:
  - Jahresanomalien (Jahresgang entfernt)
  - fuer jedes Startjahr (Ende fest, z. B. 2024): Steigung pro Jahrzehnt (Theil-Sen), p-Wert (Mann-Kendall),
    Signifikanz nach Benjamini-Hochberg (FDR) ueber alle Zellen
  - Signifikanzhorizont: kuerzeste Fensterlaenge, ab der der Trend auch fuer alle laengeren Fenster
    signifikant bleibt (einmal ohne, einmal mit FDR-Korrektur)
Ergebnis: data.js (wird von index.html geladen)

Hinweis zur KI-Nutzung (fuer das Feld "Use of Super Intelligence"):
Dieser Code wurde mit Hilfe von Claude (KI-Assistent von Anthropic) geschrieben.
Die Fragestellung und das Konzept stammen vom Teilnehmer.

Aufruf:  python build_data.py --step 5      (oder --step 2.5, wenn der feine Lauf fertig ist)
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

VARS = {
    "T2M": {
        "label": "Air temperature (2 m)", "unit": "°C",
        "desc": "Mean air temperature 2 m above the ground. From the NASA MERRA-2 reanalysis (a weather model that assimilates observations), delivered by NASA POWER. Not a station measurement.",
    },
    "PRECTOTCORR": {
        "label": "Precipitation", "unit": "mm/day",
        "desc": "Mean daily precipitation, bias-corrected. From the NASA MERRA-2 reanalysis via NASA POWER. Modelled precipitation is more uncertain than modelled temperature.",
    },
    "GWETROOT": {
        "label": "Soil moisture (root zone)", "unit": "0–1",
        "desc": "How saturated the soil is in the root zone: 0 = dry, 1 = saturated (model value). "
                "From the NASA MERRA-2 reanalysis via NASA POWER; a model value, not a measurement. Not defined over the sea.",
    },
    "QV2M": {
        "label": "Water vapour in the air", "unit": "g/kg",
        "desc": "How much water vapour each kilogram of air holds near the ground (specific humidity). "
                "Warmer air can hold more. From the NASA MERRA-2 reanalysis via NASA POWER.",
    },
    "RH2M": {
        "label": "Humidity of the air", "unit": "%",
        "desc": "How close the air near the ground is to being saturated with water vapour (relative humidity). "
                "It can fall even when the air holds more water, if the air warms faster. From the NASA MERRA-2 reanalysis via NASA POWER.",
    },
    "ALLSKY_SFC_SW_DWN": {
        "label": "Sunshine at the ground", "unit": "MJ/m²/day", "first": 1984,
        "desc": "Solar energy reaching each square metre of ground per day (all-sky shortwave radiation). More means sunnier. "
                "Satellite-based, available from 1984 only (so windows are at most 41 years long). NASA POWER uses two products: SRB until 2000 and CERES from 2001, so a small step around 2001 is possible.",
    },
    # --- "unusual months": derived from monthly values, whole year only ---------------------------------------------
    # Per calendar month, the 10 % warmest/coldest (or wettest/driest) of the first 30 years (1981-2010) set the threshold;
    # the yearly count of months beyond it is analysed like any other series. By definition about 1.2 such months per year in the baseline.
    # --- daily extremes: yearly counts of days, from the NASA POWER daily files (see daily_metrics.py / daily_counts.json), whole year only ----
    "D_HOT30": {
        "label": "Hot days (30 °C or more)", "unit": "days/year", "daily": "HOT30", "extreme": "daily", "seasons": ["year"],
        "desc": "Number of days per year with a daily maximum air temperature of 30 °C or more. Modelled grid-cell value from NASA MERRA-2 via NASA POWER; "
                "not validated against stations, and the grid-cell maximum is usually lower than a station's. In most of northern Europe the count is zero, so use the next variable there.",
    },
    "D_TX90": {
        "label": "Unusually hot days", "unit": "days/year", "daily": "TX90", "extreme": "daily", "seasons": ["year"],
        "desc": "Number of days per year whose daily maximum temperature is above the warmest 10 % of the same time of year in 1981-2010 (about 35 days per year in the baseline). "
                "Works everywhere, also where 30 °C is rare. Modelled grid-cell value from NASA MERRA-2 via NASA POWER; not validated against stations.",
    },
    "D_HEAVY": {
        "label": "Heavy-rain days", "unit": "days/year", "daily": "HEAVY", "extreme": "daily", "seasons": ["year"],
        "desc": "Number of days per year with more rain than the wettest 5 % of rainy days (at least 1 mm) in 1981-2010 at that cell (about 7 days per year in the baseline). "
                "Modelled grid-cell rain is smoother than a rain gauge, so intense local downpours are underestimated; not validated against stations.",
    },
    "D_CDD": {
        "label": "Longest dry spell", "unit": "days", "daily": "CDD", "extreme": "daily", "seasons": ["year"],
        "desc": "Length of the longest run of consecutive dry days (less than 1 mm of rain) within the year; about 26 days on average over the map. Modelled grid-cell rain from NASA MERRA-2 via NASA POWER, "
                "which is smoother than a rain gauge, so drizzle days and the exact lengths are uncertain; not validated against stations.",
    },
    "T2M_HOT": {
        "label": "Unusually warm months", "unit": "months/year", "source": "T2M", "extreme": "hi", "seasons": ["year"],
        "desc": "Number of months per year that are warmer than the warmest 10 % of the same calendar month in 1981-2010 (about 1.2 months per year by definition). "
                "Monthly means, not single hot days. Derived from the NASA MERRA-2 air temperature via NASA POWER.",
    },
    "T2M_COLD": {
        "label": "Unusually cold months", "unit": "months/year", "source": "T2M", "extreme": "lo", "seasons": ["year"],
        "desc": "Number of months per year that are colder than the coldest 10 % of the same calendar month in 1981-2010 (about 1.2 months per year by definition). "
                "Monthly means, not single cold days. Derived from the NASA MERRA-2 air temperature via NASA POWER.",
    },
    "P_WET": {
        "label": "Unusually wet months", "unit": "months/year", "source": "PRECTOTCORR", "extreme": "hi", "seasons": ["year"],
        "desc": "Number of months per year that are wetter than the wettest 10 % of the same calendar month in 1981-2010 (about 1.2 months per year by definition). "
                "Monthly totals, not single heavy-rain events. Derived from NASA MERRA-2 precipitation via NASA POWER.",
    },
    "P_DRY": {
        "label": "Unusually dry months", "unit": "months/year", "source": "PRECTOTCORR", "extreme": "lo", "seasons": ["year"],
        "desc": "Number of months per year that are drier than the driest 10 % of the same calendar month in 1981-2010 (about 1.2 months per year by definition). "
                "Monthly totals, not single dry spells. Derived from NASA MERRA-2 precipitation via NASA POWER.",
    },
}


DAILY = json.load(open("daily_counts.json")) if os.path.exists("daily_counts.json") else {}


def annual_anomalies(monthly):
    """Jahresgang entfernen (Monatsmittel abziehen), dann pro Jahr mitteln."""
    clim = monthly.groupby(monthly.index.month).transform("mean")
    anomalies = monthly - clim
    return anomalies.groupby(anomalies.index.year).mean()


def window_trend(years, values):
    """Steigung pro Jahrzehnt (Theil-Sen) und p-Wert (Kendall-tau gegen die Zeit = Mann-Kendall)."""
    slope = stats.theilslopes(values, years)[0] * 10
    if np.ptp(values) == 0:
        return float(slope), 1.0
    p = stats.kendalltau(years, values)[1]
    return float(slope), float(1.0 if np.isnan(p) else p)


def bh_fdr(p, alpha=0.05):
    """Benjamini-Hochberg: True fuer Zellen, die nach Korrektur fuer viele Tests signifikant sind."""
    p = np.asarray(p, dtype=float)
    mask = np.zeros(p.shape, dtype=bool)
    valid = ~np.isnan(p)
    pv = p[valid]
    m = len(pv)
    if m == 0:
        return mask
    order = np.argsort(pv)
    below = pv[order] <= alpha * (np.arange(1, m + 1) / m)
    rejected = np.zeros(m, dtype=bool)
    if below.any():
        rejected[order[: np.max(np.where(below)[0]) + 1]] = True
    mask[valid] = rejected
    return mask


def horizon(sig, window_lengths, i0=0):
    """Kuerzeste Fensterlaenge, ab der alle laengeren Fenster signifikant sind (None = nie).
    i0 = Index des laengsten Fensters, fuer das die Variable Daten hat (spaeter Beginn der Reihe)."""
    sig, window_lengths = sig[i0:], window_lengths[i0:]
    if not sig[0]:
        return None
    k = 0
    while k + 1 < len(sig) and sig[k + 1]:
        k += 1
    return int(window_lengths[k])


def rp(x):
    # p-values keep 3 significant digits (avoids tiny p collapsing to 0.0)
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else float(f"{float(x):.3g}")


def r(x, nd):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), nd)


SEASONS = {
    "year": {"label": "Whole year", "months": None},
    "djf": {"label": "Winter (Dec–Feb)", "months": (12, 1, 2)},
    "jja": {"label": "Summer (Jun–Aug)", "months": (6, 7, 8)},
    "mam": {"label": "Spring (Mar–May)", "months": (3, 4, 5)},
    "son": {"label": "Autumn (Sep–Nov)", "months": (9, 10, 11)},
}

# Latitude bands used for regional averages (all grid points of the band, sea included)
REGIONS = {
    "north": {"label": "Northern Europe, land (55–70°N)", "lat": (55.0, 70.0), "land": True},
    "central": {"label": "Central Europe, land (45–55°N)", "lat": (45.0, 55.0), "land": True},
    "south": {"label": "Southern Europe, land (35–45°N)", "lat": (35.0, 45.0), "land": True},
    "land": {"label": "Whole map, land only", "lat": (35.0, 70.0), "land": True},
    "sea": {"label": "Whole map, sea only", "lat": (35.0, 70.0), "land": False},
    "all": {"label": "Whole map, land and sea", "lat": (35.0, 70.0), "land": None},
}


def _load_land(path="land.js"):
    """Natural Earth land polygons (same file as the page uses) -> list of polygons, each a list of rings."""
    txt = open(path, encoding="utf-8").read()
    return json.loads(txt[txt.index("["):txt.rindex("]") + 1])


_LAND = None


def is_land(lat, lon):
    """True if the grid point (the point NASA POWER is asked for) lies on land (even-odd ray casting, holes included)."""
    global _LAND
    if _LAND is None:
        _LAND = _load_land()
    for poly in _LAND:
        inside = False
        for ring in poly:
            xs = [q[0] for q in ring]; ys = [q[1] for q in ring]
            if not (min(xs) <= lon <= max(xs) and min(ys) <= lat <= max(ys)):
                continue
            n = len(ring)
            for i in range(n - 1):
                x1, y1 = ring[i]; x2, y2 = ring[i + 1]
                if (y1 > lat) != (y2 > lat) and lon < (x2 - x1) * (lat - y1) / (y2 - y1) + x1:
                    inside = not inside
        if inside:
            return True
    return False


def in_region(c, rv):
    lo, hi = rv["lat"]
    ok = lo <= c["lat"] < hi or (hi >= 70.0 and c["lat"] == hi)
    return ok and (rv["land"] is None or rv["land"] == c["land"])


def seasonal_anomalies(monthly, season):
    """Jahresgang entfernen, dann pro Jahr bzw. pro Jahreszeit mitteln.
    Winter eines Jahres Y = Dez (Y-1) + Jan (Y) + Feb (Y); nur vollstaendige Winter zaehlen."""
    if SEASONS[season]["months"] is None:
        return annual_anomalies(monthly)
    clim = monthly.groupby(monthly.index.month).transform("mean")
    anom = monthly - clim
    months = SEASONS[season]["months"]
    anom = anom[anom.index.month.isin(months)]
    year = anom.index.year + (anom.index.month == 12).astype(int) if season == "djf" else anom.index.year
    g = anom.groupby(year)
    out = g.mean()
    out[g.count() < 3] = np.nan
    return out


def extreme_counts(monthly, kind, y_from, y_to):
    """Months per year beyond the 10 % threshold of the same calendar month (baseline y_from..y_to). kind 'hi' = above P90, 'lo' = below P10."""
    base = monthly.loc[str(y_from):str(y_to)]
    q = base.groupby(base.index.month).quantile(0.9 if kind == "hi" else 0.1)
    thr = q.reindex(monthly.index.month).values
    flag = (monthly.values > thr) if kind == "hi" else (monthly.values < thr)
    return pd.Series(flag.astype(int), index=monthly.index.year).groupby(level=0).sum().astype(float)


def series_for(info, monthly, season, years, base_start):
    """Yearly series of one cell: anomalies (ordinary variables) or counts of unusual months (derived variables)."""
    if info.get("extreme"):
        return extreme_counts(monthly, info["extreme"], base_start, base_start + 29).reindex(years)
    return seasonal_anomalies(monthly, season).reindex(years)


def window_p(years, values):
    """Mann-Kendall p only (used for the emergence curves)."""
    if np.ptp(values) == 0:
        return 1.0
    p = stats.kendalltau(years, values)[1]
    return float(1.0 if np.isnan(p) else p)


def emergence_year(sig, ends):
    """First end year from which the trend 'start..end' is significant for every later end year (None = not by the last year)."""
    k = None
    for j in range(len(ends) - 1, -1, -1):
        if sig[j]:
            k = ends[j]
        else:
            break
    return None if k is None else int(k)


def windowed(series, years_all, starts, end, min_start=0):
    s_list, p_list = [], []
    for st in starts:
        sub = series.loc[st:end].dropna()
        if st < min_start or len(sub) < 8:
            s_list.append(np.nan)
            p_list.append(np.nan)
        else:
            sl, p = window_trend(sub.index.values.astype(float), sub.values.astype(float))
            s_list.append(sl)
            p_list.append(p)
    return np.array(s_list), np.array(p_list)


def build_season(season, args, var_steps):
    first = args.start + (1 if season == "djf" else 0)   # Winter 1991 waere unvollstaendig
    starts = list(range(first, args.end - args.min_window + 2))
    window_lengths = [args.end - s + 1 for s in starts]
    years_all = list(range(first, args.end + 1))
    out = {"meta": {"season": season, "seasonLabel": SEASONS[season]["label"],
                    "start": first, "end": args.end, "years": years_all, "startYears": starts,
                    "windowLengths": window_lengths, "minWindow": args.min_window, "step": max(var_steps.values()),
                    "latMin": args.lat_min, "latMax": args.lat_max,
                    "lonMin": args.lon_min, "lonMax": args.lon_max},
           "vars": {}, "regions": {k: {"label": v["label"], "lat": list(v["lat"]), "land": v["land"], "vars": {}} for k, v in REGIONS.items()}}

    for var, info in VARS.items():
        if season not in info.get("seasons", list(SEASONS)):
            continue
        if info.get("daily") and not DAILY:
            continue
        step = var_steps[var]
        vfirst = info.get("first", 0) + (1 if (season == "djf" and "first" in info) else 0)
        i0 = next((i for i, st in enumerate(starts) if st >= vfirst), 0)
        lats = np.arange(args.lat_min, args.lat_max + 1e-9, step)
        lons = np.arange(args.lon_min, args.lon_max + 1e-9, step)
        cells = []
        for lat in lats:
            for lon in lons:
                if info.get("daily"):
                    arr = DAILY[info["daily"]].get("%g_%g" % (lat, lon))
                    if arr is None:
                        continue
                    annual = pd.Series(arr, index=range(1981, 1981 + len(arr)), dtype=float).reindex(years_all)
                else:
                    f = os.path.join(args.cache, f"{info.get('source', var)}_{lat:.2f}_{lon:.2f}_{args.start}_{args.end}.csv")
                    if not os.path.exists(f):
                        continue
                    monthly = pd.read_csv(f, index_col=0, parse_dates=True).iloc[:, 0]
                    annual = series_for(info, monthly, season, years_all, args.start)
                slopes, pvals = windowed(annual, years_all, starts, args.end, vfirst)
                cells.append({"lat": float(lat), "lon": float(lon), "land": is_land(float(lat), float(lon)), "annual": annual.values,
                              "slopes": slopes, "p": pvals})
        if not cells:
            print(f"{var}: keine Zellen im Cache gefunden")
            continue

        P = np.array([c["p"] for c in cells])
        F = np.zeros(P.shape, dtype=bool)
        for j in range(P.shape[1]):
            F[:, j] = bh_fdr(P[:, j])

        # emergence: start year fixed, end year moves; FDR over cells for every end year
        y0 = max(first, vfirst)
        ends = list(range(y0 + args.min_window - 1, args.end + 1))
        EP = np.full((len(cells), len(ends)), np.nan)
        for i, c in enumerate(cells):
            ser = pd.Series(c["annual"], index=years_all)
            for j, e in enumerate(ends):
                sub = ser.loc[y0:e].dropna()
                if len(sub) >= 8:
                    EP[i, j] = window_p(sub.index.values.astype(float), sub.values.astype(float))
        EF = np.zeros(EP.shape, dtype=bool)
        for j in range(EP.shape[1]):
            EF[:, j] = bh_fdr(EP[:, j])
        ER = np.nan_to_num(EP, nan=1.0) < 0.05
        emerge = {"y0": int(y0), "ends": ends, "fracF": [round(float(EF[:, j].mean()), 4) for j in range(len(ends))],
                  "fracR": [round(float(ER[:, j].mean()), 4) for j in range(len(ends))]}

        allslopes = np.abs(np.array([c["slopes"] for c in cells]))
        vmax = float(np.nanpercentile(allslopes[:, i0:i0 + 5], 98))

        out_cells = []
        n_h_raw = n_h_fdr = 0
        for i, c in enumerate(cells):
            raw_sig = [bool(x < 0.05) if not np.isnan(x) else False for x in c["p"]]
            h_raw = horizon(raw_sig, window_lengths, i0)
            h_fdr = horizon([bool(x) for x in F[i]], window_lengths, i0)
            n_h_raw += h_raw is not None
            n_h_fdr += h_fdr is not None
            out_cells.append({
                "lat": c["lat"], "lon": c["lon"], "l": int(c["land"]),
                "a": [r(x, 5) for x in c["annual"]],
                "s": [r(x, 5) for x in c["slopes"]],
                "p": [rp(x) for x in c["p"]],
                "f": [int(x) for x in F[i]],
                "hr": h_raw, "hf": h_fdr,
                "em": emergence_year(list(EF[i]), ends), "er": emergence_year(list(ER[i]), ends),
            })
        out["vars"][var] = {"label": info["label"], "unit": info["unit"], "desc": info["desc"],
                            "step": step, "vmax": round(vmax, 5), "i0": i0, "emerge": emerge, "cells": out_cells}
        if info.get("extreme"):
            out["vars"][var]["kind"] = "extreme"
        print(f"[{season}] {var}: {len(cells)} Zellen (Schritt {step:g}°) | Horizont: roh {n_h_raw}, FDR {n_h_fdr} "
              f"| Fenster {window_lengths[0]}..{window_lengths[-1]} Jahre")

        # Regionale Mittel: Mittel der Anomalien aller Zellen eines Breitenbandes, dann dieselbe Auswertung
        reg_series, reg_stats = {}, {}
        for rk, rv in REGIONS.items():
            sel = [c for c in cells if in_region(c, rv)]
            if not sel:
                continue
            mean = pd.Series(np.nanmean(np.array([c["annual"] for c in sel]), axis=0), index=years_all)
            sl, pv = windowed(mean, years_all, starts, args.end, vfirst)
            reg_series[rk] = mean
            reg_stats[rk] = (sl, pv, len(sel))
        keys = list(reg_stats)
        Fr = {k: np.zeros(len(starts), dtype=bool) for k in keys}
        for j in range(len(starts)):
            m = bh_fdr(np.array([reg_stats[k][1][j] for k in keys]))
            for ki, k in enumerate(keys):
                Fr[k][j] = m[ki]
        for k in keys:
            sl, pv, n = reg_stats[k]
            raw_sig = [bool(x < 0.05) if not np.isnan(x) else False for x in pv]
            out["regions"][k]["vars"][var] = {
                "n": n, "a": [r(x, 5) for x in reg_series[k].values], "s": [r(x, 5) for x in sl],
                "p": [rp(x) for x in pv], "f": [int(x) for x in Fr[k]],
                "hr": horizon(raw_sig, window_lengths, i0), "hf": horizon([bool(x) for x in Fr[k]], window_lengths, i0)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="cache")
    ap.add_argument("--step", type=float, default=5.0, help="Standard-Schrittweite fuer alle Variablen")
    ap.add_argument("--steps", default="", help='je Variable, z. B. "T2M=2.5,PRECTOTCORR=5,GWETROOT=5"')
    ap.add_argument("--lat-min", type=float, default=35)
    ap.add_argument("--lat-max", type=float, default=70)
    ap.add_argument("--lon-min", type=float, default=-10)
    ap.add_argument("--lon-max", type=float, default=40)
    ap.add_argument("--start", type=int, default=1991)
    ap.add_argument("--end", type=int, default=2024)
    ap.add_argument("--min-window", type=int, default=15, help="kuerzestes Fenster in Jahren")
    ap.add_argument("--out", default="data.js")
    ap.add_argument("--seasons", default="", help="comma list, e.g. year,djf (default: all); each season is written to parts/<season>.json")
    ap.add_argument("--assemble", action="store_true", help="assemble data.js from parts/ (always done when all seasons are built)")
    ap.add_argument("--assemble-only", action="store_true", help="only assemble data.js from the existing parts/*.json")
    args = ap.parse_args()

    var_steps = {v: args.step for v in VARS}
    for part in filter(None, args.steps.split(",")):
        k, val = part.split("=")
        var_steps[k.strip()] = float(val)

    chosen = [] if args.assemble_only else [sk for sk in SEASONS if not args.seasons or sk in args.seasons.split(",")]
    os.makedirs("parts", exist_ok=True)
    for sk in chosen:
        with open(os.path.join("parts", sk + ".json"), "w", encoding="utf-8") as fh:
            json.dump(build_season(sk, args, var_steps), fh, separators=(",", ":"))
    if args.seasons and not args.assemble and not args.assemble_only:
        print("Teile geschrieben:", chosen)
        return
    seasons = {sk: json.load(open(os.path.join("parts", sk + ".json"), encoding="utf-8")) for sk in SEASONS}
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write("window.APP_DATA_SEASONS = " + json.dumps(seasons, separators=(",", ":")) + ";\n")
    print(f"Geschrieben: {args.out} ({os.path.getsize(args.out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
