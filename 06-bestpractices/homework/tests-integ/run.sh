#!/usr/bin/env bash

cd "$(dirname "$0")"

# LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`
LOCAL_TAG="latest"

export LOCAL_IMAGE_NAME=f"nytaxi-trip-duration-model-batch:${LOCAL_TAG}"
export BUCKET_NAME="nyc-duration"
export INPUT_FILE_PATTERN="s3://${BUCKET_NAME}/in/{year:04d}-{month:02d}.parquet"
export OUTPUT_FILE_PATTERN="s3://${BUCKET_NAME}/out/{year:04d}-{month:02d}.parquet"

echo "INPUT_FILE_PATTERN: ${INPUT_FILE_PATTERN}..."

docker build -t ${LOCAL_IMAGE_NAME} ..

docker compose up -d

sleep 1

# create the localstack kinesis stream
aws --endpoint-url=http://localhost:4566 \
    s3 \
    mb s3://${BUCKET_NAME}

# # try to predict and push into kinesis
pipenv run python integration_test.py

ERROR_CODE=$?

if [ $ERROR_CODE -ne 0 ]; then
    docker compose logs
    docker compose down
    exit $ERROR_CODE
fi

echo "Input Files in localstack s3:"
aws --endpoint-url=http://localhost:4566 s3 ls s3://nyc-duration/in/
echo "Output Files in localstack s3:"
aws --endpoint-url=http://localhost:4566 s3 ls s3://nyc-duration/out/

docker compose down
