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

from typing import List, Union

from icalendar import Calendar, Event, vText

"""
What to do?
    - Add the required components first
    - then process through the events
    - get the type of the event (is_quiz)
    - make a function to "match events" based on name and category aka find open/close pairs if event is quiz
"""


def pre_process_calendar(cal: Calendar):
    headers = {
        "METHOD": "PUBLISH",
        "PRODID": "-//John Papaioannou/NONSGML Bennu 0.1//EN",
        "VERSION": "2.0",
        "X-PUBLISHED-TTL": "PT5M",
    }
    for key in headers.keys():
        cal.add(key, headers[key])
    pass


def is_quiz(event: Event) -> int:
    """0 -> not a quiz; 1-> quiz start; 2-> quiz ends"""
    if (summary := event.get("summary")).endswith("(Quiz opens)"):
        return 1
    elif summary.endswith("(Quiz closes)"):
        return 2
    else:
        return 0


def find_match(events: List[Event], match: Event) -> Union[Event, bool]:
    """
    from a given list of quizzes, find its match and return that
    :param events: list of Event s
    :param match: the event to match against
    :return: Event if match is found, else False
    """
    for index, event in enumerate(events):
        summary: vText = event.get("summary")
        category = event.get("categories")
        if summary.removesuffix("(Quiz opens)") == match.get("summary").removesuffix("(Quiz closes)") \
                and category.to_ical() == match.get("categories").to_ical():
            return events.pop(index)
    return False


def process_calendar(calendar: str) -> bytes:  # str
    # convert received cal to Calendar object
    cal: Calendar = Calendar.from_ical(calendar)
    # make new cal
    new_cal = Calendar()
    pre_process_calendar(new_cal)

    quizzes_found = []
    # iterate through the events
    event: Event
    for event in cal.subcomponents:
        # if event is quiz then do stuff
        if q_type := is_quiz(event):
            # if quiz starts
            # add the event to the list and then continue
            if q_type == 1:
                quizzes_found.append(event)
                continue

            # if quiz ends
            # find its match from quizzes_found then add the event to the calendar
            if q_type == 2:
                merged_event = find_match(quizzes_found, event)
                if isinstance(merged_event, bool) and merged_event is False:
                    continue
                merged_event['dtend'] = event.get('dtstart')
                merged_event['summary'] = merged_event.get('summary').removesuffix(" (Quiz opens)")
                new_cal.add_component(merged_event)

        # if event is not a quiz, simply add it to the new calendar
        else:
            new_cal.add_component(event)
    return new_cal.to_ical()


if __name__ == '__main__':
    with open("calendar_.ics") as f:
        cal = f.read()
    x = process_calendar(cal)
    y = x.decode()
    # breakpoint()
    with open("calendar_.ics", "wb") as f:
        f.write(x)
