.PHONY: build
build:
	docker build -t nytaxi-ride-duration-prediction:v1 .

.PHONY: run
run:
	docker run -it --rm -p 9696:9696 nytaxi-ride-duration-prediction:v1