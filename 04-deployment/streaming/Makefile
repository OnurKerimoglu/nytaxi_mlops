.PHONY: build
build:
	docker build -t nytaxi-trip-duration-model-stream:v1 .

.PHONY: run
run:
	docker run -it --rm \
	-p 8081:8080 \
	-e PREDICTIONS_STREAM_NAME="ride_predictions" \
    -e RUN_ID="2b92eb51836e47d69d74fa9e77b2e2ca" \
    -e TEST_RUN="True" \
    -e AWS_REGION="eu-central-1" \
	-v /home/onur/.aws:/root/.aws \
	nytaxi-trip-duration-model-stream:v1