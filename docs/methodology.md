# Methodology

## Decision-support setting

This project assists a review panel in comparing expected socioeconomic impact. It does not independently determine funding awards. Human reviewers should check eligibility, implementation risk, evidence quality, fairness, geographic balance, conflicts of interest, and budget constraints separately.

## Criteria and judgments

The five impact criteria are poverty reduction, employment generation, healthcare impact, education impact, and beneficiary reach. AHP asks the panel to compare their relative importance using a reciprocal Saaty-scale matrix. The default matrix encodes illustrative weights of 0.30, 0.25, 0.20, 0.15, and 0.10. The matrix is intentionally consistent so users can test the workflow before entering their own panel judgments.

## Ranking and comparison

TOPSIS first vector-normalizes application scores, applies AHP weights, and evaluates each application against ideal-best and ideal-worst score profiles. The application with a larger closeness coefficient receives higher priority. A weighted-sum ranking uses the same normalized data and weights as a transparent comparator.

## Reproducible experiments

`experiments/run_experiments.py` validates the included data, computes AHP and TOPSIS results, compares ranks with weighted sum, and runs 100 bounded score-perturbation simulations with seed 2026. It saves the ranked table, weights, comparison, perturbation results, and HTML report. Values in saved reports originate from that run.

## Sensitivity analysis

The dashboard supports two distinct exercises. Users can either modify final criterion weights directly, after which the system renormalizes and reruns TOPSIS, or change AHP pairwise judgments on the AHP page, which derives a new weight vector. A separate score perturbation adds uniform noise bounded by a user-defined amount and clips values to the 1--10 scale. Spearman correlation and top-five overlap summarize stability; they depend on the perturbation assumptions.
