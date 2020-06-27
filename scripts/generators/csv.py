import copy
import csv

def generate(dates, output_filename, *, state_info=None, name=None, description=None, uid=None, states=None, counties=None):
    columns = ["date", "key", "election_key", "type", "subtype", "name", "original_date", "state", "county", "postmark_too_late"]
    with open(output_filename, "w") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")

        writer.writeheader()
        for date in dates:
            date = copy.deepcopy(date)
            name = None
            if date["state"] and states:
                name = states[date["state"]]["name"]
            elif date["county"] and counties:
                name = counties[date["county"]]["name"]
            if date["type"] == "election" and name:
                date["name"] = name + " " + date["name"]
            date["state"] = state_info["name"]
            writer.writerow(date)
