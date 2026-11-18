import numpy as np
from typing import List, Dict, Any, Tuple

# Saaty Random Consistency Index (RI) table
SAATY_RI = {
    1: 0.00,
    2: 0.00,
    3: 0.58,
    4: 0.90,
    5: 1.12,
    6: 1.24,
    7: 1.32,
    8: 1.41,
    9: 1.45,
    10: 1.49,
    11: 1.51,
    12: 1.48,
    13: 1.56,
    14: 1.57,
    15: 1.59
}


def compute_ahp_weights(
    matrix: List[List[float]],
    criteria_names: List[str]
) -> Tuple[Dict[str, float], float, float, bool, List[Dict[str, Any]]]:
    """
    Computes AHP weights using the principal eigenvector method.
    Returns:
      - weights: dict of criteria -> weight
      - cr: Consistency Ratio
      - lambda_max: Principal eigenvalue
      - is_consistent: True if CR < 0.10 (or n <= 2)
      - inconsistency_hints: list of pair suggestions that cause largest inconsistency
    """
    A = np.array(matrix, dtype=float)
    n = A.shape[0]

    if n != len(criteria_names):
        raise ValueError(f"Matrix dimension ({n}x{n}) does not match criteria count ({len(criteria_names)})")

    # Enforce exact diagonal = 1.0 and reciprocal consistency
    for i in range(n):
        A[i, i] = 1.0
        for j in range(i + 1, n):
            if A[i, j] <= 0:
                A[i, j] = 1.0
            A[j, i] = 1.0 / A[i, j]

    if n == 1:
        return {criteria_names[0]: 1.0}, 0.0, 1.0, True, []
    if n == 2:
        w1 = A[0, 1] / (1.0 + A[0, 1])
        w2 = 1.0 - w1
        return {criteria_names[0]: round(w1, 4), criteria_names[1]: round(w2, 4)}, 0.0, 2.0, True, []

    # Calculate eigenvalues and eigenvectors
    eigenvalues, eigenvectors = np.linalg.eig(A)
    max_idx = np.argmax(np.real(eigenvalues))
    lambda_max = float(np.real(eigenvalues[max_idx]))
    principal_eigenvector = np.real(eigenvectors[:, max_idx])

    # Invert signs if eigenvector is negative
    if np.sum(principal_eigenvector) < 0:
        principal_eigenvector = -principal_eigenvector

    # Normalization to sum to 1.0
    weights_vec = principal_eigenvector / np.sum(principal_eigenvector)
    weights = {criteria_names[i]: round(float(weights_vec[i]), 4) for i in range(n)}

    # Ensure total sum is 1.0
    diff = 1.0 - sum(weights.values())
    if abs(diff) > 0.0001:
        first_key = criteria_names[0]
        weights[first_key] = round(weights[first_key] + diff, 4)

    # Consistency calculations
    ci = (lambda_max - n) / (n - 1) if n > 1 else 0.0
    ri = SAATY_RI.get(n, 1.49)
    cr = (ci / ri) if ri > 0 else 0.0
    cr = max(0.0, round(float(cr), 4))
    is_consistent = cr <= 0.10

    # Inconsistency hints: find elements with highest error |a_ij - w_i/w_j|
    inconsistency_hints = []
    if not is_consistent:
        errors = []
        for i in range(n):
            for j in range(i + 1, n):
                ideal_ratio = weights_vec[i] / weights_vec[j]
                err = abs(A[i, j] - ideal_ratio)
                errors.append({
                    "c1": criteria_names[i],
                    "c2": criteria_names[j],
                    "current_val": round(float(A[i, j]), 2),
                    "suggested_val": round(float(ideal_ratio), 2),
                    "error": round(float(err), 3)
                })
        errors.sort(key=lambda x: x["error"], reverse=True)
        inconsistency_hints = errors[:3]

    return weights, cr, round(lambda_max, 4), is_consistent, inconsistency_hints
