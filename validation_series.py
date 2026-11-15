"""
validation_series.py - writes validation_series.js: measured series next to the matching NASA POWER series, for the overlay chart in index.html.

Measured: DWD (Germany: temperature, precipitation, sunshine duration), Met Office (UK: temperature, precipitation, sunshine duration), Met Eireann via CSO (Ireland: precipitation, mean of 8 stations), SMHI (Sweden: temperature), Berkeley Earth (Spain, Italy, Greece, Finland, Norway, Latvia and Lithuania: temperature),
the CSV files in this folder. POWER: mean of the yearly values of the grid points listed in the compare scripts (dwd_compare*.py, smhi_compare.py,
berkeley_compare.py), read from cache/. Both series are shown as deviations from their own mean over the years shown (sunshine: percent of the mean),
so only the year-to-year pattern and the trend are compared, not the level.
Written with AI assistance (Claude).
"""
import os, sys, json
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_data import annual_anomalies, window_trend

END = 2024
DE = ([47.5, 50.0, 52.5, 55.0], [7.5, 10.0, 12.5, 15.0]); SE = ([57.5, 60.0, 62.5, 65.0, 67.5], [12.5, 15.0, 17.5, 20.0])
ES = [(37.5, -5.0), (37.5, -2.5), (40.0, -5.0), (40.0, -2.5), (40.0, 0.0), (42.5, -5.0), (42.5, -2.5), (42.5, 0.0)]
IT = [(45.0, 7.5), (45.0, 10.0), (42.5, 12.5), (40.0, 15.0), (40.0, 17.5), (37.5, 15.0)]
GR = [(40.0, 22.5), (37.5, 22.5)]
# UK: cells with at least 50 % United Kingdom and at least 25 % land (cellinfo.js)
UK = [(50.0, -2.5), (52.5, -2.5), (52.5, 0.0), (55.0, -5.0), (55.0, -2.5), (57.5, -5.0), (57.5, -2.5)]
FI = [(60.0, 22.5), (60.0, 25.0), (62.5, 22.5), (62.5, 25.0), (62.5, 27.5), (62.5, 30.0), (65.0, 25.0), (65.0, 27.5), (65.0, 30.0), (67.5, 25.0), (67.5, 27.5), (70.0, 27.5)]
NO = [(57.5, 7.5), (60.0, 5.0), (60.0, 7.5), (60.0, 10.0), (62.5, 7.5), (62.5, 10.0), (65.0, 12.5), (67.5, 15.0), (70.0, 20.0), (70.0, 22.5), (70.0, 25.0), (70.0, 30.0)]
BA = [(55.0, 22.5), (55.0, 25.0), (57.5, 22.5), (57.5, 25.0)]   # Lithuania and Latvia (cells with at least 50 % of one of them)
# the same cell rule as for the UK: at least 50 % of the country and at least 25 % land (cellinfo.js)
IE = [(52.5, -10.0), (52.5, -7.5), (55.0, -7.5)]   # Ireland, same cell rule as above
grid = lambda box: [(la, lo) for la in box[0] for lo in box[1]]

def read(var, la, lo):
    return pd.read_csv(f"cache/{var}_{la:.2f}_{lo:.2f}_1981_2024.csv", index_col=0, parse_dates=True).iloc[:, 0]
def power_t(points): return pd.concat([annual_anomalies(read("T2M", la, lo)) for la, lo in points], axis=1).mean(axis=1)
def power_p(points): return pd.concat([annual_anomalies(read("PRECTOTCORR", la, lo)) * 365.25 for la, lo in points], axis=1).mean(axis=1)
def power_s(points):
    ser = []
    for la, lo in points:
        m = read("ALLSKY_SFC_SW_DWN", la, lo); g = m.groupby(m.index.year); ser.append(g.mean()[g.count() == 12])
    return pd.concat(ser, axis=1).mean(axis=1)

CASES = [
    ("de_t", "Germany, air temperature", "DWD national mean vs. POWER (16 grid points)", "°C", 1981, END, pd.read_csv("dwd_germany_annual.csv", index_col=0).iloc[:, 0], power_t(grid(DE)), False, ""),
    ("se_t", "Sweden, air temperature", "SMHI national mean vs. POWER (20 grid points)", "°C", 1981, END, pd.read_csv("smhi_sweden_annual.csv", index_col=0).iloc[:, 0], power_t(grid(SE)), False, ""),
]
ber = pd.read_csv("berkeley_south_europe_annual.csv", index_col=0)
bn = pd.read_csv("berkeley_north_europe_annual.csv", index_col=0)
uk = pd.read_csv("uk_metoffice_annual.csv", comment="#", index_col=0)
ie = pd.read_csv("ireland_meteireann_annual.csv", comment="#", index_col=0)
CASES += [("es_t", "Spain, air temperature", "Berkeley Earth vs. POWER (8 grid points)", "°C", 1981, 2020, ber["spain"], power_t(ES), False, ""),
          ("it_t", "Italy, air temperature", "Berkeley Earth vs. POWER (6 grid points)", "°C", 1981, 2020, ber["italy"], power_t(IT), False, ""),
          ("gr_t", "Greece, air temperature", "Berkeley Earth vs. POWER (2 grid points)", "°C", 1981, 2020, ber["greece"], power_t(GR), False, ""),
          ("fi_t", "Finland, air temperature", "Berkeley Earth vs. POWER (12 grid points)", "°C", 1981, 2020, bn["finland"], power_t(FI), False, ""),
          ("no_t", "Norway, air temperature", "Berkeley Earth vs. POWER (12 grid points)", "°C", 1981, 2020, bn["norway"], power_t(NO), False, ""),
          ("ba_t", "Latvia and Lithuania, air temperature", "Berkeley Earth (mean of both) vs. POWER (4 grid points)", "°C", 1981, 2020, (bn["latvia"] + bn["lithuania"]) / 2, power_t(BA), False, ""),
          ("ie_p", "Ireland, precipitation", "Met Eireann, mean of 8 stations vs. POWER (3 grid points)", "mm per year", 1981, 2022, ie["rain_mm"], power_p(IE), False, ""),
          ("de_s", "Germany, sunshine", "DWD sunshine duration vs. POWER surface radiation", "% of the mean", 1984, END, pd.read_csv("dwd_germany_annual_sunshine.csv", index_col=0).iloc[:, 0], power_s(grid(DE)), True,
           "Different quantities (hours of sun vs. energy). POWER is built from two satellite products that change in 2001."),
          ("de_p", "Germany, precipitation", "DWD national mean vs. POWER (16 grid points)", "mm per year", 1981, END, pd.read_csv("dwd_germany_annual_precip.csv", index_col=0).iloc[:, 0], power_p(grid(DE)), False,
           "The yearly swings match, but the direction of the trend does not."),
          ("uk_t", "United Kingdom, air temperature", "Met Office UK series (HadUK-Grid) vs. POWER (7 grid points)", "°C", 1981, END, uk["tmean_C"], power_t(UK), False, ""),
          ("uk_p", "United Kingdom, precipitation", "Met Office UK series (HadUK-Grid) vs. POWER (7 grid points)", "mm per year", 1981, END, uk["rain_mm"], power_p(UK), False,
           "Here the direction of the trend agrees (both slightly upward, neither significant)."),
          ("uk_s", "United Kingdom, sunshine", "Met Office sunshine duration vs. POWER surface radiation", "% of the mean", 1984, END, uk["sun_hours"], power_s(UK), True,
           "Different quantities (hours of sun vs. energy); the match is weaker than for Germany.")]
out = []
for cid, label, src, unit, a, b, meas, pw, rel, note in CASES:
    m = meas.loc[a:b].astype(float); p = pw.loc[a:b].astype(float); years = [int(y) for y in m.index]
    assert list(p.index) == list(m.index), cid
    sm, _ = window_trend(m.index.values.astype(float), m.values); sp, _ = window_trend(p.index.values.astype(float), p.values)
    r = float(np.corrcoef(m.values, p.values)[0, 1])
    if rel: sm, sp = 100 * sm / m.mean(), 100 * sp / p.mean(); mv, pv = 100 * (m / m.mean() - 1), 100 * (p / p.mean() - 1)
    else: mv, pv = m - m.mean(), p - p.mean()
    out.append({"id": cid, "label": label, "src": src, "unit": unit, "years": years, "measured": [round(float(v), 3) for v in mv], "power": [round(float(v), 3) for v in pv],
                "r": round(r, 2), "slopeM": round(float(sm), 2), "slopeP": round(float(sp), 2), "note": note})
    print(f"{cid}: {a}-{b} r={r:.2f} measured {sm:+.2f} POWER {sp:+.2f} per decade ({unit})")
open("validation_series.js", "w", encoding="utf-8").write("window.VALID=" + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")
print("validation_series.js written,", os.path.getsize("validation_series.js"), "bytes")
