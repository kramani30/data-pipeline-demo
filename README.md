# Data Pipeline Demo

A simple ETL (Extract, Transform, Load) pipeline in Python that fetches weather data from a public API, transforms it into structured records, and loads it into a SQLite database.

## What it does

- **Extract** — Fetches hourly temperature data from the [Open-Meteo API](https://open-meteo.com/) (free, no API key required)
- **Transform** — Cleans and structures the raw API response into typed records
- **Load** — Persists transformed records into a SQLite database

## Project Structure

    data-pipeline-demo/
    ├── pipeline.py          # ETL pipeline (extract, transform, load)
    ├── requirements.txt     # Dependencies
    ├── tests/
    │   └── test_pipeline.py # Pytest unit tests with mocks
    └── .github/
        └── workflows/
            └── ci.yml       # GitHub Actions CI/CD

## Running the Pipeline

    pip install -r requirements.txt
    python pipeline.py

This will fetch today's hourly weather data for Toronto and load it into `weather.db`.

## Running Tests

    python -m pytest tests/ -v

## Tech Stack

- Python 3.11+
- requests — HTTP API calls
- SQLite — lightweight database storage
- pytest + pytest-mock — unit testing with mocks
- GitHub Actions — CI/CD on every push
