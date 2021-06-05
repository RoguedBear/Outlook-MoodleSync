#  Copyright (c) 2021 RoguedBear
import json
import logging

from rssPublisher import read_ics, get_events, SimpleEvent
from hashlib import md5
from random import choice
from discord import Color
from requests import Session

logger1 = logging.getLogger(__name__)


class Media:
    def __init__(self, url: str, height: int = 256, width: int = 256):
        self.url = url
        self.height = height
        self.width = width

    def genJSON(self):
        return {
            "url": self.url,
            # "width": self.width,
            # "height": self.height
        }


def calculate_hash(event: SimpleEvent) -> str:
    checksum_str = event.summary + event.category + event.description
    return md5(checksum_str.encode('utf-8')).hexdigest()


def sendWebhookUpdate(event: SimpleEvent, session: Session, **kwargs) -> bool:
    # The embeds
    embed_old = {
        "content": "testing webhook; test #2",
        "embeds": {
            "title": f"__{event.summary}__",
            "type": "rich",
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
                "text": "Bot by BouncePrime ♥ | teach' created event @ ",
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
                    "value": "> Instead of sadness, have some eyebleach <:wholesome_seal:785811088616062976>\n"
                             "||PM me (<@712318895062515809>) more eyebleach doggo pictures to be added here||\n",
                    "inline": False
                }
            ]
        }
    }
    embed = {
        "username": "LMS Bot",
        "avatar_url": "https://cdn.discordapp.com/emojis/831953662153588766.png",
        "content": f"A new event on LMS popped up: `{event.summary}`\n@everyone",
        "allowed_mentions": {
            "parse": ["everyone"],
        },
        "embeds": [
            {
                "title": f"__{event.summary}__",
                "type": "rich",
                "description": "A new event popped up on LMS!\nIs it a quiz? an assignment? a bird? a plane?\n¯\\_("
                               "ツ)_/¯",
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
                "footer": {
                    "text": "Bot by BouncePrime ♥ | teach' created event @ ",
                    "icon_url": "https://cdn.discordapp.com/attachments/794508344441700382/834801643089952768/test_1"
                                ".png "
                },
                "fields": [
                    {
                        "name": "__Subject__",
                        "value": f"`{event.category}`",
                        "inline": False if event.description == "" else True
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
                        "value": "> Instead of sadness, have some eyebleach <:wholesome_seal:785811088616062976>\n"
                                 "||PM me (<@712318895062515809>) more eyebleach doggo pictures to be added here||\n",
                        "inline": False
                    }
                ]
            }
        ]
    }

    # Add to embed if there's a description
    if event.description:
        embed["embeds"][0]["fields"].insert(1, {"name": "__Description__",
                                                "value": event.description,
                                                "inline": False
                                                })
    # send eyebleach pictures
    key, media = randomCuteImageLink()
    if key is not False:
        embed["embeds"][0][key] = media.genJSON()

    try:
        s = session.post(url=kwargs["webhook"]["url"], json=embed)
        s.raise_for_status()
    except Exception as e:
        logger1.exception(e)
        logger1.error(s.reason, s.text)
        return False
    else:
        logger1.info("Webhook response sent for: %s", event.summary)
        return True


def randomCuteImageLink():
    links = {
        "image": [
            Media("https://cdn.discordapp.com/emojis/816550207206195220.png?v=1"),
            Media("https://i.redd.it/vr50ukpo3tz61.jpg"),
            Media("https://i.redd.it/xd7z2tui9gy61.png"),
            Media("https://i.imgur.com/SCNqBQG.jpg"),
            Media("https://i.redd.it/3847pw673u751.jpg")
        ],
        "video": [
            Media("https://tenor.com/bCAqV.gif"),
            Media("https://tenor.com/bDiFj.gif"),
            Media("https://tenor.com/bmWK8.gif"),
            Media("https://tenor.com/boPYY.gif"),
            Media("https://thumbs.gfycat.com/UnluckySimpleAsianpiedstarling-mobile.mp4"),
            Media("https://redditsave.com/d/aHR0cHM6Ly9pLnJlZGQuaXQvbWtoMXRxN3Y5ODI3MS5naWY=")
        ]}
    key = choice(["image", False])
    if key is False:
        return False, False
    else:
        return key, choice(links[key])


def send_webhooks_main(config: dict):
    logger = logging.getLogger(__name__)
    events_list = get_events(read_ics())
    sent_events_hash = config.get("webhook", {}).get("sent-events-hash", [])
    hashes_to_add = []

    session = Session()
    count = 0
    for event in events_list:
        cur_hash = calculate_hash(event)
        if cur_hash not in sent_events_hash:
            sent = sendWebhookUpdate(event, session, **config)
            if sent:
                hashes_to_add.append(cur_hash)
                count += 1
        else:
            hashes_to_add.append(cur_hash)
    logger.info("Sent %d webhooks", count)
    config["webhook"]["sent-events-hash"] = hashes_to_add
    pass


if __name__ == '__main__':
    import yaml

    logging.basicConfig(level=10)
    logger1 = logging.getLogger(__name__)
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    send_webhooks_main(config)
    # with open("config.yaml", "w") as f:
    #     yaml.safe_dump(config, f)
