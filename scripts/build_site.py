import os
from pathlib import Path
import jinja2
import tomlkit
import copy

from generators import csv, ics, json

import election

os.makedirs("site", exist_ok=True)

env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))

states = {}

alternatives = [
    {"extension": "ics", "name": "https", "generator": ics.generate},
    {"extension": "csv", "name": "csv", "generator": csv.generate},
    {"extension": "json", "name": "json", "generator": json.generate},
]

state_index = env.get_template("state/index.html.jinja")
county_index = env.get_template("state/county/index.html.jinja")

specific_feed_name = "{} Election Dates by electioncal.us"
all_feed_name = "All Election Dates in {} by electioncal.us"

# Load per-state data. fn for filename which is also the lower cased version of the state or county.
dbdir = Path("states/")

for state in dbdir.glob("*/info.toml"):
    state_info = dict(tomlkit.loads(state.read_text()))
    state_info["lower_name"] = state.parent.name
    state_info["counties"] = {}
    states[state.parent.name] = state_info

for county in dbdir.glob("*/*/info.toml"):
    county_info = dict(tomlkit.loads(county.read_text()))
    county_info["lower_name"] = county.parent.name
    state = county.parent.parent.name
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
        county_data = {
            "alternatives": alternatives,
            "language": "en",
            "state": state_info,
            "county": dict(county_info),
            "dates": county_dates,
        }
        for alternative in alternatives:
            extension = alternative["extension"]
            alternative["generator"](
                county_dates, f"site/en/{state_lower}/{county_lower}/voter.{extension}"
            )
        county_index.stream(county_data).dump(
            f"site/en/{state_lower}/{county_lower}/index.html"
        )

    county_list = list(counties.values())
    county_list.sort(key=lambda x: x["lower_name"])
    os.makedirs(f"site/en/{state_lower}", exist_ok=True)
    state_dates = [d for d in all_state_dates if d["county"] is None]
    state_data = {
        "alternatives": alternatives,
        "language": "en",
        "state": state_info,
        "counties": county_list,
        "dates": state_dates,
    }
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
    state_index.stream(state_data).dump(f"site/en/{state_lower}/index.html")

state_list = list(states.values())
state_list.sort(key=lambda x: x["lower_name"])

# Render the index.
top_level = env.get_template("index.html.jinja")

federal_dates = [d for d in election.dates if d["state"] is None]
top = {
    "alternatives": alternatives,
    "language": "en",
    "states": state_list,
    "dates": federal_dates,
}
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
top_level.stream(top).dump("site/index.html")
top_level.stream(top).dump("site/en/index.html")
