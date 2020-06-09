import csv

def generate(dates, output_filename, *, name=None, description=None, uid=None):
    columns = ["date", "key", "type", "name", "original_date", "state", "county"]
    with open(output_filename, "w") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")

        writer.writeheader()
        for date in dates:
            writer.writerow(date)
