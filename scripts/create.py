import csv
import tomlkit
import os

# Set to False to start over on info files.
merge = True

state_by_fips = {}
# Get states for state.txt which has more outlying areas.
f = open("geodata/state.txt", "r")
reader = csv.reader(f, delimiter="|")
for row in reader:
    if row[0] == "STATE":
        continue

    fips, postal, name, gnisid = row
    fips = int(fips)
    lower_name = name.lower().replace(" ", "_")
    d = os.path.join("states", lower_name)
    info_file = os.path.join(d, "info.toml")
    if merge and os.path.exists(info_file):
        with open(info_file, "r") as f:
            info = tomlkit.loads(f.read())
    else:
        info = {}
    info["name"] = name
    info["fips_code"] = fips
    info["postal_code"] = postal
    state_by_fips[fips] = lower_name
    os.makedirs(d, exist_ok=True)
    with open(info_file, "w") as f:
        f.write(tomlkit.dumps(info))

f.close()

# Get counties
f = open("geodata/all-geocodes-v2019.csv", "r")

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

    if level != 50: # everything but county
        continue
    info = {}
    info["name"] = name
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
