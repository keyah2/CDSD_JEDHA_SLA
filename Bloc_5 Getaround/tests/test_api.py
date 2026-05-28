from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_metadata_contains_features():
    response = client.get("/metadata")
    assert response.status_code == 200
    body = response.json()
    assert "feature_order" in body
    assert len(body["feature_order"]) == 13

def test_predict_with_dict_payload():
    payload = {
        "input": [{
            "model_key": "Citroën",
            "mileage": 140000,
            "engine_power": 100,
            "fuel": "diesel",
            "paint_color": "black",
            "car_type": "sedan",
            "private_parking_available": True,
            "has_gps": True,
            "has_air_conditioning": True,
            "automatic_car": False,
            "has_getaround_connect": True,
            "has_speed_regulator": True,
            "winter_tires": False,
        }]
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "prediction" in body
    assert len(body["prediction"]) == 1

def test_predict_rejects_missing_feature():
    payload = {"input": [{"model_key": "Citroën"}]}
    response = client.post("/predict", json=payload)
    assert response.status_code == 400
