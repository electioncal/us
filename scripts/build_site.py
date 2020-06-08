from pathlib import Path

import ics
import os
import jinja2
import tomlkit
import copy

import election

os.makedirs("site", exist_ok=True)

env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))

states = {}

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


def add_prefix(dates, *, states=None, counties=None):
    result = copy.deepcopy(dates)
    for date in result:
        if date["state"] and states:
            date["name"] = states[date["state"]]["name"] + " " + date["name"]
        elif date["county"] and counties:
            date["name"] = counties[date["county"]]["name"] + " " + date["name"]
    return result


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
            "language": "en",
            "state": state_info,
            "county": dict(county_info),
            "dates": county_dates,
        }
        ics.generate(county_dates, f"site/en/{state_lower}/{county_lower}/voter.ics")
        county_index.stream(county_data).dump(
            f"site/en/{state_lower}/{county_lower}/index.html"
        )

    county_list = list(counties.values())
    county_list.sort(key=lambda x: x["lower_name"])
    os.makedirs(f"site/en/{state_lower}", exist_ok=True)
    state_dates = [d for d in all_state_dates if d["county"] is None]
    state_dates = add_prefix(state_dates, counties=counties)
    state_data = {
        "language": "en",
        "state": state_info,
        "counties": county_list,
        "dates": state_dates,
    }
    ics.generate(
        state_dates,
        f"site/en/{state_lower}/voter.ics",
        name=specific_feed_name.format(state_info["name"]),
    )
    ics.generate(
        all_state_dates,
        f"site/en/{state_lower}/all-voter.ics",
        name=all_feed_name.format(state_info["name"]),
    )
    state_index.stream(state_data).dump(f"site/en/{state_lower}/index.html")

state_list = list(states.values())
state_list.sort(key=lambda x: x["lower_name"])

# Render the index.
top_level = env.get_template("index.html.jinja")

federal_dates = [d for d in election.dates if d["state"] is None]
top = {"language": "en", "states": state_list, "dates": federal_dates}
ics.generate(federal_dates, f"site/en/voter.ics",
        name=all_feed_name.format("United States"),)
national_dates = add_prefix(election.dates, states=states)
ics.generate(national_dates, f"site/en/all-voter.ics",
        name=all_feed_name.format("United States"),)
top_level.stream(top).dump("site/index.html")
