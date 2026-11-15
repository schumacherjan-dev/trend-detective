"""
null_test.py - false-alarm check ("placebo test") for the trend pipeline.

The yearly values of every grid cell (full period) are shuffled in time. Shuffling destroys any real trend but keeps
each series' distribution. If the pipeline works, a shuffled data set should show about 5 % of cells as significant
without FDR correction and about none with FDR correction.
Two variants:
  same_perm: one random order of the years used for ALL cells (keeps the spatial structure, so neighbouring cells stay alike)
  indep:     every cell gets its own random order (cells independent)
Uses data.js (annual anomalies per cell). Written with AI assistance (Claude).
"""
import json, os, sys
import numpy as np
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_data import bh_fdr

NPERM = int(os.environ.get("NPERM", 200)); rng = np.random.default_rng(12345)
t = open("data.js", encoding="utf-8").read(); D = json.loads(t[t.index("{"):t.rindex("}")+1])["year"]
years = np.array(D["meta"]["years"], float)
rows = []
for k, v in D["vars"].items():
    A = np.array([[np.nan if x is None else x for x in c["a"]] for c in v["cells"]])
    ok = ~np.isnan(A).any(axis=0); yy = years[ok]; A = A[:, ok]
    for mode in ("same_perm", "indep"):
        raw, fdr = [], []
        for _ in range(NPERM):
            if mode == "same_perm":
                idx = rng.permutation(len(yy)); B = A[:, idx]
            else:
                B = np.array([row[rng.permutation(len(yy))] for row in A])
            p = np.array([stats.kendalltau(yy, row)[1] for row in B])
            raw.append(np.mean(p < 0.05) * 100); fdr.append(bh_fdr(p).sum())
        rows.append((k, mode, len(A), np.mean(raw), np.percentile(raw, 5), np.percentile(raw, 95), np.mean(fdr), np.max(fdr), np.mean(np.array(fdr) > 0) * 100))
        print(f"{k:18s} {mode:9s} cells={len(A):3d} | raw p<0.05: mean {np.mean(raw):4.1f} % (5-95 %: {np.percentile(raw,5):4.1f}-{np.percentile(raw,95):4.1f}) | FDR-significant cells: mean {np.mean(fdr):.2f}, max {np.max(fdr)}, runs with any: {np.mean(np.array(fdr)>0)*100:.0f} %")
import csv
with open("null_test.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["variable", "mode", "cells", "raw_sig_pct_mean", "raw_sig_pct_p5", "raw_sig_pct_p95", "fdr_sig_cells_mean", "fdr_sig_cells_max", "runs_with_any_fdr_pct"])
    for r in rows: w.writerow([r[0], r[1], r[2]] + [round(float(x), 3) for x in r[3:]])
