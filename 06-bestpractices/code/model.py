import os

import base64
import boto3
import json
import mlflow


def get_model_location(run_id):
    model_location = os.getenv('MODEL_LOCATION')
    if model_location:
        return model_location
    model_bucket = os.getenv('MODEL_BUCKET', 'onur-mlflow-models')
    experiment_id = os.getenv('EXPERIMENT_ID', '1')
    model_location = f's3://{model_bucket}/{experiment_id}/{run_id}/artifacts/model'
    return model_location

def load_model(run_id):
    model_path = get_model_location(run_id)
    model = mlflow.pyfunc.load_model(model_path)
    print('loaded model')
    return model

def base64_decode(encoded_data):
    decoded_data = base64.b64decode(encoded_data).decode('utf-8')
    ride_event = json.loads(decoded_data)
    return ride_event

class ModelService():

    def __init__(self, model, model_version=None, callbacks=None):
        self.model = model
        self.model_version = model_version
        if callbacks is None:
            self.callbacks = []
        else:
            self.callbacks = callbacks

    def prepare_features(self, ride):
        features = {}
        features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
        features['trip_distance'] = ride['trip_distance']
        return features

    def predict(self, features):
        preds = self.model.predict(features)
        return float(preds[0])

    def lambda_handler(self, event):
        print('lambda_handler starting')
        # print(json.dumps(event))

        prediction_events = []
        for record in event['Records']:
            encoded_data = record['kinesis']['data']
            ride_event = base64_decode(encoded_data)
            print(f'ride event: {ride_event}')
            ride = ride_event['ride']
            ride_id = ride_event['ride_id']
            features = self.prepare_features(ride)
            prediction = self.predict(features)
            prediction_event =  {
                'model': 'ride_duration_prediction_model',
                'version': self.model_version,
                'prediction': {
                    'ride_duration': prediction,
                    'ride_id': ride_id
                    }
                }
            
            for callback in self.callbacks:
                callback(prediction_event)
            
            prediction_events.append(prediction_event)
        
        return {'prediction_events': prediction_events}


class KinesisCallback:
    def __init__(self, kinesis_client, prediction_stream_name):
        self.kinesis_client = kinesis_client
        self.prediction_stream_name = prediction_stream_name

    def put_record(self, prediction_event):
        print('Sending the prediction to kinesis')
        ride_id = prediction_event['prediction']['ride_id']
        self.kinesis_client.put_record(
            StreamName=self.prediction_stream_name,
            Data=json.dumps(prediction_event),
            PartitionKey=str(ride_id)
        )
        print(f'Kinesis {self.prediction_stream_name} put_record done')

def create_kinesis_client(aws_region):
    kinesis_endpoint_url = os.getenv('KINESIS_ENDPOINT_URL')
    if kinesis_endpoint_url is None:
        # get it from aws
        kinesis_client = boto3.client('kinesis', region_name=aws_region)
    else:
        # if set, probably it's a localstack kinesis mock
        kinesis_client = boto3.client('kinesis', endpoint_url=kinesis_endpoint_url)

    return kinesis_client

def init(prediction_stream_name:str, run_id:str, aws_region:str, test_run:bool):
    model = load_model(run_id)
    callbacks = []
    if not test_run:
        kinesis_client = create_kinesis_client(aws_region)
        kinesis_callback = KinesisCallback(kinesis_client, prediction_stream_name)
        callbacks.append(kinesis_callback.put_record)
    model_service = ModelService(
        model,
        model_version=run_id,
        callbacks=callbacks)
    return model_service
