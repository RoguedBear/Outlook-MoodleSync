#!/bin/sh
# Import your cron file
/usr/bin/crontab /scripts/crontab.txt
# Start cron
/usr/sbin/crond -f -L /dev/stdout