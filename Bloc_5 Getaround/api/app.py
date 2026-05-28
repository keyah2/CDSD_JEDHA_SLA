import json
import os
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT_DIR / "models"
LOCAL_MODEL_PATH = MODELS_DIR / "getaround_pricing_pipeline.joblib"
FEATURE_ORDER = json.loads((MODELS_DIR / "feature_order.json").read_text(encoding="utf-8"))
PRICING_METRICS = json.loads((MODELS_DIR / "pricing_metrics.json").read_text(encoding="utf-8"))


class PredictionRequest(BaseModel):
    input: list[Any] = Field(
        ...,
        description="Chaque ligne peut être fournie sous forme de dictionnaire avec les noms de variables ou sous forme de liste ordonnée comme `/metadata`.",
        examples=[
            {
                "input": [
                    {
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
                        "winter_tires": False
                    }
                ]
            }
        ],
    )


class PredictionResponse(BaseModel):
    prediction: list[float]


def load_model():
    mlflow_model_uri = os.getenv("MLFLOW_MODEL_URI")
    if mlflow_model_uri:
        try:
            import mlflow
            return mlflow.pyfunc.load_model(mlflow_model_uri)
        except Exception:
            pass
    return joblib.load(LOCAL_MODEL_PATH)


MODEL = load_model()


def _payload_to_dataframe(payload: list[Any]) -> pd.DataFrame:
    if not payload:
        raise HTTPException(status_code=400, detail="La liste d’entrée est vide.")
    first = payload[0]
    if isinstance(first, dict):
        if not all(isinstance(item, dict) for item in payload):
            raise HTTPException(status_code=400, detail="Toutes les lignes doivent avoir le même format : soit des dictionnaires, soit des listes.")
        df = pd.DataFrame(payload)
        missing = [feature for feature in FEATURE_ORDER if feature not in df.columns]
        if missing:
            raise HTTPException(status_code=400, detail=f"Variables manquantes : {missing}")
        df = df[FEATURE_ORDER]
    else:
        if not all(isinstance(item, list) for item in payload):
            raise HTTPException(status_code=400, detail="Toutes les lignes doivent avoir le même format : soit des dictionnaires, soit des listes.")
        bad_rows = [idx for idx, row in enumerate(payload) if len(row) != len(FEATURE_ORDER)]
        if bad_rows:
            raise HTTPException(
                status_code=400,
                detail=f"Les lignes {bad_rows} ne correspondent pas à la longueur attendue : {len(FEATURE_ORDER)} variables."
            )
        df = pd.DataFrame(payload, columns=FEATURE_ORDER)
    return df


description = """
API de prédiction du prix journalier de location pour le projet GetAround.

## Routes principales
- `GET /` : route d'accueil
- `GET /health` : statut du service
- `GET /metadata` : variables attendues, informations sur le modèle et métriques principales
- `POST /predict` : retourne une prédiction par ligne fournie

## Remarque
Le brief impose principalement `/predict` et `/docs`. Cette implémentation conserve ce socle et ajoute une validation plus claire ainsi qu'une route de métadonnées utile pour l'exploitation.
"""

app = FastAPI(
    title="GetAround Pricing API",
    description=description,
    version="3.0.0",
    contact={"name": "GetAround Project"},
    openapi_tags=[
        {"name": "Santé", "description": "Statut du service et route d’accueil."},
        {"name": "Métadonnées", "description": "Endpoint exposant les variables attendues et les informations du modèle."},
        {"name": "Machine Learning", "description": "Endpoint de prédiction du prix journalier."},
    ],
)


@app.get("/", tags=["Santé"])
async def index():
    return {
        "message": "Bienvenue sur l’API de prédiction de prix GetAround.",
        "docs": "/docs",
        "predict_endpoint": "/predict",
        "metadata_endpoint": "/metadata",
    }


@app.get("/health", tags=["Santé"])
async def health():
    return {"status": "ok", "model_loaded": True}


@app.get("/metadata", tags=["Métadonnées"])
async def metadata():
    return {
        "feature_order": FEATURE_ORDER,
        "best_model": PRICING_METRICS["best_model"],
        "chosen_model_metrics": PRICING_METRICS["chosen_model_metrics"],
        "top_features": PRICING_METRICS["top_features"],
    }


@app.post("/predict", tags=["Machine Learning"], response_model=PredictionResponse)
async def predict(payload: PredictionRequest):
    df = _payload_to_dataframe(payload.input)
    prediction = MODEL.predict(df)
    return {"prediction": [round(float(x), 2) for x in prediction]}
