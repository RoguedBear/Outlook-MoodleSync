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
import json
import logging
from hashlib import md5
from random import choice

from discord import Color
from requests import Session
from custom_module import send_webhook_reminder_format

from rssPublisher import SimpleEvent, get_events, init_mapping, read_ics

logger1 = logging.getLogger(__name__)

ALLOW_EVERYONE = True


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
    checksum_str = event.summary + event.category + \
        event.description + event.dtstart.isoformat()
    return md5(checksum_str.encode('utf-8')).hexdigest()


def sendWebhookUpdate(event: SimpleEvent, session: Session, **kwargs) -> bool:
    # The embeds
    _ = {
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
    mentions = ""
    url = kwargs["webhook"]["url"]
    if event.category == "ECSE219L(Specialization Core - I)":
        mentions = "<@&878107435477389362>"
        # if not ALLOW_EVERYONE:
        url = kwargs["webhook"]["specialisation"]["ai"]
    elif event.category in ["ECSE237L(Specialization Core - I)", "CSET230 (DevOps-Specialization Core - II)"]:
        mentions = "<@&878107877770948698>"
        # if not ALLOW_EVERYONE:
        url = kwargs["webhook"]["specialisation"]["devops"]
    # parsing for batch names
    elif event.has_batch:
        if event.for_eb12:
            mentions = "<@&796658898953830400>"
        else:
            mentions = "<@&785031417297109022>"
    else:
        mentions = "@everyone"

    embed = {
        "username": "LMS Bot",
        "avatar_url": "https://cdn.discordapp.com/emojis/831953662153588766.png",
        "content": f"A new event on LMS popped up: `{event.funny_name}`\n{mentions}",
        "allowed_mentions": {
            "parse": ["everyone", "roles"] if ALLOW_EVERYONE else [],
        },
        "embeds": [
            {
                "title": f"__{event.funny_name}__",
                "type": "rich",
                "description": "A new event popped up on LMS!\nIs it a quiz? an assignment? a bird? a plane?\n¯\\_("
                               "ツ)_/¯",
                "color": Color.random().value,
                "timestamp": event.last_mod.isoformat(),
                "url": "https://lms.bennett.edu.in/my",
                "author": {
                    "name": "LMS Bot",
                    "url": "https://github.com/RoguedBear",
                    "icon_url": "https://cdn.discordapp.com/emojis/832110679048978472.png"
                },
                "thumbnail": {
                    "url": "https://lms.bennett.edu.in/theme/image.php/lambda/theme/1609510051/favicon"
                },
                "footer": {
                    "text": "Bot made by BouncePrime ♥ | teach' created event @ ",
                    "icon_url": "https://cdn.discordapp.com/avatars/712318895062515809/33f30b47a0d16090fe9794cbc69bb817.webp"
                },
                "fields": [
                    {
                        "name": "__Subject__",
                        "value": f"`{event.category}`" + event.human_readable_sub_name,
                        "inline": False if event.description == "" else True
                    }
                ]
            }
        ]
    }

    # Add to embed if there's a description
    if event.description:
        if (desc_len := len(event.description)) < 1024:
            embed["embeds"][0]["fields"].insert(1, {"name": "__Description__",
                                                    "value": event.description,
                                                    "inline": False
                                                    })
        elif 1024 <= desc_len < 2048:
            embed["embeds"][0]["description"] = event.description
        else:
            embed["embeds"][0]["fields"].insert(1, {"name": "__Description__",
                                                    "value": event.description[:1000] + "\n...\nRead on LMS",
                                                    "inline": False
                                                    })

    # Set the starting/end time if quiz other wise due date
    if event.isquiz:
        start_time = {
            "name": "Starting Time",
            "value": event.dtstart.strftime('%a %d %b, %H:%M:%S'),
            "inline": True
        }
        end_time = {
            "name": "End Time",
            "value": event.dtend.strftime('%a %d %b, %H:%M:%S'),
            "inline": True
        }
        embed["content"] += " **Starts <t:{:.0f}:R> & Ends at <t:{:.0f}:F>**".format(
            event.dtstart.timestamp(), event.dtend.timestamp())
        embed["embeds"][0]["fields"].append(start_time)
        embed["embeds"][0]["fields"].append(end_time)
    else:
        due_by = {
            "name": "Due By",
            "value": event.dtstart.strftime('%a %d %b, %H:%M:%S'),
            "inline": True
        }
        embed["content"] += " **Due <t:{:.0f}:R>**".format(
            event.dtstart.timestamp())
        embed["embeds"][0]["fields"].append(due_by)

    # send eyebleach pictures
    # key, media = randomCuteImageLink()
    # if key is not False:
    #     embed["embeds"][0][key] = media.genJSON()
    #     wholesome_footer = {
    #         "name": "--------",
    #         "value": "> Instead of sadness, have some eyebleach <:wholesome_seal:785811088616062976>\n"
    #                  "||PM me (<@712318895062515809>) more eyebleach doggo pictures to be added here||\n",
    #         "inline": False
    #     }
    #     embed["embeds"][0]["fields"].append(wholesome_footer)

    try:
        s = session.post(url=url, json=embed)
        s.raise_for_status()
    except Exception as e:
        logger1.exception(e)
        logger1.error(s.reason, s.text)
        logger1.error(json.dumps(embed))
        return False
    else:
        logger1.info("Webhook response sent for: %s", event.summary)
        return True


def randomCuteImageLink():
    # TODO: way to send gifs/mp4s in the embed
    links = {
        "image": [
            # big floof
            Media("https://cdn.discordapp.com/emojis/816550207206195220.png?v=1"),
            Media("https://i.redd.it/vr50ukpo3tz61.jpg"),  # chess big floof
            Media("https://i.imgur.com/SCNqBQG.jpg"),  # godray doge
            Media("https://i.redd.it/r43lhp2ubb571.jpg"),  # sleeping cat
            Media("https://i.imgur.com/tjpANwc.jpg"),  # yawning cat
            Media("https://i.redd.it/pffdsq3b0vl71.jpg")  # sunset cat
        ],
        "video": [
            Media("https://tenor.com/bCAqV.gif"),
            Media("https://tenor.com/bDiFj.gif"),
            Media("https://tenor.com/bmWK8.gif"),
            Media("https://tenor.com/boPYY.gif"),
            Media("https://thumbs.gfycat.com/UnluckySimpleAsianpiedstarling-mobile.mp4"),
            Media(
                "https://redditsave.com/d/aHR0cHM6Ly9pLnJlZGQuaXQvbWtoMXRxN3Y5ODI3MS5naWY=")
        ]}
    key = choice(["image", False])
    if key is False:
        return False, False
    else:
        return key, choice(links[key])


def send_webhooks_main(config: dict):
    logger = logging.getLogger(__name__)
    init_mapping(config, logger)
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
            if config["webhook"]["reminder_module"]["url"]:
                send_webhook_reminder_format(config, session, event)
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

    DEBUG = True
    if not DEBUG:
        send_webhooks_main(config)
    else:
        # calculate hash for each event
        events_list = get_events(read_ics())
        hashes = [calculate_hash(event) for event in events_list]
        config["webhook"]["sent-events-hash"] = hashes
        # save it
        with open("config.yaml", "w") as f:
            yaml.safe_dump(config, f)
