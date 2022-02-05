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
from requests import Session
from rssPublisher import SimpleEvent


embed_boilerplate = {
    "username": "LMS Bot",
    "avatar_url": "https://cdn.discordapp.com/emojis/831953662153588766.png",
}

logger1 = logging.getLogger(__name__)


def send_webhook_reminder_format(config: dict, session: Session, event: SimpleEvent):
    """
    sends webhook message in the format of:
    <subject name> - <assignment name> - due <time format>
    """
    if event.has_batch and not event.for_eb12:
        return

    subject_name = event.human_readable_sub_name.strip(" |`")
    if subject_name == "":
        subject_name = event.category
    time = f"<t:{event.dtstart.timestamp():.0f}:R>"
    content = f"{subject_name} - {event.summary}"

    if event.isquiz:
        content = "⚠⚠ QUIZ: " + content + f" - starts {time}"
    else:
        content += f" - due {time}"

    content += f"   || \\{time} ||"

    embed_boilerplate["content"] = content

    try:
        s = session.post(url=config["webhook"]["reminder_module"]["url"],
                         json=embed_boilerplate)
        s.raise_for_status()
    except Exception as e:
        logger1.exception(e)
        logger1.error(s.reason, s.text)
        logger1.error(json.dumps(embed_boilerplate))
        return False
    else:
        logger1.info("Webhook response sent for: %s", event.summary)
        return True


if __name__ == "__main__":
    import yaml
    from rssPublisher import get_events, read_ics, init_mapping

    logging.basicConfig(level=10)
    logger1 = logging.getLogger(__name__)

    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    session = Session()
    events_list = get_events(read_ics())
    init_mapping(config, logger1)

    send_webhook_reminder_format(config, session, events_list[0])
    send_webhook_reminder_format(config, session, events_list[5])
    send_webhook_reminder_format(config, session, events_list[-1])
