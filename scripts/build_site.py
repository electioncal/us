import os
import jinja2
import tomlkit

import election

os.makedirs("site", exist_ok=True)

env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))

states = []

state_index = env.get_template("state/index.html.jinja")
county_index = env.get_template("state/county/index.html.jinja")

# Load per-state data.
for fn in os.listdir("states/"):
    info_fn = os.path.join("states", fn, "info.toml")
    if not os.path.exists(info_fn):
        continue
    with open(info_fn, "r") as f:
        state_info = tomlkit.loads(f.read())
    state_info["lower_name"] = fn
    states.append(state_info)

    all_state_dates = [d for d in election.dates if d["state"] is None or d["state"] == fn]

    # Load per-county data.
    counties = []
    state_dir = os.path.join("states", fn)
    for county_fn in os.listdir(state_dir):
        info_fn = os.path.join(state_dir, county_fn, "info.toml")
        if not os.path.exists(info_fn):
            continue
        with open(info_fn, "r") as f:
            county_info = tomlkit.loads(f.read())
        county_info["lower_name"] = county_fn
        counties.append(county_info)
        os.makedirs(f"site/en/{fn}/{county_fn}", exist_ok=True)
        county_dates = [d for d in all_state_dates if d["county"] is None or d["county"] == county_fn]
        county_data = {"language": "en", "state": state_info, "county": county_info, "dates": county_dates}
        county_index.stream(county_data).dump(f"site/en/{fn}/{county_fn}/index.html")

    counties.sort(key=lambda x: x["lower_name"])
    os.makedirs(f"site/en/{fn}", exist_ok=True)
    state_dates = [d for d in all_state_dates if d["county"] is None]
    state_data = {"language": "en", "state": state_info, "counties": counties, "dates": state_dates}
    state_index.stream(state_data).dump(f"site/en/{fn}/index.html")

states.sort(key=lambda x: x["lower_name"])


# Render the index.
top_level = env.get_template("index.html.jinja")

federal_dates = [d for d in election.dates if d["state"] is None]
top = {"language": "en", "states": states, "dates": federal_dates}
top_level.stream(top).dump("site/index.html")
