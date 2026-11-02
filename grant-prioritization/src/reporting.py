"""Exports that preserve the computed analysis rather than static example results."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import pandas as pd


def build_html_report(ahp_result, ranked: pd.DataFrame, comparison: pd.DataFrame, metrics: dict) -> str:
    """Create a compact self-contained report from current calculations."""
    top = ranked.nsmallest(10, "topsis_rank")
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    metrics_html = "".join(f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>" for key, value in metrics.items())
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>Grant prioritization report</title>
    <style>body{{font-family:Arial,sans-serif;margin:2rem;line-height:1.45}} table{{border-collapse:collapse;width:100%}} th,td{{padding:.4rem;border:1px solid #ccc;text-align:left}} th{{background:#eef4f7}}</style></head>
    <body><h1>Grant application decision-support report</h1><p>Generated {generated_at}. The included records are simulated demonstration data. This report supports review and does not make funding decisions.</p>
    <h2>AHP consistency</h2><ul><li>Lambda max: {ahp_result.lambda_max:.6f}</li><li>Consistency index: {ahp_result.consistency_index:.6f}</li><li>Consistency ratio: {ahp_result.consistency_ratio:.6f}</li><li>Acceptable at CR ≤ 0.10: {ahp_result.is_consistent}</li></ul>
    <h2>Experimental metrics</h2><ul>{metrics_html}</ul><h2>Top 10 TOPSIS applications</h2>{top.to_html(index=False, float_format=lambda value: f'{value:.4f}')}
    <h2>Method comparison</h2>{comparison.to_html(index=False)}</body></html>"""


def write_text(path: str | Path, contents: str) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(contents, encoding="utf-8")
    return destination
