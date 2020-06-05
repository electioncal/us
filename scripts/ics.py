import icalendar

def generate(dates, output_filename, *, name=None, description=None):
    c = icalendar.Calendar()
    c.add('prodid', '-//electioncal.us generator//circuitpython.org//')
    c.add('version', '2.0')

    for date in dates:
        event = icalendar.Event()
        event.add('summary', date["name"])
        event.add('dtstart', icalendar.vDate(date["date"]))
        c.add_component(event)
    with open(output_filename, "wb") as f:
        f.write(c.to_ical())


# def add_holiday_notice(calendar, d, note):
#     d = localize(d)

# def add_meeting_notice(calendar, d, note):
#     d = localize(d)
#     event = icalendar.Event()
#     event.add('summary', 'CircuitPython Discord Meeting' + note)
#     event.add('dtstart', icalendar.vDatetime(d))
#     event.add('dtend', icalendar.vDatetime(d + meeting_duration))
#     event.add('dtstamp', icalendar.vDatetime(now))
#     if 0:  # This doesn't work, makes google not show the calendar at all
#         event.add('conference',
#                   'https://adafru.it/discord',
#                   parameters= {'VALUE':'URI'})
#     calendar.add_component(event)
