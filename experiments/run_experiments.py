"""Run reproducible analyses and save only values computed from the included dataset."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src import CRITERIA
from src.ahp import ahp_weight_table, calculate_ahp, default_pairwise_matrix
from src.data_loader import load_grant_applications
from src.reporting import build_html_report, write_text
from src.sensitivity import score_perturbation_analysis, spearman_rank_correlation
from src.topsis import calculate_topsis
from src.weighted_sum import calculate_weighted_sum


def main() -> None:
    results_directory = PROJECT_ROOT / "experiments" / "results"
    data = load_grant_applications(PROJECT_ROOT / "data" / "grant_applications.csv")
    ahp = calculate_ahp(default_pairwise_matrix())
    topsis = calculate_topsis(data, CRITERIA, ahp.weights)
    weighted_sum = calculate_weighted_sum(data, CRITERIA, ahp.weights)
    comparison = topsis.ranked[["application_id", "topsis_rank", "topsis_closeness"]].merge(
        weighted_sum[["application_id", "weighted_sum_rank", "weighted_sum_score"]], on="application_id"
    )
    comparison["rank_change_weighted_sum_minus_topsis"] = comparison["weighted_sum_rank"] - comparison["topsis_rank"]
    correlation = spearman_rank_correlation(comparison["topsis_rank"], comparison["weighted_sum_rank"])
    top_five_overlap = len(set(topsis.ranked.nsmallest(5, "topsis_rank")["application_id"]) & set(weighted_sum.nsmallest(5, "weighted_sum_rank")["application_id"]))
    perturbations = score_perturbation_analysis(data, CRITERIA, ahp.weights, perturbation=0.5, iterations=100, seed=2026)
    metrics = {
        "AHP consistency ratio": f"{ahp.consistency_ratio:.6f}",
        "Spearman rank correlation (TOPSIS vs weighted sum)": f"{correlation:.6f}",
        "Top-five overlap (TOPSIS vs weighted sum)": f"{top_five_overlap}/5",
        "Mean perturbation Spearman correlation": f"{perturbations['spearman_correlation'].mean():.6f}",
        "Mean perturbation top-five overlap": f"{perturbations['top_five_overlap'].mean():.2f}/5",
    }
    results_directory.mkdir(parents=True, exist_ok=True)
    topsis.ranked.to_csv(results_directory / "topsis_ranked_applications.csv", index=False)
    ahp_weight_table(ahp).to_csv(results_directory / "ahp_weights.csv", index=False)
    comparison.sort_values("topsis_rank").to_csv(results_directory / "method_comparison.csv", index=False)
    perturbations.to_csv(results_directory / "score_perturbation.csv", index=False)
    write_text(results_directory / "experiment_report.html", build_html_report(ahp, topsis.ranked, comparison.sort_values("topsis_rank"), metrics))
    write_text(results_directory / "experiment_summary.txt", "\n".join(f"{key}: {value}" for key, value in metrics.items()) + "\n")
    print("Experiments complete. Outputs saved to experiments/results/")
    for key, value in metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
