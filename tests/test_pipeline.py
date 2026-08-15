"""
Unit tests for the ETL pipeline.
Run with: python -m pytest tests/ -v
"""

import pytest
import sqlite3
import os
from unittest.mock import patch, MagicMock
from pipeline import extract, transform, load, run_pipeline


# ─── Sample test data ───────────────────────────────────────────────────────

MOCK_API_RESPONSE = {
    "latitude": 43.7,
    "longitude": -79.42,
    "hourly": {
        "time": [
            "2026-08-15T00:00",
            "2026-08-15T01:00",
            "2026-08-15T02:00"
        ],
        "temperature_2m": [18.5, 17.2, 16.8]
    }
}


# ─── Extract tests ──────────────────────────────────────────────────────────

class TestExtract:
    @patch("pipeline.requests.get")
    def test_extract_calls_correct_url(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_API_RESPONSE
        mock_get.return_value = mock_response

        result = extract(43.7, -79.42)

        mock_get.assert_called_once()
        assert result == MOCK_API_RESPONSE

    @patch("pipeline.requests.get")
    def test_extract_raises_on_bad_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response

        with pytest.raises(Exception):
            extract(43.7, -79.42)


# ─── Transform tests ────────────────────────────────────────────────────────

class TestTransform:
    def test_transform_returns_correct_count(self):
        records = transform(MOCK_API_RESPONSE)
        assert len(records) == 3

    def test_transform_record_structure(self):
        records = transform(MOCK_API_RESPONSE)
        record = records[0]
        assert "timestamp" in record
        assert "temperature_celsius" in record
        assert "latitude" in record
        assert "longitude" in record
        assert "ingested_at" in record

    def test_transform_correct_values(self):
        records = transform(MOCK_API_RESPONSE)
        assert records[0]["temperature_celsius"] == 18.5
        assert records[0]["latitude"] == 43.7
        assert records[0]["longitude"] == -79.42

    def test_transform_timestamps_match(self):
        records = transform(MOCK_API_RESPONSE)
        assert records[0]["timestamp"] == "2026-08-15T00:00"
        assert records[1]["timestamp"] == "2026-08-15T01:00"
        assert records[2]["timestamp"] == "2026-08-15T02:00"


# ─── Load tests ─────────────────────────────────────────────────────────────

class TestLoad:
    def test_load_creates_database(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        records = transform(MOCK_API_RESPONSE)
        load(records, db_path)
        assert os.path.exists(db_path)

    def test_load_correct_record_count(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        records = transform(MOCK_API_RESPONSE)
        load(records, db_path)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM weather")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 3

    def test_load_correct_values(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        records = transform(MOCK_API_RESPONSE)
        load(records, db_path)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT temperature_celsius FROM weather ORDER BY id")
        temps = [row[0] for row in cursor.fetchall()]
        conn.close()

        assert temps == [18.5, 17.2, 16.8]
