# This script requires an API key from data.gov in the DATA_GOV_API_KEY environment variable.
# You can get one from https://api.data.gov/signup/ and they'll email it immediately.

import os
import requests
import sys

import states

api_key = os.environ["DATA_GOV_API_KEY"]

url = f"https://api.open.fec.gov/v1/election-dates/?page={{}}&sort_hide_null=false&per_page=100&sort_nulls_last=false&sort=-election_date&api_key={api_key}&min_election_date=06%2F01%2F2020&sort_null_only=false"

pages = None
page = 1
while pages is None or page <= pages:
    data = requests.get(url.format(page))
    if not data.ok:
        sys.exit(1)
    data = data.json()
    if pages is None:
        pages = data["pagination"]["pages"]

    for election in data["results"]:
        if election["election_state"] not in states.by_fec:
            print(election)
            print()

    page += 1
