# STATE.md – NASA Space Apps 2026 (Projekt Jan)

Diese Datei ist die gemeinsame Wahrheit für alle, die am Projekt mitarbeiten (Jan, Claude, andere KI-Assistenten).
Regel: Wenn ein Chat-Gedächtnis und diese Datei sich widersprechen, gilt die Datei.
Am Ende jeder Arbeitssitzung: Stand hier aktualisieren. Nur eine KI ändert gleichzeitig denselben Code.

Letzte Aktualisierung: Sa 14.11.2026 (Claude-Chat)

## Rahmen
- Challenge: Be An Earth System Trend Detective! (NASA Space Apps 2026)
- Team: "Projekt Jan" (solo), Event: Hamburg (virtuell, lokales Event)
- Hackathon: Sa 14.11. 9:00 bis So 15.11. 23:59 Uhr. Abgabe über Reiter "Project" auf der Teamseite.
  Im Zweifel deutlich früher abgeben (Ziel: So 15.11. bis ca. 20:00).
- Abgabe-Anforderungen: alles auf Englisch; Demo = max. 7 Folien ODER max. 30 s Video (öffentlicher Link);
  Link zum finalen Projekt (z. B. GitHub, öffentlich, ohne Login); mind. 1 NASA-Datenquelle nennen;
  keine Personen unter 18 in Bild/Video; beide Häkchen setzen ("Terms" und "Original Work");
  Feld "Use of Super Intelligence" ehrlich ausfüllen; "Submit for Judging" klicken.
- Bewertung: Impact, Creativity, Validity, Relevance, Presentation (je 1–5).

## Fragestellung / Konzept (Entscheidung von Jan)
- Thema: Regionale Unterschiede der Entwicklung in Europa (wo ändert sich was, wie stark, signifikant?).
- Ablauf des Tools: Zeitreihe -> Steigung -> p-Wert -> Karte -> danach "Signifikanzhorizont"
  (ab welcher Fensterlänge wird ein Trend signifikant?).
- Horizont-Definition (Entscheidung): kürzeste Fensterlänge, ab der der Trend auch für alle längeren Fenster
  signifikant bleibt; Zellen ohne Signifikanz = "nicht erreicht in N Jahren". (Vermeidet Zufallstreffer
  durch Durchprobieren vieler Fenster.)
- Grundtool zuerst (Variable + Region wählen -> Zeitreihe, Steigung, Signifikanz), Horizont als Zusatz.
  Das entspricht dem Kern der Challenge.

## Verworfen / zurückgestellt (mit Begründung)
- "Bodenfeuchte sinkt, Niederschlag nicht signifikant": statistisch heikel (Signifikant vs. nicht signifikant
  zu vergleichen ist kein Test der Differenz); Bodenfeuchte in POWER ist Modellwert. Nicht verfolgt.
- "Vorzeichenwechsel zwischen Nachbarzellen": bei grobem Gitter und wenig signifikantem Niederschlag zu
  verrauscht / evtl. leer. Nicht verfolgt.
- "Verschwindet der Trend im Jahresmittel?" (Jahr vs. Jahreszeiten): noch offen, evtl. später als Auswahl.

## Technische Entscheidungen
- Daten: NASA POWER, monatlich, Punktabfrage (API, kein Login nötig). Hauptzeitraum 1981–2024 (44 Jahre; 1991–2024 bleibt als Fenster darin enthalten, Sicherung: data_1991.js, index_1991.html).
  Variablen: T2M (Temperatur), PRECTOTCORR (Niederschlag), GWETROOT (Bodenfeuchte, noch ungetestet).
  Achtung: Reanalyse-/Modelldaten, keine reinen Messungen -> in Demo/README erwähnen.
- Statistik: Jahresgang entfernen (Monatsmittel abziehen) -> Jahresmittel der Anomalien ->
  Steigung nach Theil-Sen, p-Wert per Kendall-tau gegen Zeit (= Mann-Kendall) ->
  Mehrfachtest-Korrektur Benjamini-Hochberg (FDR, 5 %).
- Gitter: Europa 35–70°N, 10°W–40°E, Schrittweite 5° (88 Punkte) zum Testen; 2.5° (315 Punkte) für die Demo geplant.
- Umgebung: Python 3.14.5 auf dem Mac, venv in ~/space-apps/venv
  (Aktivieren: source ~/space-apps/venv/bin/activate). Arbeitsordner: ~/Uni/Projekte/NASA Hackathon
- Die Arbeitsumgebung von Claude hat KEINEN Zugriff auf NASA-Server; Datenabfragen laufen auf Jans Mac.

## Dateien (Ordner "NASA Hackathon")
- trend_point.py: Trend + p-Wert für einen Punkt, erzeugt Grafik. Getestet (Demo + echter Punkt München).
- trend_grid.py: Gitter über Europa, FDR, Karte (map_<VAR>.png) und Tabelle (results_<VAR>.csv); Cache in ./cache.
- STATE.md: diese Datei.

## Ergebnisse bisher
- München (48.1N, 11.6E), T2M 1991–2024: +0,64 °C/Jahrzehnt (KI 0,40–0,87), signifikant.
- Europa-Gitter 5°, T2M: 87 von 88 Zellen signifikant (auch nach FDR). Stärkste Erwärmung Mittel-/Südost-Europa
  (ca. 0,7–0,8 °C/Jahrzehnt), schwächste Nordatlantik/Nordwest (ca. 0,1–0,3). Werte noch nicht gegen eine
  zweite Quelle geprüft (z. B. DWD für Deutschland).

- Niederschlag (PRECTOTCORR), 5°: 16 von 88 Zellen signifikant ohne Korrektur, nur 4 nach FDR.
  FDR-signifikant: (35N,20E) -0,12; (35N,35E) -0,24; (40N,5E) -0,26; (45N,25E) +0,26 mm/Tag pro Jahrzehnt.
  3 von 4 liegen im Mittelmeer (Meer). 56 Zellen positiv, 32 negativ.
- Bodenfeuchte (GWETROOT), 5°: 26 von 88 Punkten ohne Daten (Meer, dort nicht definiert), 62 mit Ergebnis;
  10 signifikant ohne Korrektur, 1 nach FDR: (40N,5E), stark negativ (-0,028/Jahrzehnt) – dieselbe Zelle wie beim
  Niederschlag, Küsten-/Inselzelle bei den Balearen -> mit Vorsicht behandeln (Einzelpunkt, evtl. Land-See-Effekt).
- Aussage für die Demo (Jans Entscheidung, wie erzählt): Temperatur fast überall signifikant, Niederschlag und
  Bodenfeuchte kaum -> "an vielen Orten reichen 34 Jahre nicht" (passt zum Signifikanzhorizont).
- Grenze: Gitter = Einzelpunkte (nicht Flächenmittel); Nachbarzellen können wegen lokaler Variabilität das
  Vorzeichen wechseln, besonders bei Bodenfeuchte.
- Ausgabedateien enthalten jetzt die Schrittweite im Namen (results_<VAR>_<step>deg.csv, map_<VAR>_<step>deg.png);
  Zellen ohne Daten sind grau. (Alte Läufe: results_<VAR>.csv / map_<VAR>.png.)

## Offen / nächste Schritte
1. (erledigt) PRECTOTCORR und GWETROOT auf dem 5°-Gitter gelaufen.
2. Plausibilitätscheck der Temperaturwerte gegen zweite Quelle.
3. Gitter verfeinern (--step 2.5), im Hintergrund laufen lassen.
4. Oberfläche (Variable und Zeitraum wählen, Klick auf Zelle -> Zeitreihe).
5. Signifikanzhorizont implementieren und testen.
6. Repository (GitHub, öffentlich) + README (Methode, Daten, Grenzen, KI-Hinweis).
7. Demo: 7 Folien (Englisch), Projektseite ausfüllen, abgeben.

## KI-Nutzung (Grundlage für das Feld "Use of Super Intelligence" – ehrlich pflegen!)
- Claude (Anthropic): schrieb trend_point.py und trend_grid.py (Code), erklärte Regeln/Statistik, gab fachliches Feedback.
  Code-Dateien tragen einen KI-Hinweis im Kopfkommentar.
- Konzept: Jan hat das Thema (Unterschiede in Europa) gewählt. Teile der Optionen und des Plans (z. B. POWER-Datenquelle,
  Vorzeichenwechsel- und Horizont-Idee) stammen aus einem Gespräch mit einem anderen KI-Assistenten, das Jan
  in den Claude-Chat eingefügt hat. Das muss Jan im KI-Feld wahrheitsgemäß angeben.
- Weitere genutzte KI-Tools hier eintragen:


## Update 14.11. abends: Hauptzeitraum jetzt 1981–2024
- data.js neu aus 1981 gebaut (2,5°, alle Zellen vollständig: 315 / 315 / 232). Fenster 44..15 Jahre, Winter 43.
- Ergebnisse (FDR, ganzer Zeitraum): T2M 315/315, Niederschlag 11/315, Bodenfeuchte 26/232. Winter T2M 151, Sommer T2M 299.
- Autokorrelationskorrektur (START=1981): T2M 305, Niederschlag 9, Bodenfeuchte nur 2 von 26. Winter T2M 93, Sommer 287.
- Bodenfeuchte ist fragil und hängt vom Startjahr ab (1991: 1 Zelle, 1981: 26, nach Korrektur 2). Nur vorsichtig formulieren.
- TS vs. OLS: r 0,93-0,99; mediane relative Differenz T2M 3 %.
- index.html: Zahlen im Robustheits-Satz aktualisiert, Datenzeile 1981-2024. Test: keine Konsolenfehler, Schieber 29 Schritte.
- trend_detective_standalone.html neu gebaut.
- Offen: Schieber bis 10 Jahre als Demo (optional), README/Demo/GitHub morgen.

## Update 14.11. spaet: Fenster bis 10 Jahre, Bodenfeuchte
- data.js mit --min-window 10 gebaut (Sicherung 15er-Version: data_min15.js, index_min15.html). Warnhinweis auf der Seite fuer Fenster < 15 Jahre.
- Ganzjahres-Temperatur, FDR: signifikante Zellen bei 44 J: 315, 30 J: 274, 20 J: 161, 15 J: 154, 10 J: 0. Median-Horizont weiter 21 Jahre (kleinster 11).
- Bodenfeuchte: Gebietsmittel 1981-2024 p=0,26 (nicht signifikant); 1981-1995 -0,032/Jahrzehnt (p=0,011), 1991-2024 +0,002 (p=0,32). Signal stammt aus den feuchten fruehen 80ern, kein stetiger Trend. Signifikante Zellen: 44 J: 26, 30 J: 2. Einordnung: Grenze der Methode, kein Befund.
- Findings-Kasten-Text angepasst, Standalone neu gebaut.

## Update 14.11. nachts: 6 Variablen
- Neu: QV2M (Wasserdampf), RH2M (relative Feuchte), ALLSKY_SFC_SW_DWN (Sonnenschein, erst ab 1984 -> Schieber ab 1984, i0 im Datensatz). Alle 315 Zellen im Cache (Gap-Fill gelaufen).
- build_data.py: VARS mit Alltagsnamen, 'first' fuer spaeten Start, horizon(..., i0). Sicherungen: build_data_v5.py, index_3vars.html, index_pre6.html, data_min10_3vars.js.
- Ergebnisse Ganzjahr, FDR 44 J (Strahlung 41 J) -> nach Autokorrelationskorrektur: QV2M 309 -> 301; RH2M 62 -> 5; ALLSKY 213 -> 199. Winter: QV2M 133->64, RH2M 1->1, ALLSKY 14->8. Sommer: QV2M 283->267, RH2M 45->17, ALLSKY 164->150.
- Einordnung: robust = Temperatur, Wasserdampf, Sonnenschein; fragil = Niederschlag, Bodenfeuchte, relative Feuchte.
- Seite: Dropdown in Gruppen (Heat / Water and moisture / Sunlight), Findings-Karte 4, Presets 'vapour' und 'sun', Scatter-Legende klickbar (Standard: T2M, Niederschlag, Bodenfeuchte), Regionstabelle = Kernvariablen + gewaehlte.
- Offen: Validierung Strahlung gegen DWD (Sonnenscheindauer), README/Demo/GitHub morgen. data.js 5,5 MB.

## Update 14.11. Validierung Strahlung (DWD Sonnenscheindauer)
- Quelle: DWD CDC regional_averages_DE/annual/sunshine_duration/regional_averages_sd_year.txt (Stand 2026-11-02), Spalte Deutschland -> dwd_germany_annual_sunshine.csv; Skript dwd_compare_sun.py.
- Deutschland 1984-2024: DWD Sonnenscheindauer +62 h/Jahrzehnt = +3,8 % des Mittels (p=0,001); POWER Einstrahlung +0,254 MJ/m2/Tag/Jahrzehnt = +2,4 % (p<0,001). Korrelation der Jahreswerte r=0,91 (1984-1999: 0,73; 2000-2024: 0,96).
- Einordnung: Richtung und Groessenordnung passen; Sonnenscheindauer und Einstrahlung sind verschiedene Groessen (Vergleich der Muster, nicht der Werte).
- KORREKTUR: Einheit der Einstrahlung ist MJ/m2/Tag (API-Community AG), nicht kWh. In build_data.py und auf der Seite korrigiert.

## Update 14.11. spaet: Zoom, Zellenprofil, Aufraeumen
- Ordner aufgeraeumt: alte Sicherungen, 5-Grad-Daten, results_*.csv, Test-PNGs, __pycache__ nach archive/ verschoben (nichts geloescht). Aktuelle Dateien: index.html, data.js, land.js, trend_detective_standalone.html, build_data.py, export_tables.py, autocorr_check.py, fetch_cache.py, trend_point.py, trend_grid.py, dwd_*.py, smhi_*.py, CSVs, STATE.md, cache/ (27 MB, fuer GitHub per .gitignore ausschliessen).
- Seite: Kartenzoom (+/-/Reset, Ziehen, Strg/Cmd+Mausrad oder Trackpad-Pinch), Button 'Zoom the map to this area', Zellenprofil (alle 6 Variablen fuer die gewaehlte Zelle), Auswahl bleibt beim Variablenwechsel erhalten, Robustheitstext aufklappbar, Handy: kein seitliches Scrollen mehr, Regionstabelle ohne Abschneiden.
- Offen: README, Demo (max. 7 Folien), GitHub + Pages, Einreichungstexte, PNG-Export; optional Wasserdampf/Feuchte gegen Messungen pruefen.

- Ausgewaehlte Kachel 'kommt nach vorn' (groesser, deckend, mit Schatten; Signifikanz-Punkt bleibt). Sicherung: archive/index_before_pop.html.

## Update 14.11. spaet: CI, Limits, Validierung Sueden
- Detailfeld/Profil zeigen das 95-%-Intervall der Theil-Sen-Steigung (Sen 1968, im Browser berechnet; Test gegen scipy: 0,334..0,632 vs 0,3339..0,6317). Hinweis: ohne Autokorrelation. Sicherung: archive/index_before_ci.html.
- Limits erweitert: raeumliche Abhaengigkeit, 2,5-Grad-Punktstichprobe, Breitenband-Mittel inkl. Meer, Intervall ohne Autokorrelation, Validierungszusammenfassung.
- Validierung Suedeuropa: Berkeley Earth Laenderreihen (Analyse 06-Jan-2021, Reihe bis 2020), berkeley_south_europe_annual.csv (Pruefsummen gegen Quelldateien OK), berkeley_compare.py. 1981-2020, T2M: Spanien Berkeley +0,26 vs POWER +0,21 C/Jahrzehnt (r=0,93; 8 Punkte); Italien +0,39 vs +0,30 (r=0,96; 6 Punkte); Griechenland +0,41 vs +0,41 (r=0,98; 2 Punkte). POWER liegt in ES/IT etwa 20 % niedriger.
- Gesamt T2M: DE r=0,99 (+0,47 DWD vs +0,51), SE r=0,98 (+0,42 vs +0,40), ES/IT/GR s.o. -> fuenf Laender, drei Klimazonen.
- Hinweis zur Fremd-KI-Liste: Behauptung 'SO-Europa 42,5N/25E braucht 10 Jahre' stimmt nicht, in den Daten sind es 14 (Atlantikpunkt 35N/10W: +0,09, 39 Jahre stimmt).

## Update 14.11. nachts: Land/Meer, Staedte, Gesamtaenderung, Korrelationen
- build_data.py: Land-Meer-Maske (Gitterpunkt in Natural-Earth-Land, Datei land.js, Ray-Casting), Zellen mit 'l'-Flag (173 Land / 142 Meer von 315), 6 Regionen: Nord/Mitte/Sued nur Land, ganze Karte Land, Meer, Land+Meer. Sicherungen: archive/build_data_before_landsea.py, data_before_landsea.js, index_before_landsea.html.
- Ergebnis T2M 1981-2024 (Regionen): Land +0,44, Meer +0,33, Land+Meer +0,39; Mitteleuropa Land +0,51, Nordeuropa Land +0,40, Suedeuropa Land +0,37 C/Jahrzehnt. Niederschlag: nur Land und Mitteleuropa-Land signifikant (+0,03/+0,04 mm/Tag/Jahrzehnt, 33-35 Jahre), Vorzeichen nicht belastbar.
- Seite: Regionshervorhebung zeigt die einzelnen Zellen (gestrichelt), 'Check a place' (15 Staedte -> naechste Gitterzelle, Zoom), 'Fitted change from 1981 to 2024' mit 95-%-Bereich, Spalte 'Moves with temp. (r)' im Zellenprofil (Korrelation der trendbereinigten Jahreswerte, nur beschreibend).
- Fremd-KI: Vorschlaege teils uebernommen (Land/Meer, Staedte, Gesamtaenderung); Korrelationen nur beschreibend; Hälften-Vergleich/Beschleunigung nicht umgesetzt (22 vs 22 Jahre zu duenn).

## Update 14.11. nachts (2): Pruefung der Fremd-KI-Liste, Strahlung 2001, Placebo-Test
- Datenherkunft (POWER-Doku, per Websuche): Meteorologie (T2M, PRECTOTCORR, GWETROOT, RH2M, QV2M) = NASA GMAO MERRA-2, ab 1981. Solar (ALLSKY_SFC_SW_DWN) = NASA SRB 4.0-IP (1984-2000) und CERES SYN1deg/FLASHFlux (ab 2001) -> QUELLENWECHSEL 2001.
- Befund: Deutschland POWER vs DWD-Sonnenscheindauer: Residuum 1984-2000 im Mittel -0,22 MJ/m2/Tag gegenueber 2001-2024 (sd 0,18) -> kleiner Sprung moeglich. Alle Zellen: Median-Trend 1984-2000 +0,31, 2001-2024 +0,11 MJ/m2/Tag/Jahrzehnt (84 % der Zellen positiv, nur 22 % roh signifikant). FDR-signifikante Zellen mit Start 2001 (24 J): ALLSKY 0, T2M 223, QV2M 175.
- Einordnung geaendert: Sonnenschein ist NICHT so robust wie Temperatur/Wasserdampf. Autokorrelation 213->199 ok, aber Quellenwechsel -> Vorsicht. Auf der Seite in Findings-Karte, Robustheitstext, Limits und Variablenbeschreibung vermerkt. Fuer README/Demo: 'brightening' nur mit diesem Vorbehalt; Richtung stimmt mit DWD ueberein (+3,8 %/Jahrzehnt Sonnenscheindauer, 2001-2024 p=0,14).
- null_test.py/null_test.csv (Placebo, Jahre zeitlich gemischt, 100 Laeufe): roh ~5 % Fehlalarm (4,3-5,8 %), FDR im Mittel <=0,3 Zellen; bei raeumlich gemeinsamer Mischung gelegentlich Cluster (QV2M max. 156 Zellen in 1 von 100 Laeufen) -> zeigt raeumliche Abhaengigkeit.
- Seite: 95-%-Band um die Trendgerade in der Zeitreihe, 'Per decade to total'-Satz, Beschreibungen mit MERRA-2-Herkunft, Fallback-Zahlen in den dynamischen Textstellen (auch ohne JavaScript lesbar), Presets neutraler benannt ('Water vapour: rising too?', 'Sunshine since 1984: a trend?').
- Fremd-KI-Liste (Konfidenzband, Autokorrelations-Satz, Umrechnungssatz, Herkunft, Placebo-Test, Platzhalter-Bug): uebernommen bzw. schon erledigt; Platzhalter-Bug war nur ohne JavaScript sichtbar -> behoben durch Fallback-Text. Nicht uebernommen: OLS-Formel fuer das KI (wir nutzen Theil-Sen), Vergleich Sommer-Hitze (unbelegt).

## Update 15.11. frueh: Feinschliff aus Fremd-KI-Liste
- Glossar-Winter jetzt dynamisch (1982, 43 Jahre; war 1992/33 Altlast). Presets stehen als 'Start with a question' ueber den Reglern, aktives Preset blau markiert und wird bei manueller Aenderung geloescht. Limits-Text verweist auf das Skript 'in the project repository'. Deep-Links: Ansicht steht im URL-Hash (#v=..&s=..&view=..&y=..&fdr=..&c=lat,lon oder &r=region), Button 'Copy link to this view'. Sicherung: archive/index_before_polish.html.
- Hinweis: Deep-Links funktionieren erst mit gehosteter Seite (GitHub Pages), nicht aus WhatsApp-Vorschau.

## Update 15.11. vormittags: 'What is here?' je Kachel
- cellinfo.py -> cellinfo.js (window.CELL_INFO, 34 KB): je 2,5-Grad-Zelle Landanteil, Laender nach Anteil am Land, bis zu 3 groesste Orte (>15.000 Einw., Vororte im Umkreis 0,4 Grad ausgeblendet). Quellen: Natural Earth 1:50m Laender (npm world-atlas, gemeinfrei), GeoNames Staedte (pip geonamescache, CC BY 4.0). Russland-Polygon wrapt um die Datumsgrenze -> Laengengrade unwrap (sonst falsche Russland-Anteile). Krim: GeoNames sagt Ukraine, Natural Earth Russland -> Orte ohne Laendernamen, Hinweis 'Country names in disputed areas follow Natural Earth'.
- Seite: Detailfeld zeigt 'What is here?'; Footer nennt GeoNames; hashchange-Listener fuer Deep-Links im selben Tab. Standalone enthaelt cellinfo.js inline. Sicherung: archive/index_before_cellinfo.html.
- Lehre: device_commit_files mit wiederverwendetem Dateinamen schrieb alte Version -> immer neuen stagedPath-Namen (_v2, _v3 ...) und danach md5 pruefen.
- GitHub: cellinfo.js muss neben index.html liegen (script-Tag).

## Update 15.11. mittags: 'What is here?' vereinfacht
- Nur noch Hauptland (mit Anteil, falls <100 %) und groesste Stadt. Krim wird in cellinfo.py Ukraine zugeordnet (Box 32.4-36.6E, 44.3-46.25N aus Russland herausgeschnitten); Footer angepasst, Disputed-Hinweis entfernt. cellinfo.js neu (md5 0aae2659...). Sicherung: archive/index_before_simplify_cellinfo.html.

## Update 15.11. nachmittags: Einordnung, Suche, Vergleich
- index.html: (1) Marker 'data source changes 2001' im Zeitreihen-Chart bei Sonnenschein; (2) Autokorrelations-Hinweis unter dem Kartentitel (PRECTOTCORR, GWETROOT, RH2M, ALLSKY), Zahlen aus autocorr_check.csv fest in AC eingetragen; (3) Banner unter den Preset-Fragen, Zahlen live aus den Daten; (4) Limits: Satz 'kein Forecast'; (5) Stadtsuche mit Autovervollstaendigung ersetzt das 15-Staedte-Dropdown (cities.js, 8.278 Orte >15.000 Einw. im Kartenausschnitt, GeoNames CC BY 4.0, Skript citylist.py; Stadtteile mit gleichem Namenspraefix entfernt); (6) Vergleichsmodus 'Compare two places': Zelle A + B, gemeinsames Chart, Tabelle, Deep-Link &c2=lat,lon, Swap-Knopf. Zellklick schreibt jetzt auch den Hash.
- cellinfo.py: Krim -> Ukraine. cities.js muss neben index.html liegen.
- Sicherung: archive/index_before_compare.html. Standalone neu gebaut (data, land, cellinfo, cities inline).
- Lehre: device_commit_files schrieb index.html mit Namen index_v6.html in alte Version (Name frueher benutzt) -> immer einmalige Namen + md5 pruefen.
- Offen: README, Demo, GitHub, Abgabe.

## Update 15.11. abends: Fallakten, Rekorde, Entscheidungs-Abschnitt, Fruehling/Herbst
- build_data.py: SEASONS um mam (Mar-May) und son (Sep-Nov) erweitert; data.js neu (9,1 MB; year/djf/jja unveraendert, per JSON-Vergleich geprueft). Backups: archive/data_before_mam_son.js, archive/build_data_before_mam_son.py.
- autocorr_check.py neu gelaufen (alle 5 Jahreszeiten, 9035 Zeilen; alte Werte unveraendert; Backup archive/autocorr_check_before_mam_son.csv). AC-Tabelle in index.html um mam/son ergaenzt. export_tables.py neu gelaufen (Backup archive/csv_before_mam_son/).
- Frühling: T2M 188/315 signifikant (162 nach Autokorrektur), Herbst 296/315 (290). Niederschlag in beiden: 0 Zellen signifikant.
- index.html: 'Compare places' mit drei Faellen (Dublin vs Warsaw, Stockholm vs Madrid, Oslo 10-Jahres-Fenster), Banner mit Live-Zahlen; 'Records'-Satz in der Zellansicht; Abschnitt 'What does this mean for decisions?'; Satz Land vs. Meer im Warming-Banner; Radios Spring/Autumn.
- Befund Fallakten (Daten, nicht AI-Liste): Dublin-Zelle +0.19 (38 J.) vs Warschau +0.51 (19 J.): Schwankung am Atlantik kleiner (0.4 vs 0.9 °C), aber Trend viel schwaecher. Stockholm +0.50 (27 J.) vs Madrid +0.36 (15 J.): Madrid ruhiger. Oslo letzte 10 Jahre -0.27 (n.s.), 44 Jahre +0.31; 52 von 315 Zellen kuehlen im letzten 10-Jahres-Fenster. Die AI-Behauptung 'Winter-Erwaermung im Norden vs Sommerhitze im Sueden' stimmt in unseren Daten nicht (beide Sommer staerker).
- Standalone neu gebaut. Lehre: neue Dateinamen beim Commit (index_sp_r9m4.html), md5 geprueft.

## Update 15.11. abends (2): Mittelwert-nicht-Extreme
- Rain-Banner: Satz 'Mean, not extremes' (Monatsmittel, keine Starkregen/Trockenphasen). Limits: zwei neue Punkte (Niederschlag nur als Monatsmittel; alle Zeitfenster enden 2024). Standalone neu gebaut. Erwartete md5 index.html: 1f1f1955...

## Update 15.11. abends (3): Validierung, 30-Jahre-Check, Flicker, Robustheits-Tabelle
- index.html (md5 04a2453c...): Abschnitt 'How well do the data match measurements?' (Tabelle DWD/SMHI/Berkeley/DWD-Sonnenschein/DWD-Niederschlag; Laendermittel, keine Einzelstationen); Robustness-Tabelle (Zellen signifikant vs. mit Autokorrektur); Meaning-Abschnitt: 30-Jahre-Check (T2M: 262/315 Zellen mit <=30 Jahren, 153 mit <=20; Niederschlag: 1/315) und Flicker-Zaehlung (140/315 Zellen); Flicker-Hinweis in Zell- und Vergleichsansicht (Beispiel Dublin: Fenster 13-18 und 34 Jahre signifikant, stabil erst ab 38).
- Nicht uebernommen aus AI-Liste: DJF 'steiler' (in unseren Daten Winter-Trend kleiner als Sommer-Trend), Stationsvergleich auf der Karte (unsere Validierung nutzt Laendermittel, keine Einzelzellen).
- Standalone neu gebaut.

## Update 15.11. abends (4): Halbzeit-Satz, Sensor-Button -> SEITE EINGEFROREN
- index.html (md5 65f523b8...): Meaning-Abschnitt 'A straight line is a simplification' (nur Temperatur, live: Median-Trend 1981-2002 +0.30 vs 2003-2024 +0.55 °C/Dekade, 216/315 Zellen steiler; ausdruecklich kein Signifikanztest); vierter Button 'Sunshine: the 2001 source change' (Berlin-Zelle, Sonnenschein, Linie 2001, Warntext; sagt ausdruecklich: Tool erkennt den Bruch nicht selbst, es markiert das bekannte Datum). Standalone neu gebaut; Kopie: archive/index_final_candidate_1.html.
- Fuers README 'What we tested and deliberately excluded': (a) Change-Point-Test (mehr Angriffsflaeche als Erkenntnis), (b) 'Regen-Paradoxon' (Bodenfeuchte-Trend in unseren Daten gemischt: 118 von 232 Zellen negativ, 18 signifikant fallend, 8 steigend, nach Autokorrektur 2), (c) Hitze-Trockenheit-Kopplung nach Halbzeiten (22 Jahre zu kurz; MERRA-2-Bodenfeuchte ist Modellprodukt, Kopplung koennte teils Modell-Artefakt sein), (d) Compound-Jahre zaehlen (seltene Ereignisse, 22 Jahre zu kurz, Bodenfeuchte fragil), (e) Winter 'steiler' (Winter-Trend im Median kleiner), (f) Stationsmarker auf der Karte (Validierung nutzt Laendermittel), (g) Vorhersagen (keine Prognose). Alle Fenster enden 2024.

## Update 15.11. spaet (5): Overlay gemessen vs. POWER, Startjahr-Test
- validation_series.py -> validation_series.js (7 Faelle: DWD/SMHI/Berkeley/DWD-Sonne/DWD-Niederschlag gegen POWER, jeweils als Abweichung vom eigenen Mittel). Karte 'How well do the data match measurements?' hat jetzt ein Diagramm mit Knoepfen (orange gemessen, blau POWER, gestrichelte Trends); Niederschlag Deutschland: gemessen -15.6 mm/Jahr pro Dekade, POWER +11.0 mm/Jahr -> Richtung stimmt nicht. validation_series.js muss neben index.html liegen. index.html md5 eb20280a...
- Startjahr-Test (build_data.py --start 1991, nur T2M/Niederschlag/Bodenfeuchte im Cache; Daten archive/data_start1991_test.js): Temperatur Median Jahre 21 (1981) vs 20 (1991), Zellen-Korrelation 0.94 (309 Zellen), signifikant 315 vs 309; Bodenfeuchte 26 vs 1 signifikante Zellen -> haengt vom Startjahr ab; Niederschlag 11 vs 15; Winter-T2M 151 vs 62 (kuerzere Reihe). Satz steht im Robustness check.
- Wasserdampf-Banner: 'they do not test the mechanism'.
- Idee 'Horizont in die Zukunft' verworfen: Formel n=(2.8*sqrt(12)*s/b)^(2/3) korreliert nur r~0.5-0.6 mit dem echten Horizont; graue Niederschlagszellen Median 98 Jahre, 47% >100 Jahre, bei b->0 unendlich.
- Standalone neu gebaut (inkl. validation_series.js). Kopie: archive/index_final_candidate_2.html.

## Update 15.11. spaet (6): Emergence + ungewoehnliche Monate (Jan: "mach beides")
- build_data.py: neue Felder pro Zelle `em`/`er` (erstes Endjahr, ab dem der Trend ab 1981 signifikant bleibt; FDR/roh) und pro Variable `emerge` {y0, ends, fracF, fracR}. Neue abgeleitete Variablen T2M_HOT/T2M_COLD/P_WET/P_DRY (nur Jahr; Monate ueber/unter P90/P10 des jeweiligen Kalendermonats 1981-2010; `kind:"extreme"`). Build pro Jahreszeit mit `--seasons` nach parts/*.json, dann `--assemble-only`. Alte Felder unveraendert (geprueft).
- index.html: Ansicht "Year the trend became detectable" (Karte, Legende, Tooltip, Liniendiagramm Anteil Zellen je Endjahr, Zelltext), Gruppe "Unusual months (whole year only)" im Menue (in anderen Jahreszeiten deaktiviert, Fallback T2M), 3 neue Presets (emerge, hot, wet), Meaning-Bullet, Glossar/Limits aktualisiert. Streu- und Profil-Tabelle ohne die Extrem-Variablen.
- Zahlen (FDR): T2M Anteil nachweisbar 20/49/86/96/100 % bei Endjahr 2005/2010/2015/2020/2024 (Median 2011); QV2M 48/59/76/90/98 %; PRECTOTCORR 3 % (2024); heisse Monate 0.9 -> 3.8 pro Jahr (311/315 sig.), kalte 1.5 -> 0.3 (267), nasse 1.2 -> 1.7 (26 sig., 23 steigend), trockene 1 Zelle.
- Nicht gemacht: autocorr_check.py fuer die neuen Variablen (Zaehlreihen); Hinweis steht nicht auf der Seite -> im README als Limit nennen.
- Backups: archive/index_before_emergence.html, archive/data_before_emergence.js, archive/build_data_before_emergence.py. index.html md5 685d021b..., Standalone neu gebaut.

## Update 15.11. spaet (7): MDT, S/N, Faktor "neues Normal", Wasserdampf-Satz
- index.html (md5 be608570...): Detailpanel zeigt "Smallest detectable trend" (MDT = 2.8*sigma/sqrt(n(n^2-1)/12), pro Dekade, 80 % Power, unabhaengige Jahre; sigma = Streuung um die Theil-Sen-Gerade). Meaning-Karte: neue Punkte "Not significant is not no change" (Niederschlag MDT +-0.096 mm/Tag/Dekade vs. typischer Trend 0.030; Temperatur +-0.19 vs. 0.36), "Signal against noise" (S/N>2 in 264/315 Zellen, Median 2.8, Spearman -0.61 mit Emergenzjahr), "Warmer air, drier air" (QV2M 315/315 steigend, RH2M faellt in 198/315, Bodenfeuchte 118/232 fallend = keine gemeinsame Richtung). Heisse Monate = 3.2x das erwartete 1.2/Jahr. Rain-Preset-Text mit MDT; aria-live auf presetnote/acwarn/copymsg.
- Nicht uebernommen: AMO/NAO/Aerosol-Erklaerungen (nicht testbar), "4.8 / 4x" (erfunden), Hamed-Rao-Schalter (n_eff-Zahlen stehen schon in der Robustheitstabelle), Stationsvergleich (README-Luecke), Button-Umbau (Gestaltung).
- Backup: archive/index_before_mdt.html. Standalone neu gebaut. Seite jetzt EINGEFROREN.

## Update 15.11. spaet (8): "The new normal"-Punkt (FINAL, Seite eingefroren)
- index.html md5 5a606d1a...: Meaning-Karte hat Punkt "The new normal": 172/315 Zellen: Mittel 2015-2024 waermer als das waermste Einzeljahr 1981-2000; 115/315 > Mittel+2 SD; typische Zelle: 5 der letzten 10 Jahre waermer als das waermste Basisjahr. Backup archive/index_before_newnormal.html. Standalone neu.
- Geprueft und NICHT uebernommen: "Winter feucht/Sommer trocken hebt sich auf" (Winter-P 0/315 sig., Sommer 1/315, Mediantrend in beiden leicht positiv; nur 56 Zellen mit Vorzeichen-Gegensatz; Sued<45N Winter -0.033, Nord +0.05, n.s.), NAO-Erklaerung (nicht testbar -> README hoechstens "often linked, not tested"), "Saettigungsdefizit steigt" (nicht berechnet).
- Naechste Schritte: README, Demo (max 7 Folien), Projektseite + "Use of Super Intelligence", GitHub + Pages (Jan), PNG, Abgabe ~20:00.

## Update 15.11. spaet (9): Beobachtungs-Planer "How long would I have to measure here?"
- index.html md5 a697bce7...: im Detailpanel (nach "Smallest detectable trend") Eingabefeld fuer Trendgroesse pro Dekade -> benoetigte Jahre (80 % Power, unabhaengige Jahre; Schleife n=5..300, darueber "more than 300 years"). Wert wird je Variable gemerkt. Gegenprobe: Eingabe = MDT -> 44-45 Jahre (Rundung). Beispiele: Temperatur 0.3 -> 22 J., 0.1 -> ~45 J.; Niederschlag-Zelle 0.1 mm/Tag -> 48 J., 0.01 -> 222 J.
- Backup archive/index_before_planner.html. Standalone neu. Seite wieder EINGEFROREN. Naechster Schritt: README (mit Leitsatz "Most tools show what changed. Trend Detective shows how long you need to wait before you can trust it." + 3 Nutzer), Projektseite, Demo.
- README.md, requirements.txt, .gitignore geschrieben (15.11. spaet 10). Platzhalter im README: GitHub-Pages-Link (TODO). Abgabe-Texte siehe Chat.

## Update 15.11. spaet (11): Oberflaeche Runde 1 (Design)
- index.html md5 79ea069b...: neuer Kopf (Leitsatz), 5 kuratierte Faelle + aufklappbar 'More questions and place comparisons' (alle data-preset/data-case-Buttons bleiben), Kontrollleiste kompakter und neu geordnet, Key findings unter die Karte verschoben. Kartenanfang: Laptop 917 -> 517 px, Handy 2064 -> 1066 px. Tests: Presets, Cases, Suche, Findings-Klick, Standalone, kein Overflow. Backup archive/index_before_design.html.
- Wording-Fix im wet-Preset (Gebiets-Mittel Land-Niederschlag +0.034 mm/Tag/Dekade, p=0.003, 33 Jahre; einzelne Zellen 11/315). Index md5 siehe naechster Eintrag.

## Update 15.11. spaet (12): Gebietsmittel-Satz, Warming Stripes, 'Your place' (FINAL fuer Inhalt/Design Runde 2)
- index.html md5 4aeb9f16...: (1) Meaning-Karte + Rain-Preset: Landmittel Niederschlag +0.034 mm/Tag/Dekade (signifikant, ab 33 J.) vs. 11/315 Zellen. (2) Warming Stripes unter der Zeitreihe (alle Variablen, Palette je Variable; PAL um T2M_HOT/T2M_COLD/P_DRY erweitert). (3) 'Your place'-Karte im Detailfeld (Ganzjahr, unabhaengig von Jahreszeit; Warming, nachweisbar seit, ungewoehnliche Monate, neues Normal, Regen + MDT; 'Copy summary'). Handy-Overflow der Profiltabelle behoben (overflow-x:auto). Backup archive/index_before_myplace.html. README um Zeile 'my own place' und Mittelungs-Punkt ergaenzt.

## Update 15.11. spaet (13): Lifetime, Quick start, Zitierhinweis, Stripes-PNG
- index.html: 'Your lifetime' (Geburtsjahr -> Trendlinie zuerst, dann 3-Jahres-Vergleich, warme Monate), 'Quick start in 30 seconds' (aufklappbar), 'How to cite' im Footer, Stripes als PNG-Download (Canvas, mit Beschriftung). Backup archive/index_before_lifetime.html. README um 'my lifetime' ergaenzt. Hitzetage NICHT eingebaut (Tagesdaten waeren neuer Datenbau: Risiko am Abgabetag).
- fetch_daily.py geschrieben (Jan startet im Terminal; Sandbox/VM hat kein NASA-Netz)
- (14) final5: Zeitraffer (emerge), Dark Mode, Data&limitations, Favicon/OG, Tastatur Karte; index.html md5 5d16b02e...; Backup archive/index_before_final5.html
- (15) Heisstage: fetch_daily.py (Jan lief lokal, 315 Zellen), daily_metrics.py -> daily_counts.json (HOT30, TX90, HEAVY), build_data.py um D_HOT30/D_TX90/D_HEAVY (kind extreme, nur year) erweitert; data.js = data_v3.js (md5 7b0e7195...), alte Version archive/data_v2_before_daily.js; alle alten Felder identisch (JSON-Vergleich). Ergebnis: TX90 314/315 signifikant, Median 27 Jahre, Ø 28 -> 68 Tage/Jahr (1981-90 vs 2015-24); HOT30 94 Zellen (136 Zellen nie), HEAVY 10 Zellen. UI: Gruppe "Daily extremes", Preset hotdays, Findings-Karte, Dein-Ort-Zeile, Limitations-Punkt. Als experimentell markiert. index.html md5 48aca0ee..., archive/index_before_hotdays.html.
- (16) Karte als PNG (Titel, Legende mit Farbbalken, Quelle; immer hell). index.html md5 4863a4c7..., Backup archive/index_before_png.html; Standalone neu.
- (17) Zwei Live-Karten (Map B: eigene Variable/Saison/Ansicht/Fenster, Zoom verbunden, Klick waehlt Zelle auf beiden, Swap, URL-Hash b=...), Preset twomaps. Refactor render(): paintMap/withB/mapTitleText/varDescText. index.html md5 64df6d86..., Backup archive/index_before_twomaps.html.
- (18) Tooltip-Sparkline (cellSpark) + Surprise-me-Knopf (5 Story-Typen). index.html md5 0f185b56..., Backup archive/index_before_spark.html; Standalone neu; README ergaenzt.
- (19) Tooltip nennt Land und groesste Stadt (CELL_INFO). index.html md5 53409611..., Backup archive/index_before_where.html; Standalone neu.
- (20) Karten-Extras: Hover-Rahmen, Staedtelabels (Zoomstufen, Kollisionspruefung), Land only (Meereszellen blass, Hash land=1), Play windows + 'Significant in X of N cells'. index.html md5 2a89e61c..., Backup archive/index_before_extras.html; Standalone neu; README ergaenzt. (Korrektur: Eintrag (13) 'Hitzetage NICHT gebaut' ist durch (15) ueberholt.)
- (21) Land only: nutzt jetzt Landanteil der Zelle (CELL_INFO l<10 = Meer) statt Punktflag; Kola-Zellen (67.5N 30E/32.5E, Seen im Polygon) waren faelschlich Meer. 82 statt 142 Zellen blass. Regionalmittel nutzen weiter Punktflag; 2 Zellen betreffen ~0.003 C/Dekade, im README vermerkt. index.html md5 3a5d2cb6..., Backup archive/index_before_landfix.html.
- (22) Weiche Farbuebergaenge der Kartenzellen (Rechtecke werden wiederverwendet, CSS-Transition .35 s, prefers-reduced-motion aus). paintMap speichert Zelle in r.__c. index.html md5 3a59dbcf..., Backup archive/index_before_fade.html; Standalone neu.
- (23) Uebergaenge fuer ALLE Wechsel: ein Rechteck pro Gitterzelle bleibt bestehen (rmap), Zellen, die eine Variable nicht hat (z. B. Meer bei Bodenfeuchte), blenden aus statt zu verschwinden. Zweiter Klick auf die gewaehlte Zelle hebt die Auswahl auf (pickCell). index.html md5 e5866e8b..., Backup archive/index_before_keyed.html; Standalone neu.

(24) Added D_CDD (longest dry spell; daily_metrics.py -> daily_counts.json -> data.js md5 5cb9ab57; old content identical; 1/315 FDR-significant) and context card (ESOTC 2025: Europe ~2.5 C, global ~1.4 C above 1850-1900, external, not computed). Backups: archive/*_before_cdd.*. index.html + standalone rebuilt.

(25) Added CSV download per cell (#csvdl) and CVD fix (COMBO both: #7b4f9e -> #3d1558). Backup archive/index_before_csv.html. Standalone rebuilt.

(26) Added LICENSE (MIT, Jan Schumacher), README screenshots + quickstart + Pages link (schumacherjan-dev/trend-detective), screenshots/ folder.

(27) Redesign: pill control bar (What/Where/View/When + round Surprise button, popovers), calmer cards/typography, map toolbar chips, sticky bar on desktop, compact mobile rows, dark-mode variables. Hidden <select id=var> kept for app logic. Place search ranking: exact > prefix > word. Backup archive/index_before_redesign.html. Copy-link button text now 'Copy link'.

(28) Fixes after review: gentle 1.2x nudge instead of strong zoom after picking a place; thin soft frame on 'Your place' box (no black/white thick border); birth year (4 digits) sets the time window start and switches horizon/emerge to trend; desktop: map card sticky and sized to the viewport, right panel shows key facts and folds the rest ('More numbers, planner and cell profile', 'N more facts'), 'How to read this' closed; html background fix for dark mode. Backup archive/index_before_fixes4.html.

(29) Airbnb-style panels: icon tiles + one-line descriptions for variables and views; place suggestions with pin icon, country/population and the cell's warming trend (from our data); header band separated by a thin line; longer place list. Backup archive/index_before_icons.html.

(30) Zoom after place pick / Surprise me / shared link now a ~7% nudge with soft recentering (was 1.2x / strong cell zoom); explicit 'Zoom to this cell' button keeps the strong zoom. Season chips got icons. Backup archive/index_before_zoom2.html.

(31) Map cell borders: uniform 1px non-scaling semi-transparent lines, graticule lines removed (white-stripe 'print' look). 'When' panel restyled like the others (season rows with icons + time window block). Backup archive/index_before_when.html.

(32) Validation extended with Met Office UK series (temp r=0.99, +0.30 vs +0.31 C/dec; precip r=0.90, +19.5 vs +15.0 mm/yr/dec, direction agrees, both n.s.; sunshine r=0.75, +2.2 vs +2.1 %/dec). 7 UK cells (>=50% UK, >=25% land). Files: uk_metoffice_annual.csv, validation_series.py/js, index table + texts. Backups archive/*_before_uk.*. Read from metoffice.gov.uk via built-in browser (same-origin fetch).

(33) Polish: tabular-nums, double focus ring on selected cell, legend marker (hovered/selected cell), pill-bar shadow, Surprise-me hover, Europe warming-stripes banner in header, hover enlargement in What/Where/View/When lists, visible scrollbar + "More" hint in the variable list, dark-mode contrast fix.

(34) Hover: pill-bar text no longer grows (page jitter); list items scale via transform only. Validation: Finland (r 0.99), Norway (0.94, POWER trend +0.32 vs +0.48), Latvia+Lithuania (0.99) from Berkeley Earth (to 2020), berkeley_north_europe_annual.csv added; page text/table/buttons, README updated.

(35) Sticky control bar: white background (no grey band), shrinks to a compact pill after ~150 px of scrolling, grows back on click (first click only expands), desktop only.

(36) Compact bar: first click on a pill expands the bar and opens that pill's menu; no white band behind the compact pill (pill only, with shadow).

(37) Validation: Ireland precipitation (mean of 8 Met Eireann stations via CSO MTM01, 1981-2022): r 0.89, trend +20.6 vs +10.7 mm/yr per decade (direction agrees). ireland_meteireann_annual.csv added. Compact bar already in (36).

(38) "Compare places" row (3 cases + "Choose two places yourself") moved out of the folded section, always visible. "Surprise me": 7 new extreme cases (strongest/weakest warming, wettest/driest trend, fastest soil drying, fastest humidity drop, steepest rise of days above 30 C), 12 stories in total.

(39) Cases laid out as two full rows of 4 (Oslo kept; Winter and Warming-yes-rain-not-yet moved up), compare row as one row of 4: Dublin/Warsaw, Stockholm/Madrid, new Krasnodar vs. Lisbon (fastest vs. slowest warming, replaces the sunshine-2001 button; the sunshine case remains under More questions), "Choose two places yourself". Removed 12 duplicate </head> tags. How to cite now names Met Eireann (CSO).

(40) Two-map view: map A and map B now start at exactly the same height (script measures the offset caused by B's extra controls and pads the shorter side; resets when the maps stack on narrow screens). Open idea for later: compact 3-step compass for first-time visitors.

(41) Tagline on two lines (second line bold); birth-year field as a pill without spin arrows, wide enough for "e.g. 1995"; year axis of the cell chart starts at 1981; Key findings: 6th card "14 checks" (validation, scrolls to the validation section), grid 3 x 2 (2 columns on medium, 1 on phones).

(42) Both tagline lines identical in size, weight and colour; year axis shows 1981, 1985, 1990, ...

(43) Dark mode: selected case/preset/toggle buttons were dark text on dark background; now light background with dark text.

(44) Comparison chart (two cells) axis starts at 1981 (1981, 1985, 1990, ...). Map toolbar in one line from about 1250 px width: labels shortened (Compare maps, Compare places, Save picture), smaller padding.

(45) Birth-year field accepts years from 1900 (before 1981 the window jumps to 1981 with the note that the data start there; this logic already existed).

(46) Personal flow via the Where pill: after choosing a town the "Your lifetime" box (own highlighted card right under the place facts, with birth-year pill) pulses once and the cursor jumps into the birth-year field (desktop only); hint under the search says to add the birth year. Years before 1981 jump to 1981 with a note.

(47) Choosing a town no longer scrolls the page and no longer moves the cursor into the birth-year field (the place is only step 2 of 4 in the bar). The "Your lifetime" card stays large; it still pulses once.

(48) BUG FIX: at 900 px width and below (half-window laptops, phones) a white layer from the new control-bar background covered the page header; fixed. Loading hint "Loading 44 years of climate data ..." shown until data.js has loaded.

(49) After external review: view "Warming vs. precipitation" renamed "Warming and rain, side by side" (two separate tests, no claim of a link); soil-moisture unit now reads "index units (0-1 scale)" in legend and panels. Checked: page works with all network requests blocked (no CDN, no external fonts); second click on a selected cell deselects; "Years needed" in a 10-year window shows "not reached"; trend-to-noise ratio is shown as the scatter plot in "Why do some places need more years?".

(50) Headline sentence above map (#headline, summarises current view); map always opens in full view (no zoom from link). index.html = f51.

(51) Search box no longer keeps an old town after map clicks (syncSearch); validation section grouped by variable and country, two-column layout (chart + r/trend panel), table sorted. index.html = f52.

(52) Map click now updates search box + headline (town of the clicked cell); validation side panel dark-mode fix (data-theme); Quick start visible as 4 step cards. index.html = f53.

(53) Time-window slider + Play now visible above the map (#winbar, synced with the When pill; hidden in views without a window). index.html = f54.

(54) Licence check: footer + README + SUBMISSION_TEXTS now list every source with its licence and attribution; Berkeley Earth is CC BY-NC 4.0 (not CC BY), marked as non-commercial. index.html = f55.
