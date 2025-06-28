import os

from datetime import datetime
import pandas as pd


def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)

def create_input_file():
    print ('creating input file')
    
    s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')
    if not s3_endpoint_url:
        raise Exception('S3_ENDPOINT_URL is not set')
    input_pattern = os.getenv('INPUT_FILE_PATTERN')
    if not input_pattern:
        raise Exception('INPUT_FILE_PATTERN is not set')
    
    data = [
            (None, None, dt(1, 1), dt(1, 10)),
            (1, 1, dt(1, 2), dt(1, 10)),
            (1, None, dt(1, 2, 0), dt(1, 2, 59)),
            (3, 4, dt(1, 2, 0), dt(2, 2, 1)),      
        ]

    columns_raw = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    df_input = pd.DataFrame(data, columns=columns_raw)
    
    year = 2023
    month = 1
    input_file = input_pattern.format(year=year, month=month)
    options = {'client_kwargs': {'endpoint_url': s3_endpoint_url}}
    df_input.to_parquet(
        input_file,
        engine='pyarrow',
        compression=None,
        index=False,
        storage_options=options
    )

def run_batch():
    print ('running batch')
    os.system('cd .. && python batch.py 2023 1')

def main():
    create_input_file()
    run_batch()


if __name__ == '__main__':
    main()