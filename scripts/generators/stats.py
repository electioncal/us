import copy
import jinja2
import pendulum

env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))

# Render the index.
top_level = env.get_template("stats/index.html.jinja")


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

    for d in upcoming_dates:
        if d["type"] != "election":
            continue
        if d["state"] is None:
            for s in states.values():
                if "next_election" not in s:
                    s["next_election"] = d
        else:
            s = states[d["state"]]
            if "next_election" not in s:
                s["next_election"] = d

    types = ["election", "deadline", "reminder"]
    for s in states.values():
        s["counts"] = {}
        for t in types:
            s["counts"][t] = 0

    for d in upcoming_dates:
        t = d["type"]
        if d["county"]:
            continue
        if d["state"] is None:
            for s in states.values():
                s["counts"][t] += 1
            continue
        states[d["state"]]["counts"][t] += 1

    path = f"{language}/stats"
    if state:
        state_lower = state["lower_name"]
        if county:
            county_lower = county["lower_name"]
            path = f"{language}/stats/{state_lower}/{county_lower}"
        else:
            path = f"{language}/stats/{state_lower}"

    data = {
        "alternatives": alternatives,
        "language": language,
        "path": path
    }
    template = top_level
    filename = f"site/{path}/index.html"
    if state:
        data["state"] = state
        if county:
            data["county"] = county
        else:
            county_list = list(counties.values())
            county_list.sort(key=lambda x: x["lower_name"])
            data["counties"] = county_list
    else:
        state_list = list(states.values())
        state_list.sort(key=lambda x: x["next_election"]["date"])
        data["states"] = state_list

    template.stream(data).dump(filename)
