import json
import logging
# import os
import pprint
import time
from logging.handlers import TimedRotatingFileHandler

import requests
import requests.cookies
import yaml

from rssPublisher import generate_feed


class UnableToLoginException(Exception):
    pass


def login(login_link: str, username: str, password: str) -> dict:
    """
    Logs in to moodle and gets the MoodleSession cookie value
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
    with open("config.yaml", "r+") as config_file:
        config2 = yaml.safe_load(config_file)
        if config2 != config:
            logger.info("Dumping new config data")
            config_file.seek(0)
            yaml.safe_dump(config, config_file)


def add_refresh_interval(cal: str) -> str:
    PUBLISH_LIMIT = "X-PUBLISHED-TTL:PT5M"
    lines = cal.split("\r\n")
    for index, line in enumerate(lines):
        if line == "VERSION:2.0":
            lines.insert(index + 1, PUBLISH_LIMIT)
            break
    return "\r\n".join(lines)


logging.basicConfig(level=20)
logger = logging.getLogger()
rotate_logs = TimedRotatingFileHandler(
    "logs/calendar.log", backupCount=7, when='midnight')
file_log_format = logging.Formatter(
    "%(levelname)s:[%(asctime)s]:%(message)s", datefmt="%d %a, %H:%M:%S")
rotate_logs.setFormatter(file_log_format)
logger.addHandler(rotate_logs)

try:
    with open("config.yaml", "r") as config_file:
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
                config['login_link'], config['username'], config['password'])
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

# check if calendar needs updating
updateGist = False
try:
    with open("calendar_.ics", "r+", newline="") as stored_calendar:
        old_calendar = stored_calendar.read()
        if len(old_calendar) != len(calendar.text):
            updateGist = True
            stored_calendar.truncate(0)
            stored_calendar.write(calendar.text)
            logger.info("Received calendar is different.")
            logger.debug("\nFile:\n" + old_calendar +
                         "\nOnline:\n" + calendar.text)
            logger.debug("len(old_calendar) = %d \t len(calendar.text) = %d",
                         len(old_calendar),
                         len(calendar.text))
        else:
            logger.info(
                "Calendar recieved is same. Gist does not need updating")
except FileNotFoundError:
    with open("calendar_.ics", "w") as file:
        file.write(calendar.text)
    updateGist = True

if updateGist:
    # update the gist to github
    logger.info("Updating github gist...")
    headers = {"Authorization": f"token {config['gist_token']}",
               }
    data = {"files": {'test.ics': {'content': add_refresh_interval(calendar.text)},
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

save_config(config)
# input("Press anything to quit...")
