"""
trend_point.py - Trend und Signifikanz fuer EINEN Punkt (Schritt 1 des Tools)

Ablauf:  Zeitreihe -> Jahresgang entfernen -> Jahresmittel -> Steigung (Theil-Sen)
         -> p-Wert (Mann-Kendall / Kendall-tau-Test) -> Grafik

Daten:   NASA POWER (monatlich, Punktabfrage, kein Login noetig)

Hinweis zur KI-Nutzung (fuer das Feld "Use of Super Intelligence"):
Dieser Code wurde mit Hilfe von Claude (KI-Assistent von Anthropic) geschrieben.
Die Fragestellung und das Konzept stammen vom Teilnehmer.

Beispiele:
  python trend_point.py --lat 48.1 --lon 11.6 --var T2M
  python trend_point.py --lat 48.1 --lon 11.6 --var PRECTOTCORR --start 1991 --end 2024
  python trend_point.py --demo          # Test ohne Internet mit kuenstlichen Daten
"""
import argparse
import sys

import matplotlib
matplotlib.use("Agg")  # Grafik in Datei speichern, kein Fenster noetig
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

POWER_URL = "https://power.larc.nasa.gov/api/temporal/monthly/point"

UNITS = {
    "T2M": "°C (Lufttemperatur in 2 m)",
    "PRECTOTCORR": "mm/Tag (Niederschlag, korrigiert)",
    "GWETROOT": "0-1 (Bodenfeuchte Wurzelzone, Modellwert)",
}


def fetch_power(lat, lon, var, start, end):
    """Monatswerte einer Variablen von NASA POWER holen -> pandas Series (Index = Datum)."""
    import requests

    params = {
        "parameters": var,
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": start,
        "end": end,
        "format": "JSON",
    }
    try:
        r = requests.get(POWER_URL, params=params, timeout=60)
        r.raise_for_status()
        data = r.json()["properties"]["parameter"][var]
    except Exception as e:
        raise RuntimeError(f"Abfrage bei NASA POWER fehlgeschlagen: {e}")

    rows = []
    for key, value in data.items():
        year, month = int(key[:4]), int(key[4:])
        if month == 13:          # POWER liefert zusaetzlich einen Jahreswert (Monat 13)
            continue
        if value == -999:        # fehlender Wert
            continue
        rows.append((pd.Timestamp(year=year, month=month, day=1), value))
    s = pd.Series(dict(rows)).sort_index()
    if s.empty:
        raise RuntimeError("Keine Daten erhalten. Pruefe Variable, Ort und Zeitraum.")
    return s


def annual_anomalies(monthly):
    """Jahresgang entfernen (Monatsmittel abziehen) und dann pro Jahr mitteln."""
    clim = monthly.groupby(monthly.index.month).transform("mean")
    anomalies = monthly - clim
    return anomalies.groupby(anomalies.index.year).mean()


def trend_stats(annual):
    """Steigung pro Jahrzehnt (Theil-Sen) und p-Wert (Kendall-tau gegen die Zeit = Mann-Kendall)."""
    years = annual.index.values.astype(float)
    values = annual.values.astype(float)
    slope, intercept, lo, hi = stats.theilslopes(values, years)
    tau, p = stats.kendalltau(years, values)
    return {
        "slope_per_decade": slope * 10,
        "ci_low_per_decade": lo * 10,
        "ci_high_per_decade": hi * 10,
        "p_value": p,
        "n_years": len(values),
        "intercept": intercept,
    }


def plot_result(annual, res, title, unit, outfile):
    years = annual.index.values
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(years, annual.values, "o-", color="#1f6f8b", label="Jahresmittel (Anomalie)")
    ax.plot(years, res["intercept"] + res["slope_per_decade"] / 10 * years,
            color="#d1495b", lw=2, label="Trend (Theil-Sen)")
    sig = "signifikant" if res["p_value"] < 0.05 else "nicht signifikant"
    ax.set_title(f"{title}\n{res['slope_per_decade']:+.3f} pro Jahrzehnt, "
                 f"p = {res['p_value']:.3f} ({sig}, 5 %-Niveau)", fontsize=11)
    ax.set_xlabel("Jahr")
    ax.set_ylabel(f"Anomalie in {unit}")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)


def demo_series():
    """Kuenstliche Monatsreihe mit Jahresgang, Trend (+0.4 pro Jahrzehnt) und Rauschen."""
    rng = np.random.default_rng(42)
    idx = pd.date_range("1991-01-01", "2024-12-01", freq="MS")
    t = (idx.year - 1991) + (idx.month - 1) / 12
    values = 9 + 10 * np.sin(2 * np.pi * (idx.month - 4) / 12) + 0.04 * t + rng.normal(0, 1.0, len(idx))
    return pd.Series(values, index=idx)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lat", type=float, default=48.1)
    ap.add_argument("--lon", type=float, default=11.6)
    ap.add_argument("--var", default="T2M")
    ap.add_argument("--start", type=int, default=1991)
    ap.add_argument("--end", type=int, default=2024)
    ap.add_argument("--demo", action="store_true", help="kuenstliche Daten, kein Internet")
    args = ap.parse_args()

    if args.demo:
        monthly = demo_series()
        title, unit, out = "DEMO (kuenstliche Daten)", "Einheit", "trend_demo.png"
    else:
        try:
            monthly = fetch_power(args.lat, args.lon, args.var, args.start, args.end)
        except RuntimeError as e:
            sys.exit(str(e))
        unit = UNITS.get(args.var, "Einheit")
        title = f"{args.var} bei {args.lat:.1f}N, {args.lon:.1f}E ({args.start}-{args.end})"
        out = f"trend_{args.var}_{args.lat:.1f}_{args.lon:.1f}.png"

    annual = annual_anomalies(monthly)
    res = trend_stats(annual)
    plot_result(annual, res, title, unit, out)

    print(f"Jahre:      {res['n_years']}")
    print(f"Steigung:   {res['slope_per_decade']:+.3f} pro Jahrzehnt "
          f"(Konfidenzintervall {res['ci_low_per_decade']:+.3f} bis {res['ci_high_per_decade']:+.3f})")
    print(f"p-Wert:     {res['p_value']:.4f}  ->  "
          f"{'signifikant' if res['p_value'] < 0.05 else 'nicht signifikant'} (5 %-Niveau)")
    print(f"Grafik:     {out}")


if __name__ == "__main__":
    main()
