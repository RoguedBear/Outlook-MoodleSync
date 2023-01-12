FROM python:3-alpine

# Install tzdata
RUN apk upgrade --no-cache \
    && apk add --no-cache tzdata \
    && rm -rf /var/cache/apk/*

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app
RUN mv docker-scripts /scripts

VOLUME [ "/app" ]

CMD [ "/scripts/container-entrypoint.sh" ]
