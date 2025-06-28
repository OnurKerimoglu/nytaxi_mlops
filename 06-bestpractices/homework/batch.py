#!/usr/bin/env python
# coding: utf-8

import os
import sys
import pickle
import pandas as pd


def get_input_path(year, month):
    default_input_pattern = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    input_pattern = os.getenv('INPUT_FILE_PATTERN', default_input_pattern)
    return input_pattern.format(year=year, month=month)


def get_output_path(year, month):
    default_output_pattern = 's3://nyc-duration-prediction-alexey/taxi_type=fhv/year={year:04d}/month={month:02d}/predictions.parquet'
    output_pattern = os.getenv('OUTPUT_FILE_PATTERN', default_output_pattern)
    return output_pattern.format(year=year, month=month)

def prepare_data(df, categorical):
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    return df

def read_data(filename, categorical):
    s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')
    if s3_endpoint_url:
        options = {'client_kwargs': {'endpoint_url': s3_endpoint_url}}
        df = pd.read_parquet(filename, storage_options=options)
    else:
        df = pd.read_parquet(filename)
    return df

def save_data(df, output_file):
    s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')
    if s3_endpoint_url:
        print(f'saving data to: {output_file} at endpoint: {s3_endpoint_url}')
        options = {'client_kwargs': {'endpoint_url': s3_endpoint_url}}
        df.to_parquet(
            output_file,
            engine='pyarrow',
            compression=None,
            index=False,
            storage_options=options
        )
        sum_durations = df.predicted_duration.sum()
        print(f'sum of predicted durations: {sum_durations}')
    else:
        print(f'saving data to: {output_file}')
        df = df.to_parquet(
            output_file,
            engine='pyarrow',
            index=False)
    return df

def main(year, month):

    # input_file = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    # output_file = f'output/yellow_tripdata_{year:04d}-{month:02d}.parquet'

    input_file = get_input_path(year, month)
    output_file = get_output_path(year, month)

    print(f'reading input from: {input_file}')
    categorical = ['PULocationID', 'DOLocationID']
    df_raw = read_data(input_file, categorical)
    df = prepare_data(df_raw, categorical)
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

    print('predicting..')
    with open('model.bin', 'rb') as f_in:
        dv, lr = pickle.load(f_in)
    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)
    print('predicted mean duration:', y_pred.mean())

    print(f'writing results to: {output_file}')
    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred
    save_data(df_result, output_file)


if __name__ == '__main__':
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    main(year, month)
