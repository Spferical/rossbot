From python:3-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY *.py *.sh requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY crontab /var/spool/cron/crontabs/root

RUN touch /var/log/cron.log

ENV ROSSBOT_DATA_DIR /var/rossbot

VOLUME /var/rossbot/

CMD env | sed 's/^\(.*\)$/export \1/g' > /root/.profile && tail -f /var/log/cron.log & crond -l 2 -f
