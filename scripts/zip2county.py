import csv
from pathlib import Path
import tomlkit

zips_by_county = {}

county_by_zip = {}

with open("geodata/zcta_county_rel_10.txt", "r") as f:
    f.readline() # read the header line
    for line in csv.reader(f):
        zipcode = int(line[0])
        state_fips_code = int(line[1])
        county_fips_code = int(line[3])
        percent_zip_in_county = float(line[-8])
        if county_fips_code not in zips_by_county:
            zips_by_county[county_fips_code] = []
        zips_by_county[county_fips_code].append({"zipcode": zipcode, "percent_zip_in_county": percent_zip_in_county})

        if zipcode not in county_by_zip:
            county_by_zip[zipcode] = []
        county_by_zip[zipcode].append((county_fips_code, percent_zip_in_county))

# Update county info files.
root = Path("states/")
for county_path in root.glob("*/counties/*/info.toml"):
    county_info = tomlkit.loads(county_path.read_text())
    fips = county_info["fips_code"]
    if fips not in zips_by_county:
        print("No zips for", county_info["name"])
        continue
    county_info["zipcodes"] = zips_by_county[fips]
    county_path.write_text(tomlkit.dumps(county_info))
