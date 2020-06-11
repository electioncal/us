# This script requires an API key from data.gov in the DATA_GOV_API_KEY environment variable.
# You can get one from https://api.data.gov/signup/ and they'll email it immediately.

import datetime
import os
import requests
import sys
import tomlkit

import states

api_key = os.environ["GOOGLE_CIVIC_API_KEY"]

url = f"https://www.googleapis.com/civicinfo/v2/elections?key={api_key}"

print(url)
data = requests.get(url)
print(data)
now = str(datetime.datetime.now().date())
for election in data.json()["elections"]:
    if election["id"] == "2000": # test elections
        continue
    print(election)

    postal_code = election["ocdDivisionId"][len("ocd-division/country:us/state:"):].upper()
    print(postal_code)

    lower_name = states.by_postal_code[postal_code]

    d = os.path.join("states", lower_name)
    elections_raw_fn = os.path.join(d, "elections_raw.toml")
    if os.path.exists(elections_raw_fn):
        with open(elections_raw_fn, "r") as f:
            elections_raw_file = tomlkit.loads(f.read())
    else:
        elections_raw_file = tomlkit.document()
        elections_raw_file.add(tomlkit.comment("This holds raw scraped data for reference and shouldn't be hand edited."))

    key = election["electionDay"].replace("-", "")

    empty_keys = []
    for k in election:
        if election[k] is None:
            empty_keys.append(k)
    for k in empty_keys:
        del election[k]
    if key not in elections_raw_file:
        elections_raw_file[key] = {}
    election["last_fetched"] = now
    elections_raw_file[key]["google_civic"] = election

    # print(tomlkit.dumps(elections_raw_file))

    with open(elections_raw_fn, "w") as f:
        f.write(tomlkit.dumps(elections_raw_file))
