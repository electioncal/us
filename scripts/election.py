import copy
import os
import tomlkit
import datetime

# Below we convert to Python dicts to allow None. We won't write back to TOML
federal_fn = os.path.join("federal-elections.toml")
with open(federal_fn, "r") as f:
    elections = dict(tomlkit.loads(f.read()))

for key in elections:
    election = dict(elections[key])
    election["details"] = {}
    election["key"] = key
    election["state"] = None
    election["county"] = None
    elections[key] = election

dates = []

methods = ["received_by", "in_person_by", "postmarked_by", "online_by"]
deadlines = {"absentee": ["application"]}

# Load per-state data.
for state in os.listdir("states/"):
    state_fn = os.path.join("states", state, "elections.toml")
    if not os.path.exists(state_fn):
        continue
    with open(state_fn, "r") as f:
        state_elections = dict(tomlkit.loads(f.read()))

    for key in state_elections:
        state_election = dict(state_elections[key])
        if key not in elections: # State election
            key = state + "/" + key
            state_election["state"] = state
            state_election["county"] = None
            state_election["key"] = key
            elections[key] = state_election
        deadline = {}
        deadline["state"] = state
        deadline["county"] = None
        deadline["name"] = ""
        deadline["type"] = "deadline"
        deadline["election_key"] = key
        for deadline_category in deadlines:
            if deadline_category in state_election:
                for method in methods:
                    if method in state_election[deadline_category]:
                        deadline["subtype"] = f"{deadline_category}.{method}"
                        deadline["date"] = state_election[deadline_category][method]
                        if isinstance(deadline["date"], datetime.date):
                            d = deadline["date"]
                            deadline["date"] = datetime.datetime(d.year, d.month, d.day, 23, 59, 59)
                        dates.append(copy.deepcopy(deadline))
                for stage in deadlines[deadline_category]:
                    if stage in state_election[deadline_category]:
                        for method in methods:
                            if method in state_election[deadline_category][stage]:
                                deadline["subtype"] = f"{deadline_category}.{stage}.{method}"
                                deadline["date"] = state_election[deadline_category][stage][method]
                                if isinstance(deadline["date"], datetime.date):
                                    d = deadline["date"]
                                    deadline["date"] = datetime.datetime(d.year, d.month, d.day, 23, 59, 59)
                                dates.append(copy.deepcopy(deadline))

    # Load per-county data.
    # counties = []
    # state_dir = os.path.join("states", fn)
    # for county_fn in os.listdir(state_dir):
    #     info_fn = os.path.join(state_dir, county_fn, "info.toml")
    #     if not os.path.exists(info_fn):
    #         continue
    #     with open(info_fn, "r") as f:
    #         county_info = tomlkit.loads(f.read())
    #     county_info["lower_name"] = county_fn
    #     counties.append(county_info)
    #     os.makedirs(f"site/en/{fn}/{county_fn}", exist_ok=True)
    #     county_data = {"language": "en", "state": state_info, "county": county_info}
    #     county_index.stream(county_data).dump(f"site/en/{fn}/{county_fn}/index.html")

# Listify
for key in elections:
    election = elections[key]
    election["type"] = "election"
    dates.append(election)

dates.sort(key=lambda x: x["date"])
