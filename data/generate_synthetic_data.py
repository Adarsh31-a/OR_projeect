"""Generate the included simulated grant-application dataset with a fixed seed."""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

SEED = 20261102
PROJECTS = {
    "Education": ["Digital Learning Centre", "School Retention Initiative", "Community Library Network", "STEM Lab Access"],
    "Healthcare": ["Mobile Primary Care", "Maternal Health Outreach", "Rural Diagnostic Hub", "Telemedicine Access"],
    "Rural Development": ["Farmer Producer Support", "Village Infrastructure Plan", "Women’s Livelihood Collective", "Climate-Resilient Agriculture"],
    "Employment": ["Youth Skills Academy", "Artisan Market Linkage", "Green Jobs Training", "Microenterprise Incubator"],
    "Drinking Water": ["Safe Water Kiosks", "Village Water Security", "Groundwater Recharge", "Water Quality Monitoring"],
}
REGIONS = ["North", "South", "East", "West", "Central", "North-East"]


def generate_dataset(rows: int = 60, seed: int = SEED) -> pd.DataFrame:
    """Create plausible but explicitly simulated records, never real applications."""
    random_generator = np.random.default_rng(seed)
    sectors = list(PROJECTS)
    records = []
    for number in range(1, rows + 1):
        sector = sectors[(number - 1) % len(sectors)]
        sector_effect = {
            "Education": np.array([0.3, 0.8, -0.5, 2.0, 0.6]),
            "Healthcare": np.array([0.7, -0.2, 2.0, 0.2, 0.8]),
            "Rural Development": np.array([1.8, 1.0, 0.3, 0.4, 0.7]),
            "Employment": np.array([1.2, 2.1, -0.4, 0.2, 0.6]),
            "Drinking Water": np.array([1.5, 0.3, 1.3, 0.5, 1.0]),
        }[sector]
        base = random_generator.normal(6.1, 1.35, size=5) + sector_effect
        scores = np.clip(np.rint(base), 1, 10).astype(int)
        project = PROJECTS[sector][(number - 1) % len(PROJECTS[sector])]
        records.append({
            "application_id": f"SIM-{number:03d}",
            "project_name": f"{project} {number:02d}",
            "region": REGIONS[(number * 3 + number // 4) % len(REGIONS)],
            "sector": sector,
            "requested_amount": int(random_generator.integers(750_000, 12_500_001) // 10_000 * 10_000),
            "poverty_reduction_score": scores[0],
            "employment_generation_score": scores[1],
            "healthcare_impact_score": scores[2],
            "education_impact_score": scores[3],
            "beneficiaries_score": scores[4],
        })
    return pd.DataFrame(records)


if __name__ == "__main__":
    output = Path(__file__).with_name("grant_applications.csv")
    generate_dataset().to_csv(output, index=False)
    print(f"Wrote {output}")
