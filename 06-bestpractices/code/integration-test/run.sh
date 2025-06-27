#!/usr/bin/env bash

cd "$(dirname "$0")"

LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`

export LOCAL_IMAGE_NAME=f"nytaxi-trip-duration-model-stream:${LOCAL_TAG}"
echo $LOCAL_IMAGE_NAME

docker build -t ${LOCAL_IMAGE_NAME} ..

docker compose up -d

sleep 1

pipenv run python test_docker.py

ERROR_CODE=$?

if [ $ERROR_CODE -ne 0 ]; then
    docker compose logs
fi

docker compose down

exit $ERROR_CODE