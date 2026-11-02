# Mathematical formulas

## AHP

Let `A = [a_ij]` be the reciprocal pairwise-comparison matrix. A reviewer supplies values from the Saaty scale, where `a_ij` expresses how much more important criterion `i` is than criterion `j`, `a_ii = 1`, and `a_ji = 1/a_ij`.

The implementation shows a column-normalized matrix for inspection and calculates the final priority vector `w` from the principal right eigenvector:

`A w = lambda_max w`

It rescales `w` so that `sum(w_i) = 1`. For an `n`-criterion matrix:

`CI = (lambda_max - n) / (n - 1)`

`CR = CI / RI`

For the five criteria in this project, `RI = 1.12`. The dashboard flags `CR > 0.10`; it does not alter entered judgments.

## TOPSIS

For decision-matrix value `x_ij`, vector normalization is:

`r_ij = x_ij / sqrt(sum_i x_ij^2)`

The weighted normalized value is `v_ij = w_j r_ij`. For benefit criteria, the ideal best is the column maximum and the ideal worst is the column minimum. For cost criteria, the directions reverse.

`D_i+ = sqrt(sum_j (v_ij - v_j+)^2)`

`D_i- = sqrt(sum_j (v_ij - v_j-)^2)`

`C_i = D_i- / (D_i+ + D_i-)`

The system ranks applications in descending `C_i`. All five example criteria are benefits. Requested funding does not enter the default TOPSIS matrix.

## Weighted-sum comparator

The comparison method uses the same vector-normalized criteria and AHP weights, then calculates `S_i = sum_j w_j r_ij`. Unlike TOPSIS, it does not consider an ideal or anti-ideal profile. This difference can change ranks.
