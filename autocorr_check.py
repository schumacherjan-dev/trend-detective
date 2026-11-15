"""
autocorr_check.py - Robustness check: does serial correlation (year-to-year memory) change the results?

For every grid cell, full period: Theil-Sen slope, Mann-Kendall p-value (as in build_data.py) versus a
Mann-Kendall test whose variance is inflated by the lag-1 autocorrelation of the detrended series
(effective sample size n_eff = n (1 - r1) / (1 + r1), only for r1 > 0). Then Benjamini-Hochberg FDR across cells.

Also compares the Theil-Sen slope with an ordinary least squares (OLS) slope.

Written with AI assistance (Claude). Run:  python autocorr_check.py
"""
import os, sys
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_data import VARS, SEASONS, seasonal_anomalies, bh_fdr

START, END, STEP = int(os.environ.get("START", 1991)), 2024, 2.5
LATS = np.arange(35, 70 + 1e-9, STEP); LONS = np.arange(-10, 40 + 1e-9, STEP)

rows = []
for season in SEASONS:
    first = START + (1 if season == "djf" else 0)
    years = list(range(first, END + 1))
    for var in VARS:
        recs = []
        for lat in LATS:
            for lon in LONS:
                f = os.path.join("cache", f"{var}_{lat:.2f}_{lon:.2f}_{START}_{END}.csv")
                if not os.path.exists(f): continue
                m = pd.read_csv(f, index_col=0, parse_dates=True).iloc[:, 0]
                y = seasonal_anomalies(m, season).reindex(years).dropna()
                if len(y) < 20: continue
                x = y.index.values.astype(float); v = y.values.astype(float); n = len(v)
                ts = stats.theilslopes(v, x); ols = stats.linregress(x, v)
                res = v - (ts[1] + ts[0] * x)
                r1 = float(np.corrcoef(res[:-1], res[1:])[0, 1])
                tau, p_mk = stats.kendalltau(x, v)
                S = tau * n * (n - 1) / 2
                var_s = n * (n - 1) * (2 * n + 5) / 18
                infl = n / (n * (1 - r1) / (1 + r1)) if r1 > 0 else 1.0
                z = (S - np.sign(S)) / np.sqrt(var_s * infl)
                p_ac = 2 * (1 - stats.norm.cdf(abs(z)))
                recs.append(dict(season=season, variable=var, lat=lat, lon=lon, n=n,
                                 slope_ts_per_decade=ts[0] * 10, slope_ols_per_decade=ols.slope * 10,
                                 lag1_autocorr=r1, p_mk=p_mk, p_mk_autocorr=p_ac))
        if not recs: continue
        df = pd.DataFrame(recs)
        df["sig_fdr"] = bh_fdr(df.p_mk.values)
        df["sig_fdr_autocorr"] = bh_fdr(df.p_mk_autocorr.values)
        rows.append(df)
        corr = np.corrcoef(df.slope_ts_per_decade, df.slope_ols_per_decade)[0, 1]
        rel = np.median(np.abs(df.slope_ols_per_decade - df.slope_ts_per_decade) / np.maximum(np.abs(df.slope_ts_per_decade), 1e-9))
        print(f"[{season}] {var:12s} cells={len(df):3d}  FDR-sig: {int(df.sig_fdr.sum()):3d} -> with autocorr. correction: "
              f"{int(df.sig_fdr_autocorr.sum()):3d} | median lag-1 r={df.lag1_autocorr.median():+.2f} | "
              f"TS vs OLS: r={corr:.3f}, median rel. diff={rel*100:.0f}%")
out = pd.concat(rows)
out.to_csv("autocorr_check.csv", index=False, float_format="%.5g")
print("autocorr_check.csv:", len(out), "rows")
