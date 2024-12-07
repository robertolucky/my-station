import datetime
import os.path
import os
import logging
from xml.sax.saxutils import escape
from base_provider import CalendarEvent
from google import GoogleCalendar
from utility import get_formatted_time, update_svg, configure_logging, get_formatted_date, configure_locale, add_today_date

configure_locale()
configure_logging()

# note: increasing this will require updates to the SVG template to accommodate more events
max_event_results = int(os.getenv("MAX_EVENT_RESULTS", 3))
google_calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
ttl = float(os.getenv("CALENDAR_TTL", 1 * 60 * 60))
fake_event_h=int(os.getenv("FAKE_EVENT_H",8))
output_svg_filename = str(os.getenv("CALENDAR_TEMPLATE", 'screen-temp-rob.svg'))

def get_formatted_calendar_events(fetched_events: list[CalendarEvent]) -> dict:
    formatted_events = {}
    event_count = len(fetched_events)

    for index in range(max_event_results):
        event_label_id = str(index + 1)
        if index <= event_count - 1:
            formatted_events['CAL_DATETIME_' + event_label_id] = get_datetime_formatted(fetched_events[index].start, fetched_events[index].end, fetched_events[index].all_day_event)
            formatted_events['CAL_DATETIME_START_' + event_label_id] = get_datetime_formatted(fetched_events[index].start, fetched_events[index].end, fetched_events[index].all_day_event, True)
            formatted_events['CAL_DESC_' + event_label_id] = fetched_events[index].summary
        else:
            formatted_events['CAL_DATETIME_' + event_label_id] = ""
            formatted_events['CAL_DESC_' + event_label_id] = ""

    return formatted_events


def get_datetime_formatted(event_start, event_end, is_all_day_event, start_only=False):

    if is_all_day_event or type(event_start) == datetime.date:
        start = datetime.datetime.combine(event_start, datetime.time.min)
        end = datetime.datetime.combine(event_end, datetime.time.min)

        start_day = get_formatted_date(start, include_time=False)
        end_day = get_formatted_date(end, include_time=False)
        if start == end:
            day = start_day
        else:
            day = "{} - {}".format(start_day, end_day)
    elif type(event_start) == datetime.datetime:
        start_date = event_start
        end_date = event_end
        if start_date.date() == end_date.date():
            start_formatted = get_formatted_date(start_date)
            end_formatted = get_formatted_time(end_date)
        else:
            start_formatted = get_formatted_date(start_date)
            end_formatted = get_formatted_date(end_date)
        day = start_formatted if start_only else "{} - {}".format(start_formatted, end_formatted)
    else:
        day = ''
    return day

def init_calendar():
    today_start_time = (datetime.datetime.now()
                        - datetime.timedelta(minutes=30))
    oneweeklater_iso = (datetime.datetime.now()
                        + datetime.timedelta(days=7))

    logging.info("Fetching Google Calendar Events")
    provider = GoogleCalendar(google_calendar_id, max_event_results, today_start_time, oneweeklater_iso)
    return provider

def push_event(message="ignore this event"):
    start_time = datetime.datetime.combine(datetime.date.today(), datetime.time(fake_event_h, 0))
    end_time = datetime.datetime.combine(datetime.date.today(), datetime.time(fake_event_h, 15))
    provider=init_calendar()
    provider.create_event(message, start_time, end_time)


def update_and_return():
    provider = init_calendar()
    calendar_events = provider.get_calendar_events()
    first_event = calendar_events[0].start
    output_dict = get_formatted_calendar_events(calendar_events)
    add_today_date(output_dict)
    # XML escape for safety
    for key, value in output_dict.items():
        output_dict[key] = escape(value)

    logging.info("Updating SVG")
    update_svg(output_svg_filename, 'output_svg.svg', output_dict)
    return first_event

if __name__ == "__main__":
    print(update_and_return())