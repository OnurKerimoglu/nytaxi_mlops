import model

def test_prepare_features():
    model_service = model.ModelService(None)
    ride =  {
        "PULocationID": 130,
        "DOLocationID": 205,
        "trip_distance": 3.66
    }
    actual_features = model_service.prepare_features(ride)
    expected_features = {
        "PU_DO": "130_205",
        "trip_distance": 3.66
    }
    assert actual_features == expected_features

def test_base64_decode():
    base64_input = "ewogICAgICAgICJyaWRlIjogewogICAgICAgICAgICAiUFVMb2NhdGlvbklEIjogMTMwLAogICAgICAgICAgICAiRE9Mb2NhdGlvbklEIjogMjA1LAogICAgICAgICAgICAidHJpcF9kaXN0YW5jZSI6IDMuNjYKICAgICAgICB9LCAKICAgICAgICAicmlkZV9pZCI6IDE1NgogICAgfQ=="
    actual_result = model.base64_decode(base64_input)
    expected_result = {
        "ride": {
            "PULocationID": 130,
            "DOLocationID": 205,
            "trip_distance": 3.66
        }, 
        "ride_id": 156
    }
    assert actual_result == expected_result


class ModelMock:
    def __init__(self, value, model_version=None):
        self.value = value
        self.model_version = model_version

    def predict(self, features):
        n = len(features)
        return [self.value] * n

def test_predict():
    model_mock = ModelMock(10)
    model_service = model.ModelService(model_mock)
    ride =  {
        "PULocationID": 130,
        "DOLocationID": 205,
        "trip_distance": 3.66
    }
    features = model_service.prepare_features(ride)
    actual_prediction = model_service.predict(features)
    expected_prediction = 10.0

    assert actual_prediction == expected_prediction


def test_lambda_handler():
    model_mock = ModelMock(10)
    model_version = 'test1'
    model_service = model.ModelService(model_mock, model_version)
    event = {
        "Records": [
            {
                "kinesis": {
                    "data": "ewogICAgICAgICJyaWRlIjogewogICAgICAgICAgICAiUFVMb2NhdGlvbklEIjogMTMwLAogICAgICAgICAgICAiRE9Mb2NhdGlvbklEIjogMjA1LAogICAgICAgICAgICAidHJpcF9kaXN0YW5jZSI6IDMuNjYKICAgICAgICB9LCAKICAgICAgICAicmlkZV9pZCI6IDE1NgogICAgfQ==",
                }
            }
        ]
    }
    actual_predictions = model_service.lambda_handler(event)
    expected_predictions = {
        'prediction_events': [
            {
                'model': 'ride_duration_prediction_model',
                'version': model_version,
                'prediction': {
                    'ride_duration': 10.0,
                    'ride_id': 156
                    }
                }
        ]
    }
    assert actual_predictions == expected_predictions


    
