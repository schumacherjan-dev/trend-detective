"""
cellinfo.py - facts about each 2.5 degree map cell: land share, countries by share of the cell's land, largest towns.

Countries: Natural Earth 1:50m admin-0 (public domain), via the npm package world-atlas.
Towns: GeoNames (CC BY 4.0), cities with more than 15,000 inhabitants, via the python package geonamescache.
Each cell is the box lat +-1.25, lon +-1.25 around the grid point (the cells drawn on the map).
Written with AI assistance (Claude).
Setup: npm install world-atlas topojson-client; convert node_modules/world-atlas/countries-50m.json to countries.geojson with topojson-client (feature of objects.countries); pip install shapely geonamescache.
"""
import json
import geonamescache
from shapely.geometry import shape, box
from shapely.strtree import STRtree

feats = json.load(open("countries.geojson"))["features"]
def fix(f):
    g = shape(f["geometry"])
    if f["properties"]["name"] == "Russia":   # the 50m polygon wraps around the antimeridian: unwrap longitudes (west of 0 -> +360)
        from shapely.ops import transform
        g = transform(lambda x, y, z=None: (x + 360 if x < 0 else x, y), g)
    return g.buffer(0) if not g.is_valid else g
geoms = [fix(f) for f in feats]; names = [f["properties"]["name"] for f in feats]
# Crimea: Natural Earth draws it as Russia; here it is assigned to Ukraine (internationally recognised borders). Rough box, only the Russia part inside it is moved.
CRIMEA = box(32.4, 44.3, 36.6, 46.25)
ri, ui = names.index("Russia"), names.index("Ukraine")
moved = geoms[ri].intersection(CRIMEA)
geoms[ri] = geoms[ri].difference(CRIMEA); geoms[ui] = geoms[ui].union(moved)
tree = STRtree(geoms)
gc = geonamescache.GeonamesCache(); cities = list(gc.get_cities().values()); cname = {k: v["name"] for k, v in gc.get_countries().items()}
ALIAS = {"Czech Republic": "Czechia", "Macedonia": "North Macedonia", "Russian Federation": "Russia", "Republic of Moldova": "Moldova", "Moldova, Republic of": "Moldova",
         "Bosnia and Herzegovina": "Bosnia and Herz.", "Vatican": "Vatican City"}
H = 1.25; out = {}
for lat in [35 + 2.5 * i for i in range(15)]:
    for lon in [-10 + 2.5 * i for i in range(21)]:
        b = box(lon - H, lat - H, lon + H, lat + H); area = b.area
        parts = {}
        for i in tree.query(b):
            a = geoms[i].intersection(b).area
            if a > 0: parts[names[i]] = parts.get(names[i], 0) + a
        land = sum(parts.values())
        cs = sorted(parts.items(), key=lambda kv: -kv[1])
        info = {"l": round(100 * min(land, area) / area)}
        info["c"] = [[n, round(100 * a / land)] for n, a in cs if land and a / land >= 0.05][:4]
        inbox = sorted([c for c in cities if lat - H <= c["latitude"] < lat + H and lon - H <= c["longitude"] < lon + H], key=lambda c: -c["population"])
        pl = []
        for c in inbox:   # skip suburbs and districts that lie within 0.4 degrees of a larger town already listed
            if all((c["latitude"] - q["latitude"]) ** 2 + (c["longitude"] - q["longitude"]) ** 2 > 0.4 ** 2 for q in pl): pl.append(c)
            if len(pl) == 3: break
        def town_country(c):
            """GeoNames country name, but None if it disagrees with the Natural Earth polygon the town lies in (disputed areas)."""
            gn = cname.get(c["countrycode"], c["countrycode"]); gn = ALIAS.get(gn, gn)
            from shapely.geometry import Point
            pt = Point(c["longitude"], c["latitude"]); hit = [names[i] for i in tree.query(pt) if geoms[i].contains(pt)]
            return None if (hit and hit[0] != gn and {gn, hit[0]} & {"Russia", "Ukraine"}) else gn   # only the Russia/Ukraine disagreement (Crimea) is left unlabelled
        info["p"] = [[c["name"], town_country(c), c["population"]] for c in pl]
        out[f"{lat:g}_{lon:g}"] = info
open("cellinfo.js", "w", encoding="utf-8").write("window.CELL_INFO=" + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")
print(len(out), "cells;", len(open("cellinfo.js", encoding="utf-8").read()) // 1024, "KB")
for k in ("47.5_12.5", "52.5_12.5", "40_-2.5", "60_17.5", "50_2.5", "37.5_-10", "70_20"): print(k, out[k])
