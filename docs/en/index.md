# ElectionCal.US

Election **Cal**endar's goal is to get more people voting by making deadlines easily accessible and sharable. This has two main parts, first is collecting election dates and deadlines. This data is stored in hand-editable TOML files. These files are loaded by `build_site.py` and transformed into three types of dates, election dates, election deadlines and reminders.

The second piece to the puzzle is creating a variety of machine and human readable forms of the dates and reminders. Different generators produce different output formats. `build_site.py` will also manage splitting dates by state and county. Aggregate outputs are also done for federal and state levels to include subdivision specific dates, such as a county deadline in the aggregate state feed.

## TOML format

There are three main types of TOML files.

- `info.toml` files are meant to hold election agnostic data about the state or county. This data can be helpful when normalizing across data sources and also when presenting info about the state.
- `elections.toml` files are meant to hold data for specific election dates. elections dates are keyed by their narrowest scope. So, the federal general election is just a date because it is in the top level `elections.toml`. Individual states and counties can still have unique deadlines for the federal election date. The election date key is the original date of the election and therefore stays the same if the date changes.
- `elections_raw.toml` is a dump of election related data and resources based on scraping. It shouldn't be hand edited but could be a starting point for adding data to the other two files.

### `elections.toml`

Here is an example of election deadlines from the June 23rd New York election:

```toml
[20200623]
date = 2020-06-23
name = "Congressional Primary"
original_date = 2020-06-23

[20200623.registration]
in_person_by = 2020-06-13
postmarked_by = 2020-05-29
received_by = 2020-06-03

[20200623.poll]
in_person_by = 2020-06-23

[20200623.poll.early]
in_person_starts = 2020-06-13
in_person_by = 2020-06-21
sources = ["https://www.elections.ny.gov/NYSBOE/news/2020VotingOptionsDeadlinesforJunePrimary.pdf"]

[20200623.absentee]
postmarked_by = 2020-06-22
in_person_by = 2020-06-23
received_by = 2020-06-30
overseas_received_by = 2020-07-06
sources = ["https://www.elections.ny.gov/NYSBOE/law/June2020SpecElecPolCalendar0429.pdf",
           "https://www.elections.ny.gov/VotingDeadlines.html#AbsenteeDeadlines"]

[20200623.absentee.application]
postmarked_by = 2020-06-16
in_person_by = 2020-06-22
```

The `[]` portions are `.` separated keys known as "tables" in TOML. [Here](https://github.com/toml-lang/toml/blob/master/toml.md) is a good toml reference.

The date in the `[]` is the original election date, aka the election key. After the `.` is an id for different phases (or actions maybe) of the election. They are:

- `registration` - Registering to vote in the election. It doesn't impact *how* one would be able to vote.
- `poll` - Voting in-person on election day. This will be omitted for mail-in only states like Washington.
- `poll.early` - Voting in-person prior to election day.
- `absentee` - Voting by mail.
- `absentee.application` - This is applying for an absentee ballot after registration but before the election. It doesn't include in-person absentee.

(We should make `absentee.overseas` instead of `overseas_received_by`.)

Each of these phases can be accomplished in a variety of ways. Though not all phases can happen in all ways. (`poll.*` is only ever in person.)

- `in_person_start`/`in_person_by` These are the dates one can accomplish the task (or phase) by going to a physical location to vote or drop off the ballot or application.
- `postmarked_by` This is the last date an application or ballot can be postmarked to be valid. It'll trigger reminders to mail the day before and drop off at the post office on the day-of. It may be ignored if the `received_by` date is too close.
- `received_by` This is the last date an application or ballot can be received by the appropriate election official through the mail. We bake in a 1 week USPS transit time into reminders. (For absentee applications is really should be ~4 weeks. One for the application mailing, one for processing, one for absentee ballot to the voter and one from the voter.)

`sources` isn't currently used be may be used in descriptions to demonstrate validity of the dates.
