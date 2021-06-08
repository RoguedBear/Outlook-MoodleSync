#  Copyright (c) 2021 RoguedBear
import xml.dom.minidom
from datetime import datetime
from html import unescape
from typing import List

from dateutil import tz
from icalendar import Calendar, Event
from rfeed import Feed, Guid, Item


class SimpleEvent:
    def __init__(self, event: Event):
        self._original_event = event
        self.summary = unescape(str(event.get("SUMMARY", "")))
        self.description = str(event.get("DESCRIPTION", ""))
        self.category = unescape(str(event.get("CATEGORIES", "").cats[0]))
        self.dtstart: datetime = event["DTSTART"].dt.astimezone(tz.gettz("Asia/Calcutta"))
        self.dtend: datetime = event["DTEND"].dt.astimezone(tz.gettz("Asia/Calcutta"))
        self.last_mod: datetime = event['LAST-MODIFIED'].dt


def read_ics():
    """get a calendar object from ics file"""
    with open("calendar_.ics") as calendar:
        cal = Calendar.from_ical(calendar.read())
    return cal
    pass


def get_events(cal: Calendar) -> List[SimpleEvent]:
    events = []
    for event in cal.subcomponents:
        events.append(SimpleEvent(event))
    return events


def generate_feed_item(event: SimpleEvent) -> Item:
    description = f"""**Event:** {event.summary}
**Due by:** {event.dtend.strftime('%a %d %b, %H:%M:%S')}
**Subject:** {event.category}"""

    description += "" if event.description is None else (
        "\n" + event.description)
    return Item(title=f"{event.summary}",
                description=description,
                author="BouncePrime@protonmail.com (BouncePrime)",
                guid=Guid(event.summary, isPermaLink=False),
                pubDate=event.dtstart,
                )


def generate_feed() -> str:
    events_list = get_events(read_ics())

    feed_items = []
    for event in events_list:
        feed_items.append(generate_feed_item(event))

    feed = Feed(title="BU Moodle Assignment/Quizzes Dates",
                link="https://gist.github.com/RoguedBear/3b980fec6dd85b9308893f7727fde029",
                description="This RSS Feed alerts of new Assignments quizes and stuff. useful if you have rss reader"
                            "Custom made in Python 😉",
                language="en-US",
                lastBuildDate=datetime.utcnow(),
                items=feed_items)

    return xml.dom.minidom.parseString(feed.rss()).toprettyxml()
