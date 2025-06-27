#!/usr/bin/env bash

cd "$(dirname "$0")"

LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`

export LOCAL_IMAGE_NAME=f"nytaxi-trip-duration-model-stream:${LOCAL_TAG}"
export PREDICTIONS_STREAM_NAME="ride_predictions"

docker build -t ${LOCAL_IMAGE_NAME} ..

docker compose up -d

sleep 1

# create the localstack kinesis stream
aws --endpoint-url=http://localhost:4566 \
    kinesis create-stream \
    --stream-name ${PREDICTIONS_STREAM_NAME} \
    --shard-count 1

# try to predict and push into kinesis
pipenv run python test_docker.py

ERROR_CODE=$?

if [ $ERROR_CODE -ne 0 ]; then
    docker compose logs
    docker compose down
    exit $ERROR_CODE
fi

sleep 1

# check the record in kinesis
pipenv run python test_kinesis.py

ERROR_CODE=$?

if [ $ERROR_CODE -ne 0 ]; then
    docker compose logs
    docker compose down
    exit $ERROR_CODE
fi


docker compose down
