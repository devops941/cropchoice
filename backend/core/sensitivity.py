import numpy as np
from typing import List, Dict, Any
from core.topsis import run_topsis


def run_sensitivity_analysis(
    crop_evaluations: List[Dict[str, Any]],
    base_weights: Dict[str, float],
    n_monte_carlo: int = 1000,
    concentration: float = 50.0,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Performs one-at-a-time weight sweeps and Dirichlet Monte Carlo rank stability analysis.
    """
    criteria_list = ["water", "soil", "return", "variability"]
    base_w = {k: base_weights.get(k, 0.25) for k in criteria_list}
    w_sum = sum(base_w.values()) or 1.0
    base_w = {k: base_w[k] / w_sum for k in criteria_list}

    base_result = run_topsis(crop_evaluations, base_w)
    base_crops = base_result["results"]
    base_top_crop = base_crops[0]["crop_name"] if base_crops else ""

    # 1. One-at-a-time sweeps & Tornado Chart data
    one_at_a_time = []
    tornado_summary = []
    sweep_points = np.linspace(0.05, 0.95, 19)

    for c in criteria_list:
        rank_records = {item["crop_name"]: [] for item in crop_evaluations}
        top_crop_history = []
        weight_flip_value = None

        for target_w in sweep_points:
            remaining_w = 1.0 - target_w
            other_criteria = [x for x in criteria_list if x != c]
            other_sum = sum(base_w[x] for x in other_criteria)

            curr_weights = {c: float(target_w)}
            for oc in other_criteria:
                if other_sum > 0:
                    curr_weights[oc] = float(remaining_w * (base_w[oc] / other_sum))
                else:
                    curr_weights[oc] = float(remaining_w / len(other_criteria))

            res = run_topsis(crop_evaluations, curr_weights)
            step_top = res["results"][0]["crop_name"] if res["results"] else ""
            top_crop_history.append({"weight": round(float(target_w), 2), "top_crop": step_top})

            if step_top != base_top_crop and weight_flip_value is None:
                weight_flip_value = round(float(target_w), 2)

            for cr in res["results"]:
                rank_records[cr["crop_name"]].append({
                    "weight": round(float(target_w), 2),
                    "rank": cr["rank"],
                    "closeness": cr["closeness"]
                })

        one_at_a_time.append({
            "criterion": c,
            "base_weight": round(base_w[c], 3),
            "flip_weight": weight_flip_value,
            "top_crop_history": top_crop_history,
            "crop_rank_trajectories": rank_records
        })

        # Calculate rank swing for base top crop
        if base_top_crop in rank_records:
            ranks = [r["rank"] for r in rank_records[base_top_crop]]
            min_r, max_r = min(ranks), max(ranks)
            tornado_summary.append({
                "criterion": c,
                "base_weight": round(base_w[c], 2),
                "min_rank": min_r,
                "max_rank": max_r,
                "rank_swing": max_r - min_r,
                "flip_threshold": weight_flip_value
            })

    # 2. Dirichlet Monte Carlo Perturbation
    rng = np.random.default_rng(seed)
    alphas = np.array([base_w[c] * concentration for c in criteria_list])
    # Prevent zero alphas
    alphas = np.clip(alphas, 0.5, 500.0)

    sampled_weights = rng.dirichlet(alphas, size=n_monte_carlo)

    num_crops = len(crop_evaluations)
    crop_names = [item["crop_name"] for item in crop_evaluations]
    rank_counts = {name: np.zeros(num_crops, dtype=int) for name in crop_names}

    top1_wins = {name: 0 for name in crop_names}

    for idx in range(n_monte_carlo):
        w_sample = {criteria_list[j]: float(sampled_weights[idx, j]) for j in range(len(criteria_list))}
        res = run_topsis(crop_evaluations, w_sample)
        for cr in res["results"]:
            c_name = cr["crop_name"]
            c_rank = cr["rank"]
            if 1 <= c_rank <= num_crops:
                rank_counts[c_name][c_rank - 1] += 1
            if c_rank == 1:
                top1_wins[c_name] += 1

    # Probability matrix
    rank_prob_matrix = []
    for name in crop_names:
        counts = rank_counts[name]
        probs = [round(float(cnt / n_monte_carlo), 4) for cnt in counts]
        mean_rank = round(float(np.sum((np.arange(1, num_crops + 1)) * (counts / n_monte_carlo))), 2)
        top1_pct = round(float(top1_wins[name] / n_monte_carlo) * 100.0, 1)

        rank_prob_matrix.append({
            "crop_name": name,
            "top1_probability_pct": top1_pct,
            "mean_rank": mean_rank,
            "rank_probabilities": probs[:6]  # Ranks 1 to 6
        })

    rank_prob_matrix.sort(key=lambda x: x["mean_rank"])
    base_top1_stability = top1_wins.get(base_top_crop, 0) / n_monte_carlo * 100.0

    return {
        "base_top_crop": base_top_crop,
        "base_top1_stability_pct": round(base_top1_stability, 1),
        "tornado_summary": tornado_summary,
        "one_at_a_time": one_at_a_time,
        "monte_carlo": {
            "n_runs": n_monte_carlo,
            "concentration": concentration,
            "seed": seed,
            "rank_probability_matrix": rank_prob_matrix
        }
    }
