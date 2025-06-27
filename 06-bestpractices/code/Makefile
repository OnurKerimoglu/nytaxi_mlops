PWD = $(shell pwd)

.PHONY: build
build:
	docker build -t nytaxi-trip-duration-model-stream:v2 .

.PHONY: run
run:
	docker run -it --rm \
	-p 8081:8080 \
	-e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e RUN_ID="2b92eb51836e47d69d74fa9e77b2e2ca" \
    -e TEST_RUN="True" \
    -e AWS_REGION="eu-central-1" \
	-v /home/onur/.aws:/root/.aws \
	nytaxi-trip-duration-model-stream:v2

.PHONY: run_local
run_local:
	docker run -it --rm \
	-p 8081:8080 \
	-e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e RUN_ID="Test123" \
    -e TEST_RUN="True" \
    -e AWS_REGION="eu-central-1" \
	-e MODEL_LOCATION="/app/model" \
	-v /home/onur/.aws:/root/.aws \
	-v ${PWD}/integration-test/model:/app/model \
	nytaxi-trip-duration-model-stream:v2