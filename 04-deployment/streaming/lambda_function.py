import os

import base64
import boto3
import json
import mlflow

PREDICTION_STREAM_NAME = os.getenv('PREDICTIONS_STREAM_NAME', 'ride_predictions')
TEST_RUN = os.getenv('TEST_RUN', 'False') == 'True'
RUN_ID = os.getenv('RUN_ID', '2b92eb51836e47d69d74fa9e77b2e2ca')
AWS_REGION = os.getenv('AWS_REGION', 'eu-central-1')

print('got environment variables')

kinesis_client = boto3.client('kinesis', region_name=AWS_REGION)
logged_model = f's3://onur-mlflow-models/1/{RUN_ID}/artifacts/model'
# logged_model = f'runs:/{RUN_ID}/model'
model = mlflow.pyfunc.load_model(logged_model)

print('loaded model')

def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features

def predict(features):
    preds = model.predict(features)
    return float(preds[0])

def lambda_handler(event, context=None):
    
    print('lambda_handler starting')
    # print(json.dumps(event))

    prediction_events = []
    for record in event['Records']:
        encoded_data = record['kinesis']['data']
        decoded_data = base64.b64decode(encoded_data).decode('utf-8')
        ride_event = json.loads(decoded_data)
        print(f'ride event: {ride_event}')
        ride = ride_event['ride']
        ride_id = ride_event['ride_id']
        features = prepare_features(ride)
        prediction = predict(features)
        prediction_event =  {
            'model': 'ride_duration_prediction_model',
            'version': '123',
            'prediction': {
                'ride_duration': prediction,
                'ride_id': ride_id
                }
            }
        if not TEST_RUN:
            print('prod run, sending the prediction to kinesis')
            response = kinesis_client.put_record(
                StreamName=PREDICTION_STREAM_NAME,
                Data=json.dumps(prediction_event),
                PartitionKey=str(ride_id)
            )
            print(f'kinesis {PREDICTION_STREAM_NAME} put_record response:\n{response}')
        else:
            print('test run, not sending the prediction to kinesis')
        
        prediction_events.append(prediction_event)
    
    return {'prediction_events': prediction_events}
