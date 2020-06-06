# Fixes &amp; in election names.

import os
import tomlkit


# Load per-state data.
for state in os.listdir("states/"):
    state_fn = os.path.join("states", state, "elections.toml")
    if not os.path.exists(state_fn):
        continue
    with open(state_fn, "r") as f:
        state_elections = tomlkit.loads(f.read())

    for key in state_elections:
        state_elections[key]["name"] = state_elections[key]["name"].replace("&amp;", "&")

    # print(tomlkit.dumps(state_elections))
    with open(state_fn, "w") as f:
        f.write(tomlkit.dumps(state_elections))
