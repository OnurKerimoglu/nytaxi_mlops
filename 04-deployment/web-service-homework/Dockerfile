FROM agrigorev/zoomcamp-model:mlops-2024-3.10.13-slim

RUN pip install -U pip
RUN pip install pipenv

WORKDIR /app

COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --system --deploy

COPY ["predict.py", "./"]

# EXPOSE 9696
# ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:9696", "model_prediction:app"]

ENTRYPOINT ["python", "predict.py"]
