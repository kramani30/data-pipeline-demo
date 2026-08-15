"""
ETL Pipeline Demo
-----------------
A simple ETL (Extract, Transform, Load) pipeline that:
- Extracts data from a public REST API (Open Meteo weather API)
- Transforms the raw data into a clean, structured format
- Loads the transformed data into a SQLite database

API Used: Open-Meteo (https://open-meteo.com/) - free, no API key required
"""

import sqlite3
import requests
from datetime import datetime


# ─── EXTRACT ────────────────────────────────────────────────────────────────

def extract(latitude: float, longitude: float) -> dict:
    """
    Fetch hourly temperature data from Open-Meteo API.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
    
    Returns:
        Raw JSON response from the API
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m",
        "temperature_unit": "celsius",
        "forecast_days": 1
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


# ─── TRANSFORM ──────────────────────────────────────────────────────────────

def transform(raw_data: dict) -> list[dict]:
    """
    Transform raw API response into clean, structured records.
    
    Args:
        raw_data: Raw JSON response from the API
    
    Returns:
        List of dictionaries with structured weather records
    """
    times = raw_data["hourly"]["time"]
    temperatures = raw_data["hourly"]["temperature_2m"]
    latitude = raw_data["latitude"]
    longitude = raw_data["longitude"]

    records = []
    for time, temp in zip(times, temperatures):
        records.append({
            "timestamp": time,
            "temperature_celsius": temp,
            "latitude": latitude,
            "longitude": longitude,
            "ingested_at": datetime.utcnow().isoformat()
        })
    return records


# ─── LOAD ───────────────────────────────────────────────────────────────────

def load(records: list[dict], db_path: str = "weather.db") -> None:
    """
    Load transformed records into a SQLite database.
    
    Args:
        records: List of structured weather records
        db_path: Path to the SQLite database file
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            temperature_celsius REAL,
            latitude REAL,
            longitude REAL,
            ingested_at TEXT
        )
    """)

    cursor.executemany("""
        INSERT INTO weather (timestamp, temperature_celsius, latitude, longitude, ingested_at)
        VALUES (:timestamp, :temperature_celsius, :latitude, :longitude, :ingested_at)
    """, records)

    conn.commit()
    conn.close()
    print(f"Loaded {len(records)} records into {db_path}")


# ─── RUN PIPELINE ───────────────────────────────────────────────────────────

def run_pipeline(latitude: float, longitude: float) -> None:
    """Run the full ETL pipeline."""
    print("Extracting data...")
    raw_data = extract(latitude, longitude)

    print("Transforming data...")
    records = transform(raw_data)
    print(f"Transformed {len(records)} records")

    print("Loading data...")
    load(records)
    print("Pipeline complete!")


if __name__ == "__main__":
    # Toronto coordinates
    run_pipeline(latitude=43.7, longitude=-79.42)
