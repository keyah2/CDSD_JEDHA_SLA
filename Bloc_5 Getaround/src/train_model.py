import argparse
import json
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


def maybe_start_mlflow():
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    if not tracking_uri:
        return None
    try:
        import mlflow

        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment("getaround-pricing")
        return mlflow
    except Exception:
        return None


def aggregate_feature_importance(pipe: Pipeline, cat_cols: list[str], num_cols: list[str], bool_cols: list[str]) -> list[dict]:
    model = pipe.named_steps["model"]
    if not hasattr(model, "feature_importances_"):
        return []
    raw_importances = model.feature_importances_
    preprocessor = pipe.named_steps["preprocessor"]
    onehot = preprocessor.named_transformers_["cat"].named_steps["onehot"]
    encoded_cat_names = onehot.get_feature_names_out(cat_cols).tolist()
    raw_feature_names = num_cols + encoded_cat_names + bool_cols

    feature_map = {}
    for raw_name, importance in zip(raw_feature_names, raw_importances):
        base_name = raw_name
        for col in cat_cols:
            if raw_name.startswith(f"{col}_"):
                base_name = col
                break
        feature_map[base_name] = feature_map.get(base_name, 0.0) + float(importance)

    return [
        {"feature": feature, "importance": importance}
        for feature, importance in sorted(feature_map.items(), key=lambda item: item[1], reverse=True)
    ]


def main(input_path: str, output_model_path: str) -> None:
    df = pd.read_csv(input_path)
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    X = df.drop(columns=["rental_price_per_day"])
    y = df["rental_price_per_day"]

    cat_cols = X.select_dtypes(include=["object"]).columns.tolist()
    bool_cols = X.select_dtypes(include=["bool"]).columns.tolist()
    num_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()

    preprocessor = ColumnTransformer(
        [
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), num_cols),
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                cat_cols,
            ),
            ("bool", "passthrough", bool_cols),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    candidates = {
        "LinearRegression": LinearRegression(),
        "Ridge": Ridge(alpha=1.0),
        "RandomForest": RandomForestRegressor(
            n_estimators=500, min_samples_leaf=2, random_state=42, n_jobs=-1
        ),
        "ExtraTrees": ExtraTreesRegressor(
            n_estimators=500, min_samples_leaf=2, random_state=42, n_jobs=-1
        ),
    }

    results = []
    fitted = {}
    for name, estimator in candidates.items():
        pipe = Pipeline([("preprocessor", preprocessor), ("model", estimator)])
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        results.append(
            {
                "model": name,
                "MAE": float(mean_absolute_error(y_test, pred)),
                "RMSE": float(np.sqrt(mean_squared_error(y_test, pred))),
                "R2": float(r2_score(y_test, pred)),
            }
        )
        fitted[name] = pipe

    results_df = pd.DataFrame(results).sort_values(["RMSE", "MAE"], ascending=[True, True])
    best_model_name = str(results_df.iloc[0]["model"])
    best_pipe = fitted[best_model_name]

    output_model = Path(output_model_path)
    output_model.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipe, output_model)
    feature_order = X.columns.tolist()
    (output_model.parent / "feature_order.json").write_text(
        json.dumps(feature_order, indent=2), encoding="utf-8"
    )

    top_features = aggregate_feature_importance(best_pipe, cat_cols, num_cols, bool_cols)[:10]
    metrics_payload = {
        "best_model": best_model_name,
        "holdout_metrics": results_df.to_dict(orient="records"),
        "chosen_model_metrics": results_df.iloc[0].to_dict(),
        "feature_order": feature_order,
        "top_features": top_features,
    }
    (output_model.parent / "pricing_metrics.json").write_text(
        json.dumps(metrics_payload, indent=2), encoding="utf-8"
    )

    mlflow = maybe_start_mlflow()
    if mlflow is not None:
        with mlflow.start_run(run_name=f"getaround-{best_model_name.lower()}"):
            mlflow.log_param("best_model", best_model_name)
            chosen = results_df.iloc[0].to_dict()
            for key, value in chosen.items():
                if key != "model":
                    mlflow.log_metric(key.lower(), float(value))
            try:
                mlflow.sklearn.log_model(best_pipe, artifact_path="model")
            except Exception:
                pass

    print(results_df.to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", default="data/get_around_pricing_project.csv")
    parser.add_argument("--output_model_path", default="models/getaround_pricing_pipeline.joblib")
    args = parser.parse_args()
    main(args.input_path, args.output_model_path)
