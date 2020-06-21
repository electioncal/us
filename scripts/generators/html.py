import copy
import jinja2
import pendulum

env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))

state_index = env.get_template("state/index.html.jinja")
county_index = env.get_template("state/county/index.html.jinja")
# Render the index.
top_level = env.get_template("index.html.jinja")


def build(
    now,
    dates,
    state=None,
    county=None,
    *,
    language="en",
    alternatives=[],
    name=None,
    description=None,
    uid=None,
    states=None,
    counties=None,
):

    upcoming_dates = [d for d in dates if d["date"] > now]

    # Determine the next two elections.
    this_election = None
    next_election = None
    for d in upcoming_dates:
        if d["type"] == "election":
            if not this_election:
                this_election = d
            elif not next_election:
                next_election = d
            else:
                break

    # Filter down to the next reminder date, deadlines up to the next election and
    # the next election.
    next_reminder = None
    filtered_dates = []
    for d in upcoming_dates:
        if d["type"] == "election":
            if d != this_election and d != next_election:
                continue
        elif d["type"] == "deadline":
            if d["date"] > this_election["date"]:
                continue
        elif d["type"] == "reminder":
            if "start_date" in d and now < d["start_date"]:
                continue
            if not next_reminder:
                next_reminder = d
            elif next_reminder["date"].date() == d["date"].date():
                if "composite" not in next_reminder:
                    next_reminder = {
                        "composite": True,
                        "reminders": [next_reminder],
                        "date": d["date"],
                        "deadline_date": d["date"]
                    }
                next_reminder["reminders"].append(d)
            continue
        filtered_dates.append(d)

    # if next_reminder and state and not county:
    #     print(state["name"])
    #     reminders = []
    #     if "composite" in next_reminder:
    #         reminders.extend(next_reminder["reminders"])
    #     else:
    #         reminders.append(next_reminder)
    #     for reminder in reminders:
    #         print("\t", reminder)

    main_date = None
    secondary_date = None
    if next_reminder:
        now = pendulum.instance(now)
        reminder_date = pendulum.instance(next_reminder["deadline_date"])
        diff = reminder_date.diff(now, False)
        if diff.in_days() == 0:
            main_date = "Today!"
            secondary_date = reminder_date.format("(MMMM Do)")
        if diff.in_days() == 1:
            main_date = "Tomorrowı!"
            secondary_date = reminder_date.format("(MMMM Do)")
        else:
            main_date = reminder_date.format("MMMM Do")
            secondary_date = reminder_date.format("(dddd)")

    data = {
        "alternatives": alternatives,
        "language": language,
        "dates": filtered_dates,
        "reminder": next_reminder,
        "main_date": main_date,
        "secondary_date": secondary_date,
    }
    template = top_level
    filenames = []
    if state:
        template = state_index
        data["state"] = state
        state_lower = state["lower_name"]
        if county:
            data["county"] = county
            template = county_index
            county_lower = county["lower_name"]
            filenames.append(f"site/{language}/{state_lower}/{county_lower}/index.html")
        else:
            data["counties"] = counties
            filenames.append(f"site/{language}/{state_lower}/index.html")
    else:
        data["states"] = states
        filenames.append(f"site/{language}/index.html")
        if language == "en":
            filenames.append(f"site/index.html")

    for filename in filenames:
        template.stream(data).dump(filename)
