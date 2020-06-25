import copy
import os
import tomlkit
import datetime
import pendulum

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
deadlines = {"absentee": ["application"],
             "poll": ["early", "overseas_military"],
             "registration" : []}

# Load per-state data.
for state in os.listdir("states/"):
    state_fn = os.path.join("states", state, "elections.toml")
    if not os.path.exists(state_fn):
        continue
    with open(state_fn, "r") as f:
        state_elections = dict(tomlkit.loads(f.read()))

    for key in state_elections:
        state_election = dict(state_elections[key])
        state_key = state + "/" + key
        if key not in elections and state_key not in elections: # State election
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
                        if method == "received_by":
                            deadline["postmark_too_late"] = True
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
                                if method == "received_by":
                                    deadline["postmark_too_late"] = True
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

# convert dates to plain datetime objects
for date in dates:
    for k in date:
        v = date[k]
        if isinstance(v, tomlkit.items.Date):
            date[k] = datetime.datetime(v.year, v.month, v.day, 0, 0, 0)
        elif isinstance(v, tomlkit.items.DateTime):
            date[k] = datetime.datetime(v.year, v.month, v.day, v.hour, v.minute, v.second)

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
            date["postmark_too_late"] = True
        else:
            postmark_date["postmark_too_late"] = False
            date["postmark_too_late"] = False


# Add deadline titles and reminders.
deadline_descriptions = {
    "absentee.postmarked_by": "Last day to postmark absentee ballots",
    "absentee.received_by": "Last day for election officials to receive absentee ballots",
    "absentee.in_person_by": "Last day to drop off an absentee ballot",
    "absentee.application.online_by": "Last day to apply online for a mail-in ballot",
    "absentee.application.postmarked_by": "Last day to postmark absentee applications",
    "absentee.application.received_by": "Last day for election officials to receive absentee applications",
    "absentee.application.in_person_by": "Last day to hand deliver an absentee applications",
    "poll.in_person_by": "Last day to vote in person",
    "poll.early.in_person_by": "Last day to vote early in person",
    "poll.overseas_military.received_by": "Last day for election officials to receive military and overseas ballots",
    "registration.received_by": "Last day for election officials to receive voter registration form",
    "registration.postmarked_by": "Last day to postmark voter registration form",
    "registration.in_person_by": "Last day to register to vote in person",
    "registration.online_by": "Last day to register to vote online",
}

one_day = datetime.timedelta(days=1)
one_week = datetime.timedelta(days=7)

reminders = []
for date in dates:
    if date["type"] == "deadline":
        desc = deadline_descriptions.get(date["subtype"], None)
        if not desc:
            print("missing description for", date["subtype"])
        else:
            date["name"] = desc
        subtype = date["subtype"]
        item = "ballot"
        if subtype.startswith("absentee.application"):
            item = "absentee application"
        if subtype.startswith("registration"):
            item = "voter registration"
        if subtype.endswith("postmarked_by") and not date["postmark_too_late"]:
            reminder = copy.deepcopy(date)
            reminder["type"] = "reminder"
            reminder["deadline_date"] = reminder["date"]
            friendly_date = pendulum.instance(reminder["date"]).format("MMMM Do")
            reminder["explanation"] = f"{item.capitalize()} must be postmarked by {friendly_date}."

            mail = copy.deepcopy(reminder)
            mail["date"] = reminder["date"] - one_day
            mail["name"] = f"Mail {item}"
            reminders.append(mail)

            post_office = copy.deepcopy(reminder)
            post_office["name"] = f"Mail {item} at the post office" # today
            reminders.append(post_office)
        if subtype.endswith("received_by") and date["postmark_too_late"]:
            reminder = copy.deepcopy(date)
            reminder["type"] = "reminder"
            reminder["deadline_date"] = reminder["date"]
            friendly_date = pendulum.instance(reminder["date"]).format("MMMM Do")
            reminder["explanation"] = f"{item.capitalize()} must be received by {friendly_date}."

            mail = copy.deepcopy(reminder)
            mail["date"] = reminder["date"] - one_day - one_week
            mail["name"] = f"Mail {item}"
            reminders.append(mail)

            post_office = copy.deepcopy(reminder)
            post_office["name"] = f"Mail {item} at the post office"
            post_office["date"] = reminder["date"] - one_week
            reminders.append(post_office)
        if subtype.endswith("in_person_by"):
            reminder = copy.deepcopy(date)
            reminder["type"] = "reminder"
            reminder["deadline_date"] = reminder["date"]

            vote = copy.deepcopy(reminder)
            vote["date"] = reminder["date"]
            if subtype.startswith("poll.early"):
                vote["name"] = "Vote early in person"
            elif subtype.startswith("poll"):
                plan = copy.deepcopy(reminder)
                plan["name"] = "Plan to vote"
                plan["date"] -= one_day
                reminders.append(plan)

                vote["name"] = "Vote in person"
                d = reminder["date"]
                vote["start_date"] = datetime.datetime(d.year, d.month, d.day)
            elif subtype.startswith("absentee.application"):
                vote["name"] = "Drop off absentee application"
            elif subtype.startswith("absentee"):
                vote["name"] = "Drop off ballot"
            elif subtype.startswith("registration"):
                vote["name"] = "Register to vote in person"
            reminders.append(vote)
        if subtype.endswith("online_by"):
            reminder = copy.deepcopy(date)
            reminder["type"] = "reminder"
            reminder["deadline_date"] = reminder["date"]

            vote = copy.deepcopy(reminder)
            vote["date"] = reminder["date"]
            if subtype.startswith("absentee.application"):
                vote["name"] = "Apply for an absentee ballot online"
            elif subtype.startswith("registration"):
                vote["name"] = "Register to vote online"
            reminders.append(vote)


dates.extend(reminders)
dates.sort(key=sort_key)

if __name__ == "__main__":
    import sys
    for date in dates:
        if date["state"] == sys.argv[1] and date["type"] == "reminder":
            print(date["date"], date["name"], date.get("subtype", ""), sep="\t")
