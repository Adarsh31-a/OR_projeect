# Ten-slide evaluation presentation

Replace the team placeholders and insert the results produced by `python experiments/run_experiments.py` immediately before presenting. Do not present values from a prior run as current results.

## Slide 1: Title and team

**Design and Development of an Operations Research-Based System to Prioritize Grant Applications Based on Socioeconomic Impact Using AHP and TOPSIS**

Team members, course, instructor, and evaluation date.

## Slide 2: Problem and motivation

Grant reviewers must compare applications across several competing impact dimensions. Explain that the project offers an auditable decision-support workflow, while reviewers retain accountability for funding decisions.

## Slide 3: Objectives and research questions

- Derive transparent criterion weights with AHP.
- Prioritize applications with TOPSIS.
- Compare TOPSIS with an AHP-weighted sum.
- Test sensitivity to changed weights and scores.

Ask which applications rank highest, how criteria influence rank, whether methods agree, and whether small changes alter the top five.

## Slide 4: Existing approaches and references

Describe AHP as a pairwise-comparison method that derives priority weights and reports a consistency ratio. Describe TOPSIS as a multi-criteria ranking method based on ideal and anti-ideal alternatives. Do not claim that either method always outperforms another approach.

References:

1. Saaty, T. L. (1980). *The Analytic Hierarchy Process: Planning, Priority Setting, Resource Allocation*. McGraw-Hill. ISBN 978-0070543713.
2. Hwang, C.-L., & Yoon, K. (1981). *Multiple Attribute Decision Making: Methods and Applications*. Springer-Verlag. ISBN 978-0-387-10558-9.
3. Vaidya, O. S., & Kumar, S. (2006). Analytic hierarchy process: An overview of applications. *European Journal of Operational Research*, 169(1), 1–29. https://doi.org/10.1016/j.ejor.2004.04.028
4. Behzadian, M., Otaghsara, S. K., Yazdani, M., & Ignatius, J. (2012). A state-of-the-art survey of TOPSIS applications. *Expert Systems with Applications*, 39(17), 13051–13069. https://doi.org/10.1016/j.eswa.2012.05.056

These sources describe methods and applications. The implementation results in this project come only from the included simulated data.

## Slide 5: Proposed AHP-TOPSIS methodology

Show: reviewer pairwise judgments → AHP weights and consistency check → normalized score matrix → weighted TOPSIS → closeness coefficient → ranked table. Include `CR ≤ 0.10` as the consistency guideline and the TOPSIS closeness formula.

## Slide 6: System architecture and dataset

Show modules: CSV validation, `ahp.py`, `topsis.py`, `weighted_sum.py`, `sensitivity.py`, experiments, Streamlit interface. State clearly that the bundled 60 records are reproducible simulated applications with 1–10 analyst-style impact estimates.

## Slide 7: Implementation demonstration

Open the AHP page. Change one reciprocal pair carefully, show the consistency ratio, restore the matrix, then open TOPSIS Ranking and expand intermediate matrices. Explain that requested funding is displayed but excluded from the primary impact ranking.

## Slide 8: Experimental results and visualizations

Run the experiment script and paste its current outputs: top applications, AHP weights, consistency ratio, method Spearman correlation, top-five overlap, and perturbation stability. Show the generated CSV/HTML report and dashboard charts. Label every value as generated from simulated data.

## Slide 9: Comparison, limitations, and future work

Explain why TOPSIS and weighted sum may differ: TOPSIS uses distance to ideal-best and ideal-worst profiles, while weighted sum aggregates values directly. State the limitations in `docs/limitations.md`. Suggest a future explicitly defined budget allocation model with fairness and feasibility constraints.

## Slide 10: Conclusion and references

Conclude that the system produces transparent, reproducible priorities for reviewer discussion. It does not automate awards. Include the four references from Slide 4 and invite questions.

# Fifteen-minute group demonstration

| Time | Presenter | Demonstration |
|---:|---|---|
| 0:00–2:00 | Member 1 | Slides 1–3: problem, scope, objectives, research questions |
| 2:00–4:00 | Member 2 | Slides 4–5: related methods, AHP/TOPSIS formulas and workflow |
| 4:00–6:00 | Member 3 | Slide 6: code structure, simulated data, validation and rubric |
| 6:00–10:00 | Member 4 | Slide 7 and dashboard: AHP matrix, CR, TOPSIS matrices, ranked result export |
| 10:00–13:00 | Member 5 | Slide 8: run experiment script, charts, TOPSIS versus weighted sum, sensitivity analysis |
| 13:00–15:00 | Member 1 | Slides 9–10: limitations, responsible use, conclusion, questions |

Before the demonstration, activate the environment, run tests, regenerate the experiment outputs, and start Streamlit. Keep a terminal visible to show the commands and generated files.
