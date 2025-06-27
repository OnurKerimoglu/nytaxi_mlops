from datetime import datetime
import json
import pandas as pd

import batch

def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)

def test_prepare_data():
    data = [
        (None, None, dt(1, 1), dt(1, 10)),
        (1, 1, dt(1, 2), dt(1, 10)),
        (1, None, dt(1, 2, 0), dt(1, 2, 59)),
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),      
    ]

    columns_raw = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    df_raw = pd.DataFrame(data, columns=columns_raw)

    print(f'df_raw:\n{df_raw}')

    categorical = ['PULocationID', 'DOLocationID']
    df_actual = batch.prepare_data(df_raw, categorical)
    dict_actual = df_actual.to_dict(orient='records')
    print(f'dict_actual:\n{dict_actual}')

    columns_prep = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime', 'duration']
    df_expected = pd.DataFrame([
        ('-1', '-1', dt(1, 1), dt(1, 10), 9.0),
        ('1', '1', dt(1, 2), dt(1, 10), 8.0)
    ], columns=columns_prep)
    dict_expected = df_expected.to_dict(orient='records')
    print(f'dict_expected:\n{dict_expected}')

    assert dict_actual == dict_expected

if __name__ == "__main__":
    test_prepare_data()