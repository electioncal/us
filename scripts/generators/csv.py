import copy
import csv

all_deadline_descriptions = {
    "absentee.postmarked_by": "Last day to postmark absentee ballots in {}",
    "absentee.received_by": "Last day for election officials to receive absentee ballots in {}",
    "absentee.in_person_by": "Last day to hand deliver an absentee ballot in {}",
    "absentee.application.online_by": "Last day to apply online for a mail-in ballot in {}.",
    "absentee.application.postmarked_by": "Last day to postmark absentee applications in {}",
    "absentee.application.received_by": "Last day for election officials to receive absentee applications in {}",
    "absentee.application.in_person_by": "Last day to hand deliver an absentee applications in {}"
}

deadline_descriptions = {
    "absentee.postmarked_by": "Last day to get your absentee ballot postmarked. Drop off at the post office!",
    "absentee.received_by": "Last day for election officials to receive your absentee ballot. Mail early!",
    "absentee.in_person_by": "Last day to hand deliver your absentee ballot. Check drop off hours!",
    "absentee.application.online_by": "Last day to apply online for a mail-in ballot.",
    "absentee.application.postmarked_by": "Last day to get your absentee application postmarked. Drop off at the post office!",
    "absentee.application.received_by": "Last day for election officials to receive your absentee application. Mail early!",
    "absentee.application.in_person_by": "Last day to hand deliver your absentee application. Check drop off hours!"
}

def generate(dates, output_filename, *, name=None, description=None, uid=None, states=None, counties=None):
    columns = ["date", "key", "type", "subtype", "name", "original_date", "state", "county", "postmark_too_late"]
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
            if date["type"] == "deadline":
                if name:
                    desc = all_deadline_descriptions.get(date["subtype"], None)
                    if not desc:
                        print("missing description for", date["subtype"])
                    else:
                        date["name"] = desc.format(name)
                else:
                    desc = deadline_descriptions.get(date["subtype"], None)
                    if not desc:
                        print("missing description for", date["subtype"])
                    else:
                        date["name"] = desc
            elif date["type"] == "election" and name:
                date["name"] = name + " " + date["name"]
            writer.writerow(date)
