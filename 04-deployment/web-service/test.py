import requests

from model_prediction import TaxiDurationPredictor

ride = {
    'PULocationID': 10,
    'DOLocationID': 50
    }

# predictor = TaxiDurationPredictor('./')
# predictor.run4yearmonth(2023, 4)
# predictor.run4ride(ride)

url = 'http://127.0.0.1:9696/predict'
response = requests.post(url, json=ride)
print(response.json())
