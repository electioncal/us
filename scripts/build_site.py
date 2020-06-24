import datetime
import os
from pathlib import Path
import tomlkit
import copy
import sys
import mistune
import jinja2

from generators import csv, ics, json, html

import election

os.makedirs("site", exist_ok=True)

states = {}

alternatives = [
    {"extension": "ics", "name": "https", "generator": ics.generate},
    {"extension": "csv", "name": "csv", "generator": csv.generate},
    {"extension": "json", "name": "json", "generator": json.generate},
]

specific_feed_name = "{} Election Dates by electioncal.us"
all_feed_name = "All Election Dates in {} by electioncal.us"

# Subtract by 7 hours so that days roll over with the Pacific timezone
now = datetime.datetime.utcnow() - datetime.timedelta(hours=7)
print("Now:", now)


env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
doc_template = env.get_template("doc.html.jinja")
docsdir = Path("docs/")

for doc in docsdir.glob("*/*.md"):
    d = os.path.join("site", doc.parent.name, "docs")
    os.makedirs(d, exist_ok=True)
    filename = os.path.join(d, doc.name.replace(".md", ".html"))
    data = {
        "doc": mistune.html(doc.read_text())
    }
    doc_template.stream(data).dump(filename)

# Load per-state data. fn for filename which is also the lower cased version of the state or county.
dbdir = Path("states/")

for state in dbdir.glob("*/info.toml"):
    state_info = dict(tomlkit.loads(state.read_text()))
    state_info["lower_name"] = state.parent.name
    state_info["counties"] = {}
    states[state.parent.name] = state_info

for county in dbdir.glob("*/counties/*/info.toml"):
    county_info = dict(tomlkit.loads(county.read_text()))
    county_info["lower_name"] = county.parent.name
    state = county.parent.parent.parent.name
    states[state]["counties"][county.parent.name] = county_info

for state_lower in states:
    state_info = states[state_lower]

    all_state_dates = [
        d for d in election.dates if d["state"] is None or d["state"] == state_lower
    ]

    # Load per-county data.
    counties = state_info["counties"]
    for county_lower in counties:
        county_info = counties[county_lower]
        os.makedirs(f"site/en/{state_lower}/{county_lower}", exist_ok=True)
        county_dates = [
            d
            for d in all_state_dates
            if d["county"] is None or d["county"] == county_lower
        ]
        upcoming_county_dates = [d for d in county_dates if d["date"] > now]

        for alternative in alternatives:
            extension = alternative["extension"]
            alternative["generator"](
                county_dates, f"site/en/{state_lower}/{county_lower}/voter.{extension}"
            )
        html.build(now, county_dates, state_info, dict(county_info), alternatives=alternatives)

    os.makedirs(f"site/en/{state_lower}", exist_ok=True)
    state_dates = [d for d in all_state_dates if d["county"] is None]

    for alternative in alternatives:
        extension = alternative["extension"]
        alternative["generator"](
            state_dates,
            f"site/en/{state_lower}/voter.{extension}",
            name=specific_feed_name.format(state_info["name"]),
        )
    for alternative in alternatives:
        extension = alternative["extension"]
        alternative["generator"](
            all_state_dates,
            f"site/en/{state_lower}/all-voter.{extension}",
            name=all_feed_name.format(state_info["name"]),
            counties=counties
        )

    html.build(now, state_dates, state_info, counties=counties, alternatives=alternatives)

federal_dates = [d for d in election.dates if d["state"] is None]
for alternative in alternatives:
    extension = alternative["extension"]
    alternative["generator"](
        federal_dates,
        f"site/en/voter.{extension}",
        name=all_feed_name.format("United States"),
    )
for alternative in alternatives:
    extension = alternative["extension"]
    alternative["generator"](
        election.dates,
        f"site/en/all-voter.{extension}",
        name=all_feed_name.format("United States"),
        states=states
    )
html.build(now, election.dates, states=states, alternatives=alternatives)
