import copy
import jinja2
import pendulum

from . import images

env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))

state_index = env.get_template("state/index.html.jinja")
state_debug = env.get_template("state/debug.html.jinja")
county_index = env.get_template("state/county/index.html.jinja")
# Render the index.
top_level = env.get_template("index.html.jinja")
top_level_debug = env.get_template("debug.html.jinja")


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
    upcoming_dates = [d for d in dates if d["date"].date() >= now.date()]

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
            if d["date"].date() > this_election["date"].date():
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
        reminder_date = pendulum.instance(next_reminder["date"])
        diff = reminder_date.diff(now, False)
        if diff.in_days() == 0:
            main_date = "Today!"
            secondary_date = reminder_date.format("(MMMM Do)")
        elif diff.in_days() == -1:
            main_date = "Tomorrow!"
            secondary_date = reminder_date.format("(MMMM Do)")
        else:
            main_date = reminder_date.format("MMMM Do")
            secondary_date = reminder_date.format("(dddd)")
        if "composite" in next_reminder:
            next_reminder["state"] = [r["state"] for r in next_reminder["reminders"]]
            next_reminder["state"] = sorted(list(set(next_reminder["state"])))
            actions = list(set((r["name"] for r in next_reminder["reminders"])))
            if len(next_reminder["state"]) > 1 and len(actions) > 1:
                next_reminder["name"] = "Check electioncal.us for deadlines"
            else:
                if all((a.startswith("Register to vote ") for a in actions)):
                    for i in range(1, len(actions)):
                        actions[i] = actions[i][len("Register to vote "):]
                next_reminder["name"] = ", ".join(actions[:-1]) + " or " + actions[-1]
                next_reminder["explanation"] = " ".join((r["explanation"] for r in next_reminder["reminders"] if "explanation" in r))
            next_reminder["name"] = next_reminder["name"].lower().capitalize()

    path = f"{language}"
    if state:
        state_lower = state["lower_name"]
        if county:
            county_lower = county["lower_name"]
            path = f"{language}/{state_lower}/{county_lower}"
        else:
            path = f"{language}/{state_lower}"

    data = {
        "alternatives": alternatives,
        "language": language,
        "dates": filtered_dates,
        "reminder": next_reminder,
        "main_date": main_date,
        "secondary_date": secondary_date,
        "path": path
    }
    template = top_level
    debug_template = None
    filenames = [f"site/{path}/index.html"]
    if state:
        template = state_index
        data["state"] = state
        data["demonym"] = state.get("demonym", "American")
        if county:
            data["county"] = county
            data["reminder_location"] = county["name"] + ", " + state["name"]
            template = county_index
        else:
            debug_template = state_debug
            county_list = list(counties.values())
            county_list.sort(key=lambda x: x["lower_name"])
            data["reminder_location"] = state["name"]
            data["counties"] = county_list
    else:
        state_list = list(states.values())
        state_list.sort(key=lambda x: x["lower_name"])
        if next_reminder:
            if isinstance(next_reminder["state"], list):
                data["reminder_location"] = ", ".join((states[s]["name"] for s in next_reminder["state"]))
                data["explanation"] = data["reminder_location"]
            else:
                data["reminder_location"] = states[next_reminder["state"]]["name"]
        data["states"] = state_list
        data["demonym"] = "American"
        if language == "en":
            filenames.append(f"site/index.html")
        debug_template = top_level_debug

    explanation = None
    if next_reminder:
        reminder = next_reminder["name"] + " by"
        if "explanation" in next_reminder:
            explanation = next_reminder["explanation"]
    else:
        reminder = "Help us add dates at"
        main_date = "github.com/electioncal/us"

    sec_date = None
    if secondary_date:
        sec_date = secondary_date.replace("(", "( ").replace(")", " )")

    images.render_twitter_image(
        f"site/{path}/twitter_card.png",
        state=state["name"] if state else None,
        county=county["name"] if county else None,
        reminder=reminder,
        main_date=main_date,
        secondary_date=sec_date,
        explanation=explanation)
    if debug_template:
        debug_twitter = dict(data)
        debug_twitter["debug_name"] = "Twitter Card"
        debug_twitter["filename"] = "twitter_card.png"
        debug_template.stream(debug_twitter).dump(f"site/{path}/debug_twitter.html")

    for filename in filenames:
        template.stream(data).dump(filename)
