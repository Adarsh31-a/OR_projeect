# Grant Application Prioritization with AHP and TOPSIS

A modular Python decision-support system for prioritizing grant applications by expected socioeconomic impact. It uses the Analytic Hierarchy Process (AHP) to derive criteria weights and TOPSIS to rank applications. The system supports transparent calculations, data validation, visual analysis, comparison with weighted sum, and reproducible sensitivity analysis.

It does **not** approve, reject, or allocate funding independently. A review panel must combine its output with eligibility, feasibility, evidence quality, fairness, conflict-of-interest, and governance checks.

## Project objectives

1. Translate reviewer preferences across five socioeconomic criteria into AHP weights with a consistency check.
2. Rank applications with TOPSIS and compare the result with an AHP-weighted sum.
3. Give users a reproducible dashboard, experiments, exports, and sensitivity analysis.

## Techniques

### AHP

Reviewers enter reciprocal pairwise comparisons using the Saaty scale. The system validates that the matrix is square, positive, reciprocal, and has a unit diagonal. It derives the principal-eigenvector weight vector and reports lambda max, CI, and CR. A five-criterion matrix uses random index `RI = 1.12`; `CR > 0.10` triggers a warning without changing any judgment.

### TOPSIS

TOPSIS vector-normalizes the five impact columns, applies AHP weights, finds ideal-best and ideal-worst profiles, and calculates each application’s closeness coefficient. A higher coefficient means the application is closer to the specified ideal profile within this set of alternatives. The primary model treats all five impact scores as benefit criteria. Requested funding remains visible but does not determine impact rank.

See [mathematical formulas](docs/mathematical_formulas.md) for all equations and [methodology](docs/methodology.md) for the workflow.

## Dataset

The included `data/grant_applications.csv` contains 60 **simulated** records produced from a fixed seed. They are not real grant applications or measured outcomes. The fields are application ID, project name, region, sector, requested INR amount, and five 1–10 impact estimates. See [data documentation](data/README.md) and [dataset provenance](docs/dataset_sources.md) for the rubric and replacement process.

When importing a real dataset, use the same CSV columns and scoring range. The validation layer detects absent required columns, missing values, duplicate IDs, non-numeric values, invalid requested amounts, and scores outside 1–10. Record the real source’s endpoint, period, units, licence, and all transformations.

## Architecture

```text
app.py                         Streamlit interface
data/                          Included simulated CSV and generator
src/data_validation.py         Input-quality checks
src/ahp.py                     AHP calculation and consistency checks
src/topsis.py                  TOPSIS calculation and intermediate matrices
src/weighted_sum.py            Same-weight comparison method
src/sensitivity.py             Weight and score-perturbation studies
src/visualizations.py          Dashboard chart constructors
src/reporting.py               Dynamic HTML report creation
experiments/run_experiments.py Reproducible analysis outputs
tests/                         Mathematical and validation tests
docs/                          Method, limitations, and presentation material
```

## Installation

Python 3.11 is recommended. On macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run the dashboard

```bash
streamlit run app.py
```

The dashboard has Overview, Dataset Explorer, AHP Analysis, TOPSIS Ranking, Visual Analytics, Sensitivity Analysis, and Export and Reports pages. Uploading a valid CSV changes the current dashboard session only.

## Run tests

```bash
pytest -v
```

The tests cover AHP normalization and consistency, invalid matrices, TOPSIS bounds and ordering, zero-value columns, bad weights, duplicate IDs, missing values, and invalid scores.

## Run experiments

```bash
python experiments/run_experiments.py
```

The script saves computed CSV files and an HTML report in `experiments/results/`. It reports TOPSIS closeness coefficients, AHP consistency, Spearman rank correlation between TOPSIS and weighted sum, top-five overlap, and ranking stability after controlled score perturbation. Because the data are synthetic, these outputs illustrate model behavior rather than predictive accuracy or real-world effectiveness.

## Interpretation and limitations

TOPSIS and weighted-sum methods can give different ranks because TOPSIS considers each application’s distances from both ideal profiles, whereas weighted sum adds weighted normalized values. Neither method is universally superior. See [limitations](docs/limitations.md) before interpreting ranks. The 10-slide presentation plan and 15-minute demonstration script are in [presentation outline](docs/presentation_outline.md).

## References

- Saaty, T. L. (1980). *The Analytic Hierarchy Process: Planning, Priority Setting, Resource Allocation*. McGraw-Hill. ISBN 978-0070543713.
- Hwang, C.-L., & Yoon, K. (1981). *Multiple Attribute Decision Making: Methods and Applications*. Springer-Verlag. ISBN 978-0-387-10558-9.
- Vaidya, O. S., & Kumar, S. (2006). Analytic hierarchy process: An overview of applications. *European Journal of Operational Research*, 169(1), 1–29. https://doi.org/10.1016/j.ejor.2004.04.028
- Behzadian, M., Otaghsara, S. K., Yazdani, M., & Ignatius, J. (2012). A state-of-the-art survey of TOPSIS applications. *Expert Systems with Applications*, 39(17), 13051–13069. https://doi.org/10.1016/j.eswa.2012.05.056
