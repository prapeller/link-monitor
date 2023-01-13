#!/bin/bash

set -o errexit
set -o nounset

worker_ready(){
   celery -A celery_app inspect ping
}

until worker_ready; do
   >&2 echo "Celery workers are not available :-("
   sleep 1
done
>&2 echo "Celery workers are available and ready!....:-)"

celery -A celery_app --broker="${CELERY_BROKER_URL}" flower --basic_auth="${CELERY_FLOWER_USER}:${CELERY_FLOWER_PASSWORD}"