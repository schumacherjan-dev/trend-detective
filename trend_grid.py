"""
trend_grid.py - Schritt 2: Trend und Signifikanz fuer ein Gitter -> Karte

Ablauf:  Gitter ueber Europa -> pro Gitterpunkt Zeitreihe holen (NASA POWER)
         -> Jahresgang entfernen -> Steigung (Theil-Sen) + p-Wert (Mann-Kendall)
         -> Korrektur fuer viele Tests (Benjamini-Hochberg, FDR) -> Karte + CSV

Hinweis zur KI-Nutzung (fuer das Feld "Use of Super Intelligence"):
Dieser Code wurde mit Hilfe von Claude (KI-Assistent von Anthropic) geschrieben.
Die Fragestellung und das Konzept stammen vom Teilnehmer.

Beispiele:
  python trend_grid.py --demo                       # Test ohne Internet
  python trend_grid.py --var T2M                    # Europa, 5-Grad-Gitter (schnell)
  python trend_grid.py --var T2M --step 2.5         # feiner, dauert laenger
  python trend_grid.py --var PRECTOTCORR --cmap BrBG
Ergebnisse (Tabelle und Karte) landen im aktuellen Ordner, Rohdaten im Ordner "cache".
"""
import argparse
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm

from trend_point import UNITS, annual_anomalies, fetch_power, trend_stats


def series_for_point(var, lat, lon, start, end, cache_dir):
    """Monatsreihe aus dem Cache lesen oder bei NASA POWER holen (mit 3 Versuchen)."""
    os.makedirs(cache_dir, exist_ok=True)
    f = os.path.join(cache_dir, f"{var}_{lat:.2f}_{lon:.2f}_{start}_{end}.csv")
    if os.path.exists(f):
        return pd.read_csv(f, index_col=0, parse_dates=True).iloc[:, 0]
    last_error = None
    for attempt in range(3):
        try:
            s = fetch_power(lat, lon, var, start, end)
            s.to_csv(f)
            time.sleep(0.1)  # die Schnittstelle nicht ueberfordern
            return s
        except RuntimeError as e:
            last_error = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(last_error)


def demo_series_for_cell(rng, lat, start=1991, end=2024):
    """Kuenstliche Reihe: Trend waechst nach Norden, im Sueden-Osten ein Gebiet ohne Trend."""
    idx = pd.date_range(f"{start}-01-01", f"{end}-12-01", freq="MS")
    t = (idx.year - start) + (idx.month - 1) / 12
    trend_per_year = 0.02 + 0.001 * (lat - 35)
    values = 9 + 10 * np.sin(2 * np.pi * (idx.month - 4) / 12) + trend_per_year * t + rng.normal(0, 1.2, len(idx))
    return pd.Series(values, index=idx)


def bh_fdr(p, alpha=0.05):
    """Benjamini-Hochberg: True fuer Punkte, die nach Korrektur fuer viele Tests signifikant sind."""
    p = np.asarray(p, dtype=float)
    mask = np.zeros(p.shape, dtype=bool)
    valid = ~np.isnan(p)
    pv = p[valid]
    m = len(pv)
    if m == 0:
        return mask
    order = np.argsort(pv)
    thresholds = alpha * (np.arange(1, m + 1) / m)
    below = pv[order] <= thresholds
    rejected = np.zeros(m, dtype=bool)
    if below.any():
        k = np.max(np.where(below)[0])
        rejected[order[: k + 1]] = True
    mask[valid] = rejected
    return mask


def plot_map(df, var, unit, outfile, cmap, start, end):
    """Karte der Steigung pro Jahrzehnt; Punkte markieren signifikante Zellen (nach FDR)."""
    z = df.pivot(index="lat", columns="lon", values="slope_per_decade")
    s = df.pivot(index="lat", columns="lon", values="significant_fdr").fillna(False).astype(bool)
    lats, lons = z.index.values, z.columns.values
    vmax = np.nanmax(np.abs(z.values))
    vmax = vmax if vmax > 0 else 1.0
    norm = TwoSlopeNorm(vcenter=0, vmin=-vmax, vmax=vmax)
    cmap = plt.get_cmap(cmap).copy()
    cmap.set_bad("#d9d9d9")  # Zellen ohne Daten (z. B. Meer bei Bodenfeuchte) grau
    zvals = np.ma.masked_invalid(z.values)

    try:  # Kuestenlinien, wenn cartopy installiert ist (optional)
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature
        fig, ax = plt.subplots(figsize=(9, 6.5), subplot_kw={"projection": ccrs.PlateCarree()})
        transform = ccrs.PlateCarree()
        have_cartopy = True
    except Exception:
        fig, ax = plt.subplots(figsize=(9, 6.5))
        transform, have_cartopy = None, False

    kw = {"transform": transform} if have_cartopy else {}
    mesh = ax.pcolormesh(lons, lats, zvals, cmap=cmap, norm=norm, shading="nearest", **kw)
    yy, xx = np.meshgrid(lats, lons, indexing="ij")
    ax.scatter(xx[s.values], yy[s.values], s=14, c="k", marker=".", label="signifikant (FDR 5 %)", **kw)
    if have_cartopy:
        try:
            ax.add_feature(cfeature.COASTLINE, linewidth=0.6)
            ax.add_feature(cfeature.BORDERS, linewidth=0.3)
        except Exception:
            pass  # kein Internet fuer die Kuestendaten: Karte ohne Linien
    else:
        ax.set_xlabel("Laenge (°)")
        ax.set_ylabel("Breite (°)")
    cbar = fig.colorbar(mesh, ax=ax, shrink=0.8)
    cbar.set_label(f"Steigung pro Jahrzehnt, {unit}")
    ax.set_title(f"{var}: Trend {start}-{end} (Theil-Sen), Punkte = signifikant, grau = keine Daten", fontsize=10)
    ax.legend(loc="lower left", fontsize=8)
    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--var", default="T2M")
    ap.add_argument("--lat-min", type=float, default=35)
    ap.add_argument("--lat-max", type=float, default=70)
    ap.add_argument("--lon-min", type=float, default=-10)
    ap.add_argument("--lon-max", type=float, default=40)
    ap.add_argument("--step", type=float, default=5.0)
    ap.add_argument("--start", type=int, default=1991)
    ap.add_argument("--end", type=int, default=2024)
    ap.add_argument("--cmap", default="RdBu_r", help="z. B. RdBu_r (Temperatur), BrBG (Niederschlag)")
    ap.add_argument("--cache", default="cache")
    ap.add_argument("--demo", action="store_true", help="kuenstliche Daten, kein Internet")
    args = ap.parse_args()

    lats = np.arange(args.lat_min, args.lat_max + 1e-9, args.step)
    lons = np.arange(args.lon_min, args.lon_max + 1e-9, args.step)
    n = len(lats) * len(lons)
    print(f"Gitter: {len(lats)} x {len(lons)} = {n} Punkte")

    rng = np.random.default_rng(1)
    rows, failed = [], 0
    for i, (lat, lon) in enumerate(((a, b) for a in lats for b in lons), start=1):
        try:
            if args.demo:
                monthly = demo_series_for_cell(rng, lat, args.start, args.end)
            else:
                monthly = series_for_point(args.var, lat, lon, args.start, args.end, args.cache)
            res = trend_stats(annual_anomalies(monthly))
            rows.append({"lat": lat, "lon": lon, "slope_per_decade": res["slope_per_decade"],
                         "ci_low": res["ci_low_per_decade"], "ci_high": res["ci_high_per_decade"],
                         "p_value": res["p_value"], "n_years": res["n_years"]})
        except RuntimeError as e:
            failed += 1
            rows.append({"lat": lat, "lon": lon, "slope_per_decade": np.nan, "ci_low": np.nan,
                         "ci_high": np.nan, "p_value": np.nan, "n_years": 0})
            print(f"  Punkt {lat}/{lon} uebersprungen: {e}")
        if i % 10 == 0 or i == n:
            print(f"  {i}/{n} Punkte")

    df = pd.DataFrame(rows)
    df["significant_raw"] = df["p_value"] < 0.05
    df["significant_fdr"] = bh_fdr(df["p_value"].values, alpha=0.05)

    name = "DEMO" if args.demo else args.var
    unit = "Einheit" if args.demo else UNITS.get(args.var, "Einheit")
    step_txt = f"{args.step:g}deg"
    csv_out, png_out = f"results_{name}_{step_txt}.csv", f"map_{name}_{step_txt}.png"
    df.to_csv(csv_out, index=False)
    plot_map(df, name, unit, png_out, args.cmap, args.start, args.end)

    ok = df["p_value"].notna().sum()
    print(f"\nPunkte mit Ergebnis: {ok} (uebersprungen: {failed})")
    print(f"Signifikant ohne Korrektur (p<0,05): {int(df['significant_raw'].sum())}")
    print(f"Signifikant nach FDR-Korrektur:      {int(df['significant_fdr'].sum())}")
    print(f"Tabelle: {csv_out}")
    print(f"Karte:   {png_out}")


if __name__ == "__main__":
    main()
