from pathlib import Path
import json
import pandas as pd
import joblib

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
MODELS_DIR = ROOT_DIR / "models"

DELAY_FILE = DATA_DIR / "get_around_delay_analysis.xlsx"
PRICING_FILE = DATA_DIR / "get_around_pricing_project.csv"
MODEL_FILE = MODELS_DIR / "getaround_pricing_pipeline.joblib"
FEATURE_ORDER_FILE = MODELS_DIR / "feature_order.json"

def load_delay_data() -> pd.DataFrame:
    return pd.read_excel(DELAY_FILE, sheet_name="rentals_data")

def load_pricing_data() -> pd.DataFrame:
    df = pd.read_csv(PRICING_FILE)
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    return df

def load_feature_order():
    return json.loads(FEATURE_ORDER_FILE.read_text(encoding="utf-8"))

def load_model():
    return joblib.load(MODEL_FILE)
