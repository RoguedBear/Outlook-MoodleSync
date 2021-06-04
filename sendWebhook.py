#  Copyright (c) 2021 RoguedBear
from icalendar import Calendar, Event
from rssPublisher import read_ics, get_events, SimpleEvent
from hashlib import md5
from random import choice
from dateutil.tz import gettz
from datetime import datetime
from discord import Color


def calculate_hash(event: SimpleEvent) -> str:
    checksum_str = event.summary + event.category + event.description
    return md5(checksum_str.encode('utf-8')).hexdigest()


def sendWebhookUpdate(event: SimpleEvent):
    embed = {
        "content": "",
        "embed": {
            "title": f"__{event.summary}__",
            "description": "A new event popped up on LMS!\nIs it a quiz? an assignment? a bird? a plane?\n¯\\_(ツ)_/¯",
            "color": Color.random().value,
            "timestamp": event.last_mod.isoformat(),
            "url": "https://lms.bennett.edu.in/my",
            "author": {
                "name": "LMS Bot",
                "url": "https://github.com/RoguedBear",
                "icon_url": "https://cdn.discordapp.com/emojis/831953662153588766.png"
            },
            "thumbnail": {
                "url": "https://lms.bennett.edu.in/theme/image.php/lambda/theme/1609510051/favicon"
            },
            "image": {
                "url": randomCuteImageLink()
            },
            "footer": {
                "text": "Bot by BouncePrime ♥ | event created ",
                "icon_url": "https://cdn.discordapp.com/attachments/794508344441700382/834801643089952768/test_1.png"
            },
            "fields": [
                {
                    "name": "__Subject__",
                    "value": f"`{event.category}`",
                    "inline": False if event.description is None else True
                },
                {
                    "name": "__Description__",
                    "value": event.description,
                    "inline": False
                },
                {
                    "name": "Starting Time",
                    "value": event.dtstart.strftime('%a %d %b, %H:%M:%S'),
                    "inline": True
                },
                {
                    "name": "End Time",
                    "value": event.dtend.strftime('%a %d %b, %H:%M:%S'),
                    "inline": True
                },
                {
                    "name": "--------",
                    "value": "> Instead of sadness, have some eyebleach <:wholesome_seal:785811088616062976>\n",
                    "inline": False
                }
            ]
        }
    }

    pass


def randomCuteImageLink():
    links = ["https://unsplash.it/380/200",
             "https://cdn.discordapp.com/emojis/816550207206195220.png?v=1",
             "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT3YM38YKc2cbnP2Qmy-DCjvomUnOf0Riu_ZwbnidE34ggA1rM&s",
             ]
    return choice(links)


def main(config: dict):
    events_list = get_events(read_ics())
    sent_events_hash = config.get("webhook", {}).get("sent_events", [])
    hashes_to_add = []
    for event in events_list:
        if calculate_hash(event) in sent_events_hash:
            sendWebhookUpdate()
    pass
