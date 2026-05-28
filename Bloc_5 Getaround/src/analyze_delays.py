import argparse
import json
from pathlib import Path

import pandas as pd

from common import load_delay_data


def prepare_chains(delay: pd.DataFrame) -> pd.DataFrame:
    prev_delay = delay[["rental_id", "delay_at_checkout_in_minutes", "state"]].rename(
        columns={
            "rental_id": "previous_ended_rental_id",
            "delay_at_checkout_in_minutes": "previous_delay_at_checkout_in_minutes",
            "state": "previous_state",
        }
    )
    chains = delay.merge(prev_delay, on="previous_ended_rental_id", how="left")
    chains = chains[chains["time_delta_with_previous_rental_in_minutes"].notna()].copy()
    chains["previous_delay_positive"] = (
        chains["previous_delay_at_checkout_in_minutes"].fillna(0).clip(lower=0)
    )
    chains["impacted_by_previous_late"] = (
        chains["previous_delay_positive"] > chains["time_delta_with_previous_rental_in_minutes"]
    )
    return chains


def build_threshold_table(delay: pd.DataFrame, chains: pd.DataFrame) -> pd.DataFrame:
    thresholds = list(range(0, 24 * 60 + 1, 30))
    rows = []
    all_problematic = int(chains["impacted_by_previous_late"].sum())
    for scope in ["all", "connect", "mobile"]:
        subset = chains if scope == "all" else chains[chains["checkin_type"] == scope]
        subset_problematic = int(subset["impacted_by_previous_late"].sum())
        for threshold in thresholds:
            affected = subset["time_delta_with_previous_rental_in_minutes"] < threshold
            solved = affected & subset["impacted_by_previous_late"]
            rows.append(
                {
                    "scope": scope,
                    "threshold_min": threshold,
                    "affected_rentals": int(affected.sum()),
                    "affected_share_of_scope": float(affected.mean()) if len(subset) else 0.0,
                    "affected_share_of_all_rentals": float(affected.sum() / len(delay)),
                    "solved_problematic_cases": int(solved.sum()),
                    "solved_share_of_scope_problematic_cases": (
                        float(solved.sum() / subset_problematic) if subset_problematic else 0.0
                    ),
                    "solved_share_of_all_problematic_cases": (
                        float(solved.sum() / all_problematic) if all_problematic else 0.0
                    ),
                    "efficiency_solved_per_affected": (
                        float(solved.sum() / affected.sum()) if int(affected.sum()) else 0.0
                    ),
                }
            )
    return pd.DataFrame(rows)


def pick_recommendations(threshold_df: pd.DataFrame) -> tuple[dict, dict]:
    all_scope = threshold_df[threshold_df["scope"] == "all"].copy()
    all_scope = all_scope.sort_values(["solved_share_of_all_problematic_cases", "threshold_min"])
    # Smallest threshold solving at least 80% of all problematic cases
    qualified = all_scope[all_scope["solved_share_of_all_problematic_cases"] >= 0.80]
    recommendation = qualified.sort_values("threshold_min").iloc[0].to_dict()

    connect_scope = threshold_df[threshold_df["scope"] == "connect"].copy()
    qualified_connect = connect_scope[connect_scope["threshold_min"] == int(recommendation["threshold_min"])]
    fallback = qualified_connect.iloc[0].to_dict()
    return recommendation, fallback


def build_summary(delay: pd.DataFrame, chains: pd.DataFrame, threshold_df: pd.DataFrame) -> dict:
    recommendation, fallback = pick_recommendations(threshold_df)

    ended = delay[(delay["state"] == "ended") & delay["delay_at_checkout_in_minutes"].notna()].copy()
    problematic = chains[chains["impacted_by_previous_late"]].copy()

    checkout_by_type = {}
    for checkin_type, subset in ended.groupby("checkin_type"):
        checkout_by_type[checkin_type] = {
            "count": int(len(subset)),
            "median_delay_min": float(subset["delay_at_checkout_in_minutes"].median()),
            "late_gt_0_share": float((subset["delay_at_checkout_in_minutes"] > 0).mean()),
            "late_gt_15_share": float((subset["delay_at_checkout_in_minutes"] > 15).mean()),
            "late_gt_60_share": float((subset["delay_at_checkout_in_minutes"] > 60).mean()),
        }

    problematic_by_type = {}
    for checkin_type, subset in chains.groupby("checkin_type"):
        problematic_by_type[checkin_type] = {
            "linked_rentals": int(len(subset)),
            "problematic_cases": int(subset["impacted_by_previous_late"].sum()),
            "problematic_share": float(subset["impacted_by_previous_late"].mean()),
        }

    summary = {
        "dataset": {
            "all_rentals": int(len(delay)),
            "cars": int(delay["car_id"].nunique()),
            "ended_rentals": int((delay["state"] == "ended").sum()),
            "canceled_rentals": int((delay["state"] == "canceled").sum()),
            "linked_rentals": int(len(chains)),
            "linked_rentals_share": float(len(chains) / len(delay)),
        },
        "checkout_behavior": {
            "known_checkout_delays": int(len(ended)),
            "late_gt_0_share": float((ended["delay_at_checkout_in_minutes"] > 0).mean()),
            "late_gt_15_share": float((ended["delay_at_checkout_in_minutes"] > 15).mean()),
            "late_gt_60_share": float((ended["delay_at_checkout_in_minutes"] > 60).mean()),
            "median_delay_min": float(ended["delay_at_checkout_in_minutes"].median()),
            "p90_delay_min": float(ended["delay_at_checkout_in_minutes"].quantile(0.90)),
        },
        "checkout_behavior_by_checkin_type": checkout_by_type,
        "operational_risk": {
            "problematic_cases": int(problematic["impacted_by_previous_late"].sum()),
            "problematic_share_of_linked_rentals": float(problematic["impacted_by_previous_late"].sum() / len(chains)),
            "problematic_share_of_all_rentals": float(problematic["impacted_by_previous_late"].sum() / len(delay)),
            "median_overlap_when_problematic_min": float(
                problematic["time_delta_with_previous_rental_in_minutes"].median()
            ),
        },
        "operational_risk_by_checkin_type": problematic_by_type,
        "recommendation": recommendation,
        "conservative_fallback": fallback,
    }
    return summary


def main(output_csv: str, output_json: str) -> None:
    delay = load_delay_data()
    chains = prepare_chains(delay)
    threshold_df = build_threshold_table(delay, chains)
    summary = build_summary(delay, chains, threshold_df)

    output_csv_path = Path(output_csv)
    output_json_path = Path(output_json)
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)

    threshold_df.to_csv(output_csv_path, index=False)
    output_json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Saved threshold simulation to {output_csv_path}")
    print(f"Saved business summary to {output_json_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_csv", default="data/threshold_simulation.csv")
    parser.add_argument("--output_json", default="data/business_summary.json")
    args = parser.parse_args()
    main(args.output_csv, args.output_json)
