#  Copyright (c) 2021-22 RoguedBear
"""
This file is part of Moodle-Calendar-Sync.

Moodle-Calendar-Sync is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

Moodle-Calendar-Sync is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
Moodle-Calendar-Sync. If not, see <https://www.gnu.org/licenses/>.
"""

import xml.dom.minidom
from datetime import datetime
from html import unescape
from typing import List

from dateutil import tz
from icalendar import Calendar, Event
from rfeed import Feed, Guid, Item


class SimpleEvent:
    mapping = dict()

    def __init__(self, event: Event):
        self._original_event = event
        self.summary = unescape(str(event.get("SUMMARY", "")))
        self.description = str(event.get("DESCRIPTION", ""))
        self.category = unescape(str(event.get("CATEGORIES", "").cats[0]))
        self.dtstart: datetime = event["DTSTART"].dt.astimezone(tz.gettz("Asia/Calcutta"))
        self.dtend: datetime = event["DTEND"].dt.astimezone(tz.gettz("Asia/Calcutta"))
        self.last_mod: datetime = event['LAST-MODIFIED'].dt
        self.isquiz = False if self.dtstart == self.dtend else True

    @property
    def human_readable_sub_name(self):
        name = self.mapping.get(self.category, "")
        if name:
            return f" | `{name}`"
        else:
            return ""


def init_mapping(config: dict, logger):
    mapping_list: list = config.get("mapping", [])
    mapping_dict = dict()
    try:
        for dict_ in mapping_list:
            mapping_dict[dict_["code"]] = dict_["name"]
    except KeyError:
        logger.error("INVALID mapping specified! no key 'name' or 'code'")
    else:
        SimpleEvent.mapping = mapping_dict


def read_ics():
    """get a calendar object from ics file"""
    with open("calendar_.ics", encoding="utf-8") as calendar:
        cal = Calendar.from_ical(calendar.read())
    return cal
    pass


def get_events(cal: Calendar) -> List[SimpleEvent]:
    events = []
    for event in cal.subcomponents:
        events.append(SimpleEvent(event))
    return events


def generate_feed_item(event: SimpleEvent) -> Item:
    description = [f"**Event:** {event.summary}",
                   f"**Subject:** {event.category}"]
    if event.isquiz:
        description.insert(1, f"**Starting time:** {event.dtend.strftime('%a %d %b, %H:%M:%S')}")
        description.insert(2, f"**End time:** {event.dtend.strftime('%a %d %b, %H:%M:%S')}")
    else:
        description.insert(1, f"**Due by:** {event.dtend.strftime('%a %d %b, %H:%M:%S')}")

    description = "\n".join(description)

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
