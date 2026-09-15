# fifa-wc2026-schedule-venues — sample

Source: https://github.com/mominullptr/FIFA-World-Cup-2026-Dataset (CC0-1.0, last push 17 Aug 2026; also on Kaggle).
FIFA World Cup 2026 relational dataset: 16 host venues (city, country, capacity, lat/lon), 104 matches
(date, UTC kickoff, stage, venue, teams, results, xG), 48 teams, 7 tournament stages. Matches run 11 Jun - 19 Jul 2026.
Pulled 14 Sep 2026 with curl from raw.githubusercontent.com/<repo>/HEAD/<file>; five CSVs, 33 KB total (no caps hit).
Not pulled by design: player/lineup/event/team-stats CSVs, real_match_details.json, sqlite db (~1.4 MB whole repo).
Full dataset: `git clone --depth 1 https://github.com/mominullptr/FIFA-World-Cup-2026-Dataset`.
ABNB use: venue city x match date -> daily host-market event-intensity calendar for the 3Q26 nights/ADR shock in
11 US, 2 Canadian and 3 Mexican metros. Note venues.csv gives stadium municipalities (Arlington, Inglewood, Foxborough,
Santa Clara, Guadalupe, Zapopan), so a metro mapping must be added. Spot-check scores against FIFA.com before using results.
