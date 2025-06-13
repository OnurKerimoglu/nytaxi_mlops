import os
 
from flask import Flask, request, jsonify
import pandas as pd
import pickle


class TaxiDurationPredictor():

    def __init__(
            self,
            modeldir):
        
        model_fpath = os.path.join(modeldir,'model.bin')
        with open(model_fpath, 'rb') as f_in:
            dv, model = pickle.load(f_in)

        self.dv = dv
        self.model = model
        self.categorical = ['PULocationID', 'DOLocationID']

    def read_data(self, filename):
        df = pd.read_parquet(filename)

        df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
        df['duration'] = df.duration.dt.total_seconds() / 60

        df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

        df[self.categorical] = df[self.categorical].fillna(-1).astype('int').astype('str')
        
        return df

    def store_output(self, y_pred, year, month):
        df_result = pd.DataFrame({'duration': y_pred})
        df_result['ride_id'] = f'{year:04d}/{month:02d}_' + df_result.index.astype('str')
        df_result.to_parquet(
            'predictions_{}-{:02d}.parquet'.format(year, month),
            engine='pyarrow',
            compression=None,
            index=False
        )

    def run4yearmonth(self, year, month):
        url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
        print(f'reading from cloud: {url}')
        df = self.read_data(url)

        dicts = df[self.categorical].to_dict(orient='records')
        X_val = self.dv.transform(dicts)
        y_pred = self.model.predict(X_val)

        print(f'predicted mean duration: {y_pred.mean()}')

        self.store_output(y_pred, year, month)

    def run4ride(self, ride_dict):
        """
        Args:
            ride_dict = {'PULocationID': int, 'DOLocationID': int}
        """
        # df = pd.DataFrame(ride, index=0)

        # dicts = df[self.categorical].to_dict(orient='records')
        print(f'Estimating trip duration for Pickup location: {ride_dict["PULocationID"]}, Dropoff location: {ride_dict["DOLocationID"]}')
        dicts= ride_dict
        X_val = self.dv.transform(dicts)
        y_pred = self.model.predict(X_val)
        print(f'Estimated duration: {y_pred[0]:.2f} minutes')
        return y_pred[0]


app = Flask('duration-prediction')
@app.route('/predict', methods=['POST'])
def predict4ride_endpoint():
    ride_dict = request.get_json()
    print(f'Estimating trip duration for Pickup location: {ride_dict["PULocationID"]}, Dropoff location: {ride_dict["DOLocationID"]}')
    
    predictor = TaxiDurationPredictor('./')
    X_val = predictor.dv.transform(ride_dict)
    y_pred = predictor.model.predict(X_val)
    print(f'Estimated duration: {y_pred[0]:.2f} minutes')
    result = {
        'duration': y_pred[0]
    }
    return jsonify(result)



if __name__ == '__main__':
    predictor = TaxiDurationPredictor('./')
    # predictor.run4yearmonth(2023, 4)
    # predictor.run4ride(ride={'PULocationID': 10, 'DOLocationID': 50})
    app.run(debug=True, host='0.0.0.0', port=9696)