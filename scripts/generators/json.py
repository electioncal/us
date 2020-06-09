import json
import copy

def generate(dates, output_filename, *, name=None, description=None, uid=None):
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
        date["original_date"] = date["original_date"].strftime("%Y-%m-%d")
        if "details" in date:
            del date["details"]

    with open(output_filename, "w") as f:
        json.dump(top_level, f)
