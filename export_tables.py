# Exports data.js to CSV tables: all_windows.csv, compare_variables.csv, regions.csv.
# Part of the NASA Space Apps 2026 project; written with AI assistance (Claude).
import json, csv, re
s = open("data.js", encoding="utf-8").read()
DS = json.loads(re.search(r"=\s*(\{.*\})\s*;", s, re.S).group(1))

with open("all_windows.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["season", "variable", "unit", "lat", "lon", "start_year", "end_year", "window_years",
                "slope_per_decade", "p_value", "significant_raw", "significant_fdr"])
    for se, D in DS.items():
        M = D["meta"]
        for k, v in D["vars"].items():
            for c in v["cells"]:
                for j, sy in enumerate(M["startYears"]):
                    if c["s"][j] is None: continue
                    w.writerow([se, k, v["unit"], c["lat"], c["lon"], sy, M["end"], M["windowLengths"][j],
                                round(c["s"][j], 5), c["p"][j], int(c["p"][j] < 0.05), c["f"][j]])

with open("compare_variables.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    first = DS["year"]
    hdr = ["season", "lat", "lon"]
    for k in first["vars"]: hdr += [f"{k}_slope_per_decade", f"{k}_p", f"{k}_sig_fdr", f"{k}_years_needed_fdr"]
    w.writerow(hdr)
    for se, D in DS.items():
        cells = {}
        for k, v in D["vars"].items():
            for c in v["cells"]:
                cells.setdefault((c["lat"], c["lon"]), {})[k] = c
        for (la, lo) in sorted(cells):
            row = [se, la, lo]
            for k in first["vars"]:
                c = cells[(la, lo)].get(k)
                i0 = first["vars"][k].get("i0", 0)   # first window this variable has data for
                if c is None or c["s"][i0] is None: row += ["", "", "", ""]
                else: row += [round(c["s"][i0], 5), c["p"][i0], c["f"][i0], "" if c["hf"] is None else c["hf"]]
            w.writerow(row)

with open("regions.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["season", "region", "variable", "n_grid_points", "window_years", "slope_per_decade", "p_value",
                "significant_fdr_over_regions", "years_needed_fdr"])
    for se, D in DS.items():
        M = D["meta"]
        for rk, rg in D["regions"].items():
            for k, c in rg["vars"].items():
                for j, sy in enumerate(M["startYears"]):
                    if c["s"][j] is None: continue
                    w.writerow([se, rg["label"], k, c["n"], M["windowLengths"][j], c["s"][j], c["p"][j], c["f"][j],
                                "" if c["hf"] is None else c["hf"]])
print("ok")
