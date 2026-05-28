import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from common import load_delay_data


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
ASSETS_DIR = ROOT_DIR / "assets"
MODELS_DIR = ROOT_DIR / "models"

ASSETS_DIR.mkdir(parents=True, exist_ok=True)

def build_delay_distribution(delay: pd.DataFrame) -> None:
    ended = delay[(delay["state"] == "ended") & delay["delay_at_checkout_in_minutes"].notna()].copy()
    low = ended["delay_at_checkout_in_minutes"].quantile(0.01)
    high = ended["delay_at_checkout_in_minutes"].quantile(0.99)
    ended["delay_winsorized"] = ended["delay_at_checkout_in_minutes"].clip(lower=low, upper=high)

    plt.figure(figsize=(10, 6))
    for label in ["connect", "mobile"]:
        subset = ended[ended["checkin_type"] == label]
        plt.hist(subset["delay_winsorized"], bins=60, alpha=0.55, label=label)
    plt.title("Checkout delay distribution (winsorized 1%-99%)")
    plt.xlabel("Delay at checkout in minutes")
    plt.ylabel("Number of rentals")
    plt.legend()
    plt.tight_layout()
    plt.savefig(ASSETS_DIR / "delay_distribution.png", dpi=200)
    plt.close()

def build_threshold_tradeoff(thresholds: pd.DataFrame) -> None:
    subset = thresholds[thresholds["scope"].isin(["all", "connect"])].copy()
    fig, ax = plt.subplots(figsize=(10, 6))
    for scope in ["all", "connect"]:
        scoped = subset[subset["scope"] == scope]
        ax.plot(scoped["threshold_min"], scoped["solved_share_of_all_problematic_cases"], marker="o", label=f"{scope} — solved share")
        ax.plot(scoped["threshold_min"], scoped["affected_share_of_all_rentals"], marker="x", linestyle="--", label=f"{scope} — affected share")
    ax.set_title("Threshold trade-off")
    ax.set_xlabel("Threshold (minutes)")
    ax.set_ylabel("Share")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(ASSETS_DIR / "threshold_tradeoff.png", dpi=200)
    plt.close()

def build_feature_importance() -> None:
    metrics = json.loads((MODELS_DIR / "pricing_metrics.json").read_text(encoding="utf-8"))
    features = pd.DataFrame(metrics["top_features"]).sort_values("importance")
    plt.figure(figsize=(10, 6))
    plt.barh(features["feature"], features["importance"])
    plt.title("Top pricing drivers")
    plt.xlabel("Aggregated importance")
    plt.tight_layout()
    plt.savefig(ASSETS_DIR / "feature_importance.png", dpi=200)
    plt.close()

def main():
    delay = load_delay_data()
    thresholds = pd.read_csv(DATA_DIR / "threshold_simulation.csv")
    build_delay_distribution(delay)
    build_threshold_tradeoff(thresholds)
    build_feature_importance()
    print("Assets created in assets/")

if __name__ == "__main__":
    main()
