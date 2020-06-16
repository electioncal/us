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
        deadline_template = {}
        deadline_template["state"] = state
        deadline_template["county"] = None
        deadline_template["name"] = ""
        deadline_template["type"] = "deadline"
        deadline_template["election_key"] = key
        for deadline_category in deadlines:
            if deadline_category in state_election:
                for method in methods:
                    if method in state_election[deadline_category]:
                        deadline = copy.deepcopy(deadline_template)
                        deadline["subtype"] = f"{deadline_category}.{method}"
                        deadline["date"] = state_election[deadline_category][method]
                        if isinstance(deadline["date"], datetime.date):
                            d = deadline["date"]
                            deadline["date"] = datetime.datetime(d.year, d.month, d.day, 23, 59, 59)
                        if method == "postmarked_by":
                            deadline["postmark_too_late"] = False
                        dates.append(deadline)
                for stage in deadlines[deadline_category]:
                    if stage in state_election[deadline_category]:
                        for method in methods:
                            if method in state_election[deadline_category][stage]:
                                deadline = copy.deepcopy(deadline_template)
                                deadline["subtype"] = f"{deadline_category}.{stage}.{method}"
                                deadline["date"] = state_election[deadline_category][stage][method]
                                if isinstance(deadline["date"], datetime.date):
                                    d = deadline["date"]
                                    deadline["date"] = datetime.datetime(d.year, d.month, d.day, 23, 59, 59)

                                if method == "postmarked_by":
                                    deadline["postmark_too_late"] = False
                                dates.append(deadline)

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

# Use state and county to ensure a stable sort of dates.
def sort_key(x):
    state = x["state"]
    if not state:
        state = ""

    county = x["county"]
    if not county:
        county = ""
    return (x["date"], state, county)

dates.sort(key=sort_key)

last_postmarked = {}

# Add flag to postmarked by dates to indicate if they are within a week of the received by date.
for date in dates:
    if date["type"] != "deadline":
        continue
    postmark = date["subtype"].endswith(".postmarked_by")
    receive = date["subtype"].endswith(".received_by")
    action = ".".join(date["subtype"].split(".")[:-1])
    key = (date["state"], date["county"], action)
    if postmark:
        last_postmarked[key] = date
    if receive and key in last_postmarked:
        postmark_date = last_postmarked[key]
        delta = date["date"] - postmark_date["date"]
        if delta.days < 7:
            postmark_date["postmark_too_late"] = True
