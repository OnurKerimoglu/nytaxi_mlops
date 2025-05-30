#!/usr/bin/env python
# coding: utf-8

import os
import pickle
from pathlib import Path

import mlflow
import numpy as np
import pandas as pd
from prefect import flow, task
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import root_mean_squared_error

# mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("nyc-taxi-experiment")

models_folder = Path("models")
models_folder.mkdir(exist_ok=True)


@task(retries=2, retry_delay_seconds=1, log_prints=True)
def read_dataframe(
    color: str,
    year: int,
    month: int,
    read_local: bool = False,
):
    filename = f"{color}_tripdata_{year}-{month:02d}.parquet"

    if read_local:
        data_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'data_raw')
        url = os.path.join(data_path, filename)
        print(f"reading local: {url}")
    else:
        url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{filename}"
        print(f"reading from cloud: {url}")
    df = pd.read_parquet(url)

    if color == "green":
        df["duration"] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    elif color == "yellow":
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df["duration"] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df.duration = df.duration.apply(lambda td: td.total_seconds() / 60)

    df = df[(df.duration >= 1) & (df.duration <= 60)]

    return df

def get_features(df):

    # df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']
    # categorical = ['PU_DO']
    categorical = ["PULocationID", "DOLocationID"]
    df[categorical] = df[categorical].astype(str)
    print(f'Using categorical features: {categorical}')
    
    # numerical = ["trip_distance"]
    numerical = []
    print(f'Using numerical features: {numerical}')

    colnames = categorical + numerical
    return df, colnames

@task(log_prints=True)
def create_X(
    df: pd.DataFrame,
    dv: DictVectorizer = None
) -> tuple:

    df, colnames = get_features(df)

    dicts = df[colnames].to_dict(orient="records")

    if dv is None:
        print("Fitting and Transforming with DictVectorizer")
        dv = DictVectorizer(sparse=True)
        X = dv.fit_transform(dicts)
    else:
        print("Transforming with DictVectorizer")
        X = dv.transform(dicts)

    return X, dv


@task(log_prints=True)
def train_model(
    modeltype: str,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    dv: DictVectorizer,
):
    print(f"Training model of type {modeltype}")
    with mlflow.start_run() as run:
        if modeltype == "LR":
            from sklearn.linear_model import LinearRegression

            regressor = LinearRegression()
            regressor.fit(X_train, y_train)
            y_pred = regressor.predict(X_val)
            mlflow.sklearn.log_model(regressor, artifact_path="models_mlflow")
            # print(f'Intercept of the model: {regressor.intercept_}')

        elif modeltype == "XGB":
            import xgboost as xgb

            train = xgb.DMatrix(X_train, label=y_train)
            valid = xgb.DMatrix(X_val, label=y_val)

            best_params = {
                "learning_rate": 0.09585355369315604,
                "max_depth": 30,
                "min_child_weight": 1.060597050922164,
                "objective": "reg:linear",
                "reg_alpha": 0.018060244040060163,
                "reg_lambda": 0.011658731377413597,
                "seed": 42,
            }

            mlflow.log_params(best_params)

            booster = xgb.train(
                params=best_params,
                dtrain=train,
                num_boost_round=30,
                evals=[(valid, "validation")],
                early_stopping_rounds=50,
            )

            y_pred = booster.predict(valid)
            mlflow.xgboost.log_model(booster, artifact_path="models_mlflow")
        else:
            raise ValueError(f"Unknown model type: {modeltype}. Allowed: [LR, XGB]")

        rmse = root_mean_squared_error(y_val, y_pred)
        mlflow.log_metric("rmse", rmse)

        with open("models/preprocessor.b", "wb") as f_out:
            pickle.dump(dv, f_out)
        mlflow.log_artifact("models/preprocessor.b", artifact_path="preprocessor")

        return run.info.run_id


@flow
def nyc_taxi_train_pipeline(
    color: str,
    year: int,
    month: int,
    modeltype: str,
    read_local: bool) -> str:
    print (f'Starting the training of a {modeltype} model for color: {color} taxis with data from {year}-{month}')
    df_train = read_dataframe(
        color=color, year=year, month=month, read_local=read_local
    )

    next_year = year if month < 12 else year + 1
    next_month = month + 1 if month < 12 else 1
    df_val = read_dataframe(
        color=color, year=next_year, month=next_month, read_local=read_local
    )

    X_train, dv = create_X(df_train)
    X_val, _ = create_X(df_val, dv)

    target = "duration"
    y_train = df_train[target].values
    y_val = df_val[target].values

    run_id = train_model(modeltype, X_train, y_train, X_val, y_val, dv)
    print(f"MLflow run_id: {run_id}")
    return run_id


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Train a model to predict taxi trip duration."
    )
    parser.add_argument(
        "--color", type=str, required=True, help="Color of the taxi (green/yellow)"
    )
    parser.add_argument(
        "--year", type=int, required=True, help="Year of the data to train on"
    )
    parser.add_argument(
        "--month", type=int, required=True, help="Month of the data to train on"
    )
    parser.add_argument(
        "--modeltype", type=str, required=True, help="Model type (LR/XGB)"
    )
    args = parser.parse_args()

    print("Run params: {}".format(args))
    run_id = nyc_taxi_train_pipeline(
        color=args.color,
        year=args.year,
        month=args.month,
        modeltype=args.modeltype,
        read_local=False,
    )

    # print(f'run_id: {run_id}')
    # with open("run_id.txt", "w") as f:
    #     f.write(run_id)
