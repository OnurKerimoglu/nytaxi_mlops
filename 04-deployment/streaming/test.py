
import lambda_function

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


result = lambda_function.lambda_handler(event, None)
print(result)
