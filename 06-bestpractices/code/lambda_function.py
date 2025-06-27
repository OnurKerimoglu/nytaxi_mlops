import os
import model


PREDICTION_STREAM_NAME = os.getenv('PREDICTIONS_STREAM_NAME', 'ride_predictions')
TEST_RUN = os.getenv('TEST_RUN', 'False') == 'True'
RUN_ID = os.getenv('RUN_ID', '2b92eb51836e47d69d74fa9e77b2e2ca')
AWS_REGION = os.getenv('AWS_REGION', 'eu-central-1')

print('got environment variables')

model_service = model.init(
    prediction_stream_name=PREDICTION_STREAM_NAME,
    run_id=RUN_ID,
    aws_region=AWS_REGION,
    test_run=TEST_RUN)

def lambda_handler(event, context=None):
    return model_service.lambda_handler(event)