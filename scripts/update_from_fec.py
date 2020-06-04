# This script requires an API key from data.gov in the DATA_GOV_API_KEY environment variable.
# You can get one from https://api.data.gov/signup/ and they'll email it immediately.

import os
import requests
import sys
import tomlkit

import states

api_key = os.environ["DATA_GOV_API_KEY"]

url = f"https://api.open.fec.gov/v1/election-dates/?page={{}}&sort_hide_null=false&per_page=100&sort_nulls_last=false&sort=-election_date&api_key={api_key}&min_election_date=06%2F01%2F2020&sort_null_only=false"

pages = None
page = 1
missing_states = set()
while pages is None or page <= pages:
    data = requests.get(url.format(page))
    if not data.ok:
        sys.exit(1)
    data = data.json()
    if pages is None:
        pages = data["pagination"]["pages"]

    for election in data["results"]:
        lower_name = states.by_postal_code[election["election_state"]]

        d = os.path.join("states", lower_name)
        elections_raw_fn = os.path.join(d, "elections_raw.toml")
        if os.path.exists(elections_raw_fn):
            with open(elections_raw_fn, "r") as f:
                elections_raw_file = tomlkit.loads(f.read())
        else:
            elections_raw_file = tomlkit.document()
            elections_raw_file.add(tomlkit.comment("This holds raw scraped data for reference and shouldn't be hand edited."))

        key = election["election_date"].replace("-", "")
        if lower_name == "idaho" and key == "20200602":
            key = "20200519"
        if lower_name == "north_carolina" and key == "20200623":
            key = "20200512"
        if key not in elections_raw_file and election["election_type_full"] != "Convention" and election["election_type_id"] != "CAU":
            print(election)
            print()
            continue
        empty_keys = []
        for k in election:
            if election[k] is None:
                empty_keys.append(k)
        for k in empty_keys:
            del election[k]
        if key not in elections_raw_file:
            elections_raw_file[key] = {}
        elections_raw_file[key]["fec"] = election

        with open(elections_raw_fn, "w") as f:
            f.write(tomlkit.dumps(elections_raw_file))

    page += 1
