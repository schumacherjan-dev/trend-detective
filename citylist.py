"""
citylist.py - searchable place list for the map (cities.js): GeoNames cities with more than 15,000 inhabitants inside the map area.
Source: GeoNames (CC BY 4.0) via the python package geonamescache. Written with AI assistance (Claude).
"""
import geonamescache, json
gc = geonamescache.GeonamesCache(); cs = list(gc.get_cities().values()); cn = {k: v["name"] for k, v in gc.get_countries().items()}
cn["NL"] = "Netherlands"; cn["GB"] = "United Kingdom"; cn["RU"] = "Russia"; cn["VA"] = "Vatican City"
H = 1.25
sel = [c for c in cs if 35 - H <= c["latitude"] < 70 + H and -10 - H <= c["longitude"] < 40 + H]
# well-known English/local name pairs (only used if GeoNames lists the alternative name for that city)
WANT = ["Köln", "Cologne", "München", "Munich", "Wien", "Vienna", "Praha", "Prague", "Warszawa", "Warsaw", "Roma", "Rome", "Milano", "Milan", "Napoli", "Naples", "Firenze", "Florence",
        "Venezia", "Venice", "Torino", "Turin", "Genova", "Genoa", "Lisboa", "Lisbon", "Moskva", "Moscow", "Kiev", "Kyiv", "Athína", "Athens", "Athina", "København", "Copenhagen", "Göteborg",
        "Gothenburg", "Bruxelles", "Brussels", "Brussel", "Antwerpen", "Antwerp", "Anvers", "Den Haag", "The Hague", "Nürnberg", "Nuremberg", "Sevilla", "Seville", "București", "Bucharest",
        "Beograd", "Belgrade", "Zürich", "Zurich", "Genève", "Geneva", "Gdańsk", "Danzig", "Kraków", "Krakow", "Wrocław", "Breslau", "Hannover", "Hanover", "Lyon", "Marseille", "Sankt-Peterburg",
        "Saint Petersburg", "Istanbul", "İstanbul", "Thessaloníki", "Thessaloniki", "Salonica", "Bratislava", "Pressburg", "Ljubljana", "Zagreb", "Tallinn", "Riga", "Vilnius", "Helsinki",
        "Köbenhavn", "Malmö", "Wien", "Lisbon", "Porto", "Oporto", "Cádiz", "Bruges", "Brugge", "Gent", "Ghent", "Liège", "Luik", "Lüttich", "Aachen", "Aix-la-Chapelle", "Tórshavn", "Reykjavik"]
WL = set(WANT)
out = []; kept = []
for c in sorted(sel, key=lambda c: -c["population"]):
    # drop districts that GeoNames lists as cities (e.g. Hamburg-Nord, Hamburg-Mitte): same-prefix name right next to a larger town
    if any(c["name"].startswith(k["name"] + "-") or c["name"].startswith(k["name"] + " ") for k in kept if abs(k["latitude"] - c["latitude"]) < 0.5 and abs(k["longitude"] - c["longitude"]) < 0.5): continue
    kept.append(c)
    al = [a for a in c["alternatenames"] if a in WL and a != c["name"]][:3]
    row = [c["name"], round(c["latitude"], 3), round(c["longitude"], 3), cn.get(c["countrycode"], c["countrycode"]), c["population"]]
    if al: row.append(" ".join(al))
    out.append(row)
open("cities.js", "w", encoding="utf-8").write("window.CITY_LIST=" + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")
import os; print(len(out), "places;", os.path.getsize("cities.js") // 1024, "KB")
for r in out:
    if r[0] in ("Munich", "Cologne", "Hamburg", "Vienna", "Köln", "Berlin", "Prague", "Kyiv", "Athens"): print(r)
