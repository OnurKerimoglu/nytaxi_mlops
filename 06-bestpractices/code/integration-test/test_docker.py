from deepdiff import DeepDiff
import json
import requests

event = {
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49664609009639282080112586150820704880860048089430360066",
                "data": "ewogICAgICAgICJyaWRlIjogewogICAgICAgICAgICAiUFVMb2NhdGlvbklEIjogMTMwLAogICAgICAgICAgICAiRE9Mb2NhdGlvbklEIjogMjA1LAogICAgICAgICAgICAidHJpcF9kaXN0YW5jZSI6IDMuNjYKICAgICAgICB9LCAKICAgICAgICAicmlkZV9pZCI6IDE1NgogICAgfQ==",
                "approximateArrivalTimestamp": 1750929926.306
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49664609009639282080112586150820704880860048089430360066",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::046455880223:role/lambda-kinesis-role",
            "awsRegion": "eu-central-1",
            "eventSourceARN": "arn:aws:kinesis:eu-central-1:046455880223:stream/ride_events"
        }
    ]
}

url = "http://localhost:8081/2015-03-31/functions/function/invocations"
actual_response = requests.post(url, json=event).json()
print(json.dumps(actual_response, indent=2))
expected_response = {
    'prediction_events': [
        {
            'model': 'ride_duration_prediction_model',
            'version': 'Test123',
            'prediction': {
                'ride_duration': 18.17,
                'ride_id': 156
            }
        }
    ]
}
# assert expected_response == actual_response

diff = DeepDiff(expected_response, actual_response, significant_digits=2)
print(f'diff: {diff}')

assert 'type_changes' not in diff
assert 'values_changed' not in diff

