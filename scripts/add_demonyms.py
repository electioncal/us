import os
import tomlkit

demonyms = open("geodata/demonyms.txt", "r")

skip = ["american_samoa", "district_of_columbia", "guam", "northern_mariana_islands", "puerto_rico", "u.s._virgin_islands"]

for fn in sorted(os.listdir("states")):
    info_fn = os.path.join("states", fn, "info.toml")
    if not os.path.exists(info_fn) or fn in skip:
        continue

    with open(info_fn, "r") as f:
        state_info = tomlkit.loads(f.read())
    state_info["demonym"] = demonyms.readline().strip()
    with open(info_fn, "w") as f:
        f.write(tomlkit.dumps(state_info))

demonyms.close()
