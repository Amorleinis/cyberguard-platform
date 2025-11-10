FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir . confluent-kafka pydantic

ENTRYPOINT ["spectra-producer"]
