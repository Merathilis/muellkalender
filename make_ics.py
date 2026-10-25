"""Erzeugt aus den MyMüll-Abfuhrterminen eine iCal-Datei (docs/muell.ics)."""
import datetime as dt
import json
import os
import urllib.request

CITY_ID = os.environ["CITY_ID"]
AREA_ID = os.environ["AREA_ID"]
BASE = "https://mymuell.jumomind.com"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "muell.ics")


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


names = {t["name"]: t["title"] for t in get(f"{BASE}/mmapp/api.php?r=trash&city_id={CITY_ID}&area_id={AREA_ID}")}
data = get(f"{BASE}/webservice.php?idx=termins&city_id={CITY_ID}&area_id={AREA_ID}&ws=3")[0]["_data"]
if not data:
    raise SystemExit("Keine Termine erhalten - bestehende Datei bleibt unverändert.")

lines = [
    "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//muellkalender//MyMuell Export//DE",
    "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:Müllabfuhr",
    "X-WR-TIMEZONE:Europe/Berlin", "REFRESH-INTERVAL;VALUE=DURATION:PT12H", "X-PUBLISHED-TTL:PT12H",
]
for x in sorted(data, key=lambda x: (x["cal_date"], x["cal_garbage_type"])):
    day = dt.date.fromisoformat(x["cal_date"])
    title = names.get(x["cal_garbage_type"], x["cal_garbage_type"])
    desc = "Abfuhrtermin laut MyMüll" + (r"\n" + x["cal_comment"] if x["cal_comment"] else "")
    lines += [
        "BEGIN:VEVENT", f"UID:mymuell-{x['cal_id']}", f"DTSTAMP:{day:%Y%m%d}T000000Z",
        f"DTSTART;VALUE=DATE:{day:%Y%m%d}", f"DTEND;VALUE=DATE:{day + dt.timedelta(days=1):%Y%m%d}",
        f"SUMMARY:{title}", f"DESCRIPTION:{desc}", "TRANSP:TRANSPARENT", "CATEGORIES:Müllabfuhr",
        "BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:Morgen: {title}", "TRIGGER:-PT6H", "END:VALARM",
        "END:VEVENT",
    ]
lines.append("END:VCALENDAR")

with open(OUT, "w", encoding="utf-8", newline="") as f:
    f.write("\r\n".join(lines) + "\r\n")
print(f"{len(data)} Termine geschrieben")
