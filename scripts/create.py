import csv
import tomlkit
import os

f = open("geodata/all-geocodes-v2019.csv", "r")

state_by_fips = {}

merge = True

reader = csv.reader(f)

for row in reader:
    if not row[-1]:
        continue
    if row[0] == "Summary Level":
        continue
    level, state_fips, county_fips, _, _, _, name = row
    level = int(level)

    if level > 50:
        continue
    state_fips = int(state_fips)
    county_fips = int(county_fips)

    if level == 10: # nation
        continue

    info = {}
    info["name"] = name
    if state_fips == 11: # district of colombia
        if level == 50:
            continue
        # Fall through to state but not county

    if level == 40: # state
        lower_name = name.lower().replace(" ", "_")
        d = os.path.join("states", lower_name)
        info["fips_code"] = state_fips
        state_by_fips[state_fips] = lower_name
        os.makedirs(d, exist_ok=True)
        info_file = os.path.join(d, "info.toml")
        if merge and os.path.exists(info_file):
            with open(info_file, "r") as f:
                previous = tomlkit.loads(f.read())
                previous.update(info)
                info = previous
        with open(info_file, "w") as f:
            f.write(tomlkit.dumps(info))
    elif level == 50: # county
        state_name = state_by_fips[state_fips]
        # Lowercase, _ and remove qualifier (usually "county")
        lower_name = "_".join(name.lower().split()[:-1])
        d = os.path.join("states", state_name, lower_name)
        info["fips_code"] = state_fips * 1000 + county_fips
        os.makedirs(d, exist_ok=True)
        info_file = os.path.join(d, "info.toml")
        if merge and os.path.exists(info_file):
            with open(info_file, "r") as f:
                previous = tomlkit.loads(f.read())
                previous.update(info)
                info = previous
        with open(info_file, "w") as f:
            f.write(tomlkit.dumps(info))
        print("https://electioncal.us/{}/{}/".format(state_name, lower_name))

f.close()
