"""Streamlit interface for transparent grant-application decision support."""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

from src import CRITERIA, CRITERIA_LABELS
from src.ahp import ahp_weight_table, calculate_ahp, default_pairwise_matrix
from src.data_loader import load_grant_applications
from src.data_validation import validate_grant_dataframe
from src.reporting import build_html_report
from src.sensitivity import score_perturbation_analysis, spearman_rank_correlation, weight_sensitivity
from src.topsis import calculate_topsis
from src.visualizations import (funding_score_chart, method_comparison_chart, score_heatmap,
                                sector_score_chart, top_applications_chart, weights_chart)
from src.weighted_sum import calculate_weighted_sum

ROOT = Path(__file__).parent
st.set_page_config(page_title="Grant Prioritization", page_icon="📊", layout="wide")


def current_data() -> pd.DataFrame:
    uploaded = st.session_state.get("uploaded_data")
    if uploaded is not None:
        return uploaded.copy()
    return load_grant_applications(ROOT / "data" / "grant_applications.csv")


def currency(value: float) -> str:
    return f"₹{value:,.0f}"


def compute(data: pd.DataFrame, pairwise_matrix: np.ndarray):
    ahp = calculate_ahp(pairwise_matrix)
    topsis = calculate_topsis(data, CRITERIA, ahp.weights)
    weighted_sum = calculate_weighted_sum(data, CRITERIA, ahp.weights)
    comparison = topsis.ranked[["application_id", "topsis_rank", "topsis_closeness"]].merge(
        weighted_sum[["application_id", "weighted_sum_rank", "weighted_sum_score"]], on="application_id"
    )
    comparison["rank_change_weighted_sum_minus_topsis"] = comparison["weighted_sum_rank"] - comparison["topsis_rank"]
    return ahp, topsis, weighted_sum, comparison


st.title("Grant Application Prioritization")
st.caption("A transparent decision-support demonstration using AHP weights and TOPSIS ranking. It does not approve or reject funding applications.")
if "pairwise_matrix" not in st.session_state:
    st.session_state.pairwise_matrix = default_pairwise_matrix()

page = st.sidebar.radio("Navigate", ["Overview", "Dataset Explorer", "AHP Analysis", "TOPSIS Ranking", "Visual Analytics", "Sensitivity Analysis", "Export and Reports"])
data = current_data()

try:
    ahp_result, topsis_result, weighted_sum_result, comparison = compute(data, st.session_state.pairwise_matrix)
except ValueError as error:
    st.error(str(error))
    st.stop()

if page == "Overview":
    metric_one, metric_two, metric_three, metric_four = st.columns(4)
    metric_one.metric("Applications", len(data))
    metric_two.metric("Total requested funding", currency(data["requested_amount"].sum()))
    metric_three.metric("Sectors", data["sector"].nunique())
    metric_four.metric("Average impact score", f"{data[CRITERIA].to_numpy().mean():.2f}/10")
    st.subheader("Purpose")
    st.write("The system prioritizes applications according to expected socioeconomic impact scores. AHP converts stated reviewer priorities into criterion weights. TOPSIS then ranks each application by proximity to an ideal high-impact profile and distance from a low-impact profile.")
    st.info("The included 60 records are simulated. Rankings demonstrate the method and require human review, evidence checks, and governance before any real funding decision.")
    st.subheader("Current AHP weights")
    st.plotly_chart(weights_chart(CRITERIA_LABELS, ahp_result.weights), use_container_width=True)

elif page == "Dataset Explorer":
    st.subheader("Input dataset")
    upload = st.file_uploader("Upload a CSV with the required fields", type="csv")
    if upload is not None:
        try:
            uploaded_frame = pd.read_csv(upload)
            report = validate_grant_dataframe(uploaded_frame, raise_on_error=False)
            if report["valid"]:
                st.session_state.uploaded_data = uploaded_frame
                st.success("Uploaded CSV is valid and is now used across the dashboard.")
                data = current_data()
            else:
                st.error("Upload failed validation: " + " | ".join(report["errors"]))
        except Exception as error:
            st.error(f"Unable to read the CSV: {error}")
    if st.button("Use included simulated dataset"):
        st.session_state.pop("uploaded_data", None)
        st.rerun()
    report = validate_grant_dataframe(data, raise_on_error=False)
    first, second, third = st.columns(3)
    first.metric("Rows", report["rows"])
    second.metric("Missing values", report["missing_values"])
    third.metric("Duplicate IDs", report["duplicate_application_ids"])
    st.success("Data-quality checks passed." if report["valid"] else "Data-quality checks need attention.")
    sectors = st.multiselect("Sector", sorted(data["sector"].unique()), default=sorted(data["sector"].unique()))
    regions = st.multiselect("Region", sorted(data["region"].unique()), default=sorted(data["region"].unique()))
    amount_range = st.slider("Requested amount (INR)", int(data.requested_amount.min()), int(data.requested_amount.max()), (int(data.requested_amount.min()), int(data.requested_amount.max())))
    search = st.text_input("Search project name or application ID")
    filtered = data[data.sector.isin(sectors) & data.region.isin(regions) & data.requested_amount.between(*amount_range)]
    if search:
        filtered = filtered[filtered.project_name.str.contains(search, case=False, na=False) | filtered.application_id.str.contains(search, case=False, na=False)]
    st.dataframe(filtered, use_container_width=True, hide_index=True)

elif page == "AHP Analysis":
    st.subheader("Pairwise comparisons")
    st.write("Use the Saaty scale: 1 means equal importance, 3 moderate, 5 strong, 7 very strong, and 9 extreme importance. Use reciprocal values for the reverse comparison.")
    editor = pd.DataFrame(st.session_state.pairwise_matrix, index=CRITERIA_LABELS, columns=CRITERIA_LABELS)
    edited = st.data_editor(editor, use_container_width=True, key="pairwise_editor", num_rows="fixed")
    update_col, reset_col = st.columns(2)
    if update_col.button("Apply pairwise matrix"):
        try:
            calculate_ahp(edited.to_numpy(float))
            st.session_state.pairwise_matrix = edited.to_numpy(float)
            st.rerun()
        except ValueError as error:
            st.error(f"Matrix not applied: {error}")
    if reset_col.button("Restore consistent example"):
        st.session_state.pairwise_matrix = default_pairwise_matrix()
        st.rerun()
    st.dataframe(ahp_weight_table(ahp_result), use_container_width=True, hide_index=True)
    st.plotly_chart(weights_chart(CRITERIA_LABELS, ahp_result.weights), use_container_width=True)
    one, two, three = st.columns(3)
    one.metric("Lambda max", f"{ahp_result.lambda_max:.6f}")
    two.metric("Consistency index", f"{ahp_result.consistency_index:.6f}")
    three.metric("Consistency ratio", f"{ahp_result.consistency_ratio:.6f}")
    (st.success if ahp_result.is_consistent else st.warning)("Judgments are acceptably consistent (CR ≤ 0.10)." if ahp_result.is_consistent else "Judgments are inconsistent (CR > 0.10). Review the pairwise comparisons before relying on the ranking.")
    st.markdown("**Calculation:** the principal eigenvector gives weights. `CI = (λmax − n)/(n − 1)` and `CR = CI/RI`; for five criteria, `RI = 1.12`. Higher weights give that criterion more influence in TOPSIS.")

elif page == "TOPSIS Ranking":
    st.subheader("Ranked applications")
    ranked = topsis_result.ranked
    selected_sectors = st.multiselect("Filter sectors", sorted(ranked.sector.unique()), default=sorted(ranked.sector.unique()), key="rank_sectors")
    search = st.text_input("Search ranking", key="rank_search")
    shown = ranked[ranked.sector.isin(selected_sectors)]
    if search:
        shown = shown[shown.project_name.str.contains(search, case=False, na=False) | shown.application_id.str.contains(search, case=False, na=False)]
    display_columns = ["topsis_rank", "application_id", "project_name", "sector", "region", "requested_amount", *CRITERIA, "topsis_closeness"]
    st.dataframe(shown[display_columns], use_container_width=True, hide_index=True)
    st.download_button("Download ranked CSV", ranked.to_csv(index=False).encode(), "ranked_applications.csv", "text/csv")
    with st.expander("Intermediate TOPSIS matrices"):
        st.write("Vector-normalized decision matrix")
        st.dataframe(pd.DataFrame(topsis_result.normalized_matrix, columns=CRITERIA), use_container_width=True)
        st.write("Weighted normalized matrix")
        st.dataframe(pd.DataFrame(topsis_result.weighted_matrix, columns=CRITERIA), use_container_width=True)
        st.dataframe(pd.DataFrame({"criterion": CRITERIA, "ideal_best": topsis_result.ideal_best, "ideal_worst": topsis_result.ideal_worst}), use_container_width=True, hide_index=True)
    st.caption("All five impact criteria are benefit criteria. Requested amount is shown for context and does not enter the TOPSIS ranking.")

elif page == "Visual Analytics":
    st.plotly_chart(top_applications_chart(topsis_result.ranked), use_container_width=True)
    st.plotly_chart(weights_chart(CRITERIA_LABELS, ahp_result.weights), use_container_width=True)
    st.plotly_chart(funding_score_chart(topsis_result.ranked), use_container_width=True)
    st.plotly_chart(sector_score_chart(topsis_result.ranked, CRITERIA), use_container_width=True)
    st.pyplot(score_heatmap(topsis_result.ranked, CRITERIA))
    st.plotly_chart(method_comparison_chart(comparison), use_container_width=True)

elif page == "Sensitivity Analysis":
    st.subheader("Criterion-weight sensitivity")
    st.caption("These sliders change the final weights directly. This differs from changing the AHP pairwise judgments on the AHP page.")
    raw_adjusted = np.array([st.slider(label, 0.0, 1.0, float(weight), 0.01, key=f"weight_{index}") for index, (label, weight) in enumerate(zip(CRITERIA_LABELS, ahp_result.weights))])
    result = weight_sensitivity(data, CRITERIA, ahp_result.weights, raw_adjusted)
    st.write("Normalized adjusted weights", {label: round(float(weight), 4) for label, weight in zip(CRITERIA_LABELS, result["adjusted_weights"])})
    st.metric("Spearman rank correlation", f"{result['spearman_correlation']:.4f}")
    st.metric("Top-five overlap", f"{result['top_five_overlap']}/5")
    st.dataframe(result["comparison"], use_container_width=True, hide_index=True)
    st.subheader("Application-score perturbation")
    perturbation = st.slider("Maximum score change", 0.0, 2.0, 0.5, 0.1)
    iterations = st.slider("Simulations", 10, 200, 100, 10)
    if st.button("Run reproducible perturbation analysis"):
        simulations = score_perturbation_analysis(data, CRITERIA, ahp_result.weights, perturbation, iterations, seed=2026)
        st.dataframe(simulations, use_container_width=True, hide_index=True)
        st.metric("Mean rank correlation", f"{simulations.spearman_correlation.mean():.4f}")
        st.metric("Mean top-five overlap", f"{simulations.top_five_overlap.mean():.2f}/5")
        st.caption("Results depend on the bounded uniform-noise assumption and fixed seed, not on observed future outcomes.")

else:
    st.subheader("Exports and current report")
    correlation = spearman_rank_correlation(comparison.topsis_rank, comparison.weighted_sum_rank)
    top_overlap = len(set(topsis_result.ranked.nsmallest(5, "topsis_rank").application_id) & set(weighted_sum_result.nsmallest(5, "weighted_sum_rank").application_id))
    metrics = {"AHP consistency ratio": f"{ahp_result.consistency_ratio:.6f}", "Spearman rank correlation": f"{correlation:.6f}", "Top-five overlap": f"{top_overlap}/5"}
    report = build_html_report(ahp_result, topsis_result.ranked, comparison.sort_values("topsis_rank"), metrics)
    st.download_button("Download ranked applications", topsis_result.ranked.to_csv(index=False).encode(), "ranked_applications.csv", "text/csv")
    st.download_button("Download AHP weights", ahp_weight_table(ahp_result).to_csv(index=False).encode(), "ahp_weights.csv", "text/csv")
    st.download_button("Download AHP consistency report", pd.DataFrame([{"lambda_max": ahp_result.lambda_max, "consistency_index": ahp_result.consistency_index, "consistency_ratio": ahp_result.consistency_ratio, "is_consistent": ahp_result.is_consistent}]).to_csv(index=False).encode(), "ahp_consistency.csv", "text/csv")
    st.download_button("Download weighted-sum comparison", comparison.to_csv(index=False).encode(), "weighted_sum_comparison.csv", "text/csv")
    st.download_button("Download HTML report", report.encode(), "grant_prioritization_report.html", "text/html")
