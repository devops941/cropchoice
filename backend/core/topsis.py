import math
import numpy as np
from typing import List, Dict, Any, Tuple
from scipy.stats import spearmanr, kendalltau

# Default criterion directions: "cost" (lower is better), "benefit" (higher is better)
CRITERIA_DIRECTIONS = {
    "water": "cost",
    "wsr": "cost",
    "soil": "benefit",
    "return": "benefit",
    "variability": "cost",
    "labour": "cost",
    "duration": "cost",
    "profit_per_water": "benefit"
}


def run_topsis(
    crop_evaluations: List[Dict[str, Any]],
    weights: Dict[str, float],
    use_wsr: bool = False,
    normalization_method: str = "vector"
) -> Dict[str, Any]:
    """
    Executes TOPSIS multi-criteria ranking on the evaluated crops.
    """
    if not crop_evaluations:
        return {"rankings": [], "correlation": {"spearman": 1.0, "kendall": 1.0}}

    water_key = "wsr" if use_wsr else "water"
    criteria_keys = ["water", "soil", "return", "variability"]
    active_keys = [k for k in criteria_keys if k in weights and weights[k] > 0]
    if not active_keys:
        active_keys = ["water", "soil", "return", "variability"]

    # Remap water weight if use_wsr
    used_weights = {}
    for k in active_keys:
        val = weights.get(k, 0.25)
        mapped_key = water_key if k == "water" else k
        used_weights[mapped_key] = val

    matrix_keys = list(used_weights.keys())
    w_sum = sum(used_weights.values())
    w_norm = [used_weights[k] / w_sum for k in matrix_keys]

    m = len(crop_evaluations)
    n = len(matrix_keys)

    # 1. Build Decision Matrix X (m x n)
    X = np.zeros((m, n), dtype=float)
    for i, item in enumerate(crop_evaluations):
        cv = item["criteria_values"]
        for j, k in enumerate(matrix_keys):
            X[i, j] = float(cv.get(k, 0.0))

    # 2. Vector Normalization: r_ij = x_ij / sqrt(sum_i x_ij^2)
    R = np.zeros_like(X)
    for j in range(n):
        col = X[:, j]
        norm = np.linalg.norm(col)
        if norm > 0:
            R[:, j] = col / norm
        else:
            R[:, j] = 0.0

    # 3. Weighted Normalized Matrix V = w_j * r_ij
    V = np.zeros_like(R)
    for j in range(n):
        V[:, j] = R[:, j] * w_norm[j]

    # 4. Ideal Best (A+) and Ideal Worst (A-)
    A_plus = np.zeros(n)
    A_minus = np.zeros(n)
    for j, k in enumerate(matrix_keys):
        direction = CRITERIA_DIRECTIONS.get(k, "benefit")
        if direction == "benefit":
            A_plus[j] = np.max(V[:, j])
            A_minus[j] = np.min(V[:, j])
        else:  # cost
            A_plus[j] = np.min(V[:, j])
            A_minus[j] = np.max(V[:, j])

    # 5. Separation Distances S+ and S-
    S_plus = np.zeros(m)
    S_minus = np.zeros(m)
    for i in range(m):
        S_plus[i] = np.sqrt(np.sum((V[i, :] - A_plus) ** 2))
        S_minus[i] = np.sqrt(np.sum((V[i, :] - A_minus) ** 2))

    # 6. Closeness Coefficient C_i = S-_i / (S+_i + S-_i)
    C = np.zeros(m)
    for i in range(m):
        denom = S_plus[i] + S_minus[i]
        C[i] = (S_minus[i] / denom) if denom > 0 else 0.5

    # 7. Weighted Sum Model (WSM) cross-check on min-max values
    X_minmax = np.zeros_like(X)
    for j, k in enumerate(matrix_keys):
        col = X[:, j]
        min_v = np.min(col)
        max_v = np.max(col)
        rng = max_v - min_v
        direction = CRITERIA_DIRECTIONS.get(k, "benefit")
        if rng > 0:
            if direction == "benefit":
                X_minmax[:, j] = (col - min_v) / rng
            else:
                X_minmax[:, j] = (max_v - col) / rng
        else:
            X_minmax[:, j] = 1.0

    WSM_scores = np.dot(X_minmax, np.array(w_norm))

    # Ranks (1 is best, descending score)
    topsis_order = np.argsort(-C)
    topsis_ranks = np.zeros(m, dtype=int)
    for rank, idx in enumerate(topsis_order, 1):
        topsis_ranks[idx] = rank

    wsm_order = np.argsort(-WSM_scores)
    wsm_ranks = np.zeros(m, dtype=int)
    for rank, idx in enumerate(wsm_order, 1):
        wsm_ranks[idx] = rank

    # Correlations between TOPSIS and WSM
    if m >= 3:
        try:
            sp_rho, _ = spearmanr(C, WSM_scores)
            kd_tau, _ = kendalltau(C, WSM_scores)
            sp_rho = round(float(sp_rho), 4) if not math.isnan(sp_rho) else 1.0
            kd_tau = round(float(kd_tau), 4) if not math.isnan(kd_tau) else 1.0
        except Exception:
            sp_rho, kd_tau = 1.0, 1.0
    else:
        sp_rho, kd_tau = 1.0, 1.0

    # Build detailed crop rank cards with plain-language explanations
    results = []
    for i in range(m):
        item = crop_evaluations[i]
        rank = int(topsis_ranks[i])
        closeness = round(float(C[i]), 4)
        wsm_s = round(float(WSM_scores[i]), 4)
        wsm_r = int(wsm_ranks[i])

        # Criteria contributions
        contributions = {}
        for j, k in enumerate(matrix_keys):
            # Proximity to ideal
            dist_worst = abs(V[i, j] - A_minus[j])
            contributions[k] = round(float(dist_worst), 4)

        explanation = generate_explanation(
            crop_name=item["crop_name"],
            rank=rank,
            criteria_values=item["criteria_values"],
            closeness=closeness
        )

        results.append({
            "crop_id": item["crop_id"],
            "crop_name": item["crop_name"],
            "category": item.get("category", ""),
            "rank": rank,
            "closeness": closeness,
            "wsm_score": wsm_s,
            "wsm_rank": wsm_r,
            "separation_ideal": round(float(S_plus[i]), 4),
            "separation_worst": round(float(S_minus[i]), 4),
            "criteria_values": item["criteria_values"],
            "contributions": contributions,
            "explanation": explanation,
            "is_excluded": item.get("is_excluded", False),
            "details": item.get("details", {})
        })

    results.sort(key=lambda x: x["rank"])

    return {
        "results": results,
        "rank_correlation": {
            "spearman": sp_rho,
            "kendall": kd_tau
        },
        "ideal_best": {matrix_keys[j]: round(float(A_plus[j]), 4) for j in range(n)},
        "ideal_worst": {matrix_keys[j]: round(float(A_minus[j]), 4) for j in range(n)}
    }


def generate_explanation(crop_name: str, rank: int, criteria_values: Dict[str, Any], closeness: float) -> str:
    ret = criteria_values.get("return", 0)
    soil = criteria_values.get("soil", 0)
    water = criteria_values.get("water", 0)
    cv = criteria_values.get("variability", 0)

    ordinal = f"{rank}{'st' if rank==1 else 'nd' if rank==2 else 'rd' if rank==3 else 'th'}"

    traits = []
    if soil >= 0.85:
        traits.append(f"exceptional soil compatibility ({soil:.2f})")
    elif soil >= 0.70:
        traits.append(f"good soil fit ({soil:.2f})")
    else:
        traits.append(f"moderate soil fit ({soil:.2f})")

    if ret >= 80000:
        traits.append(f"high net return (₹{ret:,.0f}/ha)")
    elif ret >= 40000:
        traits.append(f"steady return (₹{ret:,.0f}/ha)")
    else:
        traits.append(f"modest return (₹{ret:,.0f}/ha)")

    if water <= 450:
        traits.append(f"low water footprint ({water:.0f} mm)")
    elif water <= 800:
        traits.append(f"moderate water demand ({water:.0f} mm)")
    else:
        traits.append(f"heavy water demand ({water:.0f} mm)")

    if cv <= 0.15:
        traits.append("very stable mandi prices")
    elif cv >= 0.28:
        traits.append("higher price volatility")

    return f"Ranks {ordinal} (Closeness: {closeness:.3f}): Features {', '.join(traits)}."
