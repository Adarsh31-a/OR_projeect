"""Chart constructors used by the Streamlit interface and experiments."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px


def top_applications_chart(ranked: pd.DataFrame):
    top = ranked.nlargest(10, "topsis_closeness").sort_values("topsis_closeness")
    return px.bar(top, x="topsis_closeness", y="project_name", orientation="h", color="sector",
                  title="Top 10 applications by TOPSIS closeness", labels={"topsis_closeness": "Closeness coefficient", "project_name": "Project"})


def weights_chart(labels: list[str], weights: np.ndarray):
    return px.bar(x=labels, y=weights, title="AHP criterion weights", labels={"x": "Criterion", "y": "Weight"})


def funding_score_chart(ranked: pd.DataFrame):
    return px.scatter(ranked, x="requested_amount", y="topsis_closeness", color="sector", hover_name="project_name",
                      title="Requested funding and TOPSIS score", labels={"requested_amount": "Requested amount (INR)", "topsis_closeness": "Closeness coefficient"})


def sector_score_chart(ranked: pd.DataFrame, criteria: list[str]):
    sector_scores = ranked.groupby("sector", as_index=False)[criteria].mean().melt(id_vars="sector", var_name="criterion", value_name="average_score")
    return px.bar(sector_scores, x="sector", y="average_score", color="criterion", barmode="group",
                  title="Average socioeconomic scores by sector", labels={"average_score": "Average score (1–10)"})


def score_heatmap(data: pd.DataFrame, criteria: list[str]):
    shown = data.head(25)
    figure, axis = plt.subplots(figsize=(11, 7))
    image = axis.imshow(shown[criteria].to_numpy(float), cmap="YlGnBu", aspect="auto", vmin=1, vmax=10)
    axis.set_title("Impact-score heatmap (first 25 applications)")
    axis.set_xticks(range(len(criteria)), [name.replace("_score", "").replace("_", " ").title() for name in criteria], rotation=35, ha="right")
    axis.set_yticks(range(len(shown)), shown["application_id"])
    figure.colorbar(image, ax=axis, label="Score (1–10)")
    figure.tight_layout()
    return figure


def method_comparison_chart(comparison: pd.DataFrame):
    plot_data = comparison.melt(id_vars="application_id", value_vars=["topsis_rank", "weighted_sum_rank"],
                                var_name="method", value_name="rank")
    return px.scatter(plot_data, x="application_id", y="rank", color="method", title="AHP–TOPSIS versus weighted-sum rank",
                      labels={"application_id": "Application", "rank": "Rank (lower is better)"}).update_yaxes(autorange="reversed")
