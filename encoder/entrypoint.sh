#!/bin/sh

apk add curl
while ! nc -z rabbitmq 5672; do sleep 5; done
python /app/consumer.py