import pandas as pd
import pickle
import sys

from flask import Flask, request, jsonify

CATEGORICAL = ['PULocationID', 'DOLocationID']
with open('model.bin', 'rb') as f_in:
    (dv, model) = pickle.load(f_in)


def read_data(filename):
    df = pd.read_parquet(filename)

    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[CATEGORICAL] = df[CATEGORICAL].fillna(-1).astype('int').astype('str')
    
    return df

def store_output(y_pred, year, month):
    df_result = pd.DataFrame({'duration': y_pred})
    df_result['ride_id'] = f'{year:04d}/{month:02d}_' + df_result.index.astype('str')
    df_result.to_parquet(
        'predictions_{}-{:02d}.parquet'.format(year, month),
        engine='pyarrow',
        compression=None,
        index=False
    )

def prepare_ride_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features


def predict_ride(features):
    X = dv.transform(features)
    preds = model.predict(X)
    return float(preds[0])


app = Flask('duration-prediction')

# @app.route('/predict_yearmonth', methods=['POST'])
def predict_yearmonth(year, month):
    # yearmonth = request.get_json()
    # year = yearmonth['year']
    # month = yearmonth['month']
    
    print(f'reading from cloud: {year:04d}-{month:02d}')
    url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    print(f'reading from cloud: {url}')
    df = read_data(url)

    dicts = df[CATEGORICAL].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = model.predict(X_val)

    pred_mean = y_pred.mean()
    print(f'predicted mean duration: {pred_mean}')

    # store_output(y_pred, year, month)

    # result = {
    #     'duration': pred_mean
    # }
    # return jsonify(result)

@app.route('/predict_ride', methods=['POST'])
def predict_ride_endpoint():
    ride = request.get_json()

    features = prepare_ride_features(ride)
    pred = predict_ride(features)

    result = {
        'duration': pred
    }

    return jsonify(result)


if __name__ == "__main__":
    # app.run(debug=True, host='0.0.0.0', port=9696)
    year = int(sys.argv[1]) # 2023
    month = int(sys.argv[2]) # 4
    predict_yearmonth(year, month)