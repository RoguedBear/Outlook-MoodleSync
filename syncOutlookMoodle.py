#  Copyright (c) 2021-22 RoguedBear
#  This file is part of Moodle-Calendar-Sync.
#
#  Moodle-Calendar-Sync is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  Moodle-Calendar-Sync is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Moodle-Calendar-Sync. If not, see <https://www.gnu.org/licenses/>.
import base64
import json
import logging
# import os
import pprint
import time
from logging.handlers import TimedRotatingFileHandler

import requests
import requests.cookies
import six
import yaml

from processCalendar import process_calendar
from rssPublisher import generate_feed
from sendWebhook import send_webhooks_main


class UnableToLoginException(Exception):
    pass


def login(login_link: str, username: str, password: str) -> dict:
    """
    Logs in to moodle and gets the MoodleSession cookie value
    :param login_link: link to login
    :param username: username
    :param password: password
    :return: MoodleSession cookie value
    """
    url = login_link
    data = {'username': username,
            'password': password,
            'rememberusername': 1,
            'anchor': ''}
    logger.info("Logging into Moodle...")
    ses = requests.session()
    response = ses.post(url=url, data=data)

    if response.raise_for_status():
        logger.error(
            "unable to login to Moodle! [%s] \n[%s]", response.reason, response.text)
        raise UnableToLoginException("Unable to login to moodle")

    return dict(ses.cookies)


def save_config(config: dict):
    with open("config.yaml", "r+", encoding="utf8") as config_file:
        config2 = yaml.safe_load(config_file)
        if config2 != config:
            logger.info("Dumping new config data")
            config_file.seek(0)
            config_file.truncate()
            yaml.safe_dump(config, config_file)


def add_refresh_interval(cal: str) -> str:
    PUBLISH_LIMIT = "X-PUBLISHED-TTL:PT5M"
    lines = cal.split("\r\n")
    for index, line in enumerate(lines):
        if line == "VERSION:2.0":
            lines.insert(index + 1, PUBLISH_LIMIT)
            break
    return "\r\n".join(lines)


def sanitise_password(pwd: str) -> str:
    # Vigenere Cipher
    # def encode(key: str, string: str) -> bytes:
    #     encoded_chars = []
    #     for i in range(len(string)):
    #         key_c = key[i % len(key)]
    #         encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
    #         encoded_chars.append(encoded_c)
    #     encoded_string = ''.join(encoded_chars)
    #     encoded_string = encoded_string.encode('latin') if six.PY3 else encoded_string
    #     return base64.urlsafe_b64encode(encoded_string).rstrip(b'=')

    def decode(key: str, string: bytes) -> str:
        string = base64.urlsafe_b64decode(string + b'===')
        string = string.decode('latin') if six.PY3 else string
        encoded_chars = []
        for i in range(len(string)):
            key_c = key[i % len(key)]
            encoded_c = chr((ord(string[i]) - ord(key_c) + 256) % 256)
            encoded_chars.append(encoded_c)
        encoded_string = ''.join(encoded_chars)
        return encoded_string
    k = "super s+lty +bcd".replace(str(base64.b64decode(b"Kw==")), "a")

    return decode(k, pwd.encode())


logging.basicConfig(level=20)
logger = logging.getLogger()
rotate_logs = TimedRotatingFileHandler(
    "logs/calendar.log", backupCount=7, when='midnight')
file_log_format = logging.Formatter(
    "%(levelname)s:[%(asctime)s]:%(message)s", datefmt="%d %a, %H:%M:%S")
rotate_logs.setFormatter(file_log_format)
logger.addHandler(rotate_logs)

try:
    with open("config.yaml", "r", encoding="utf8") as config_file:
        config = yaml.safe_load(config_file)
except FileNotFoundError:
    logger.exception("config file does not exist!")
    quit(1)

# get calendar from moodle
tries = 0
# breakpoint()
while True:
    logger.info("GETting calendar...")

    cookie = requests.cookies.cookiejar_from_dict(config['cookie'])

    tries_login = 1
    while True:
        try:
            calendar = requests.get(
                url=config['calendar_link'], cookies=cookie)
            break
        except requests.exceptions.ConnectionError as e:
            tries_login += 1
            logger.warning("%s", str(e))
            logger.info("retrying in 30 seconds")
            time.sleep(30)
            if tries_login > 3:
                logger.warning("not connected to Internet, exiting...")
                quit(1)

    # Non 200 status code:
    if calendar.raise_for_status():
        logger.error(calendar.raise_for_status())

    logger.info("Calendar retrieved... Size: %d bytes", len(calendar.text))

    # Empty calendar
    if calendar.text.replace("\r\n", "\n") == config['empty_calendar']:
        logger.warning("Empty Calendar recieved!")
        logger.info("Trying to login myself...")

        try:
            if tries == 1:
                raise UnableToLoginException()
            config['cookie'] = login(
                config['login_link'], config['username'], sanitise_password(config['password']))
        except UnableToLoginException:
            # logger.warning(
            #     "Unable to automatically login, try logging in manually and then fill the cookies")
            # input("Press anything to quit...")
            # os.system("explorer .")
            # os.system("notepad config.yaml")
            # os.system(
            #     r'""C:\Program Files\Mozilla Firefox\Firefox.exe" -P "Loggins"" -new-tab lms.bennett.edu.in')
            # quit(1)
            logger.warning(
                "Unable to automatically login, or LMS is really empty")
            save_config(config)

        else:
            logger.info("MoodleSession cookie retrieved, retrying login...")
            tries += 1
            continue

    else:
        logger.info("Calendar seems good.")
        break

# Process the calendar
CALENDAR_TEXT = process_calendar(calendar.text).decode()
# check if calendar needs updating
updateGist = False
try:
    with open("calendar_.ics", "r+", newline="") as stored_calendar:
        old_calendar = stored_calendar.read()
        if len(old_calendar) != len(CALENDAR_TEXT):
            updateGist = True
            # explanation https://stackoverflow.com/a/48863075
            stored_calendar.seek(0)
            stored_calendar.truncate(0)
            stored_calendar.write(CALENDAR_TEXT)
            logger.info("Received calendar is different.")
            logger.debug("\nFile:\n" + old_calendar +
                         "\nOnline:\n" + CALENDAR_TEXT)
            logger.debug("len(old_calendar) = %d \t len(CALENDAR_TEXT) = %d",
                         len(old_calendar),
                         len(CALENDAR_TEXT))
        else:
            logger.info(
                "Calendar recieved is same. Gist does not need updating")
except FileNotFoundError:
    with open("calendar_.ics", "w") as file:
        file.write(CALENDAR_TEXT)
    updateGist = True

if updateGist:
    # update the gist to github
    logger.info("Updating github gist...")
    headers = {"Authorization": f"token {config['gist_token']}",
               }
    data = {"files": {'test.ics': {'content': CALENDAR_TEXT},
                      'rssFeed.rss': {'content': generate_feed()}
                      },
            "accept": "application/vnd.github.v3+json",
            "gist_id": config['gist_id'],
            "description": "my calendar dump from moodle"
            }

    github_response = requests.patch(f"https://api.github.com/gists/{config['gist_id']}",
                                     headers=headers,
                                     data=json.dumps(data)
                                     )
    if github_response.raise_for_status():
        logger.error(pprint.pformat(github_response.json()))
    else:
        logger.info("Github gist updated %s", github_response)
    logger.info("Sending webhooks...")
    send_webhooks_main(config)

save_config(config)
# input("Press anything to quit...")
