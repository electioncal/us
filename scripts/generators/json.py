import json
import copy
import datetime

def generate(dates, output_filename, *, state_info=None, name=None, description=None, uid=None, states=None, counties=None):
    dates = copy.deepcopy(dates)
    path_parts = output_filename.split("/")
    top_level = {
        "version": 0,
        "name": name,
        "description": description,
        "dates": dates,
        "url": "https://electioncal.us/" + "/".join(path_parts[1:-1]) + "/",
        "source": "https://electioncal.us/" + "/".join(path_parts[1:])
    }
    for date in dates:
        date["date"] = date["date"].strftime("%Y-%m-%d")
        for key in date:
            value = date[key]
            if not isinstance(value, datetime.datetime):
                continue
            date[key] = value.strftime("%Y-%m-%d")
        if "details" in date:
            del date["details"]
        date["state"] = state_info["name"]

    with open(output_filename, "w") as f:
        json.dump(top_level, f)
