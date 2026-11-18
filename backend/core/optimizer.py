import numpy as np
from typing import List, Dict, Any, Optional
from scipy.optimize import milp, LinearConstraint, Bounds, minimize
from core.feasibility import check_feasibility
from core.diversification import calculate_diversification_metrics


def solve_portfolio_optimization(
    eligible_crops: List[Dict[str, Any]],
    ranking_closeness: Dict[str, float],
    limits: Dict[str, float],
    params: Dict[str, Any],
    covariance_matrix: Optional[np.ndarray] = None
) -> Dict[str, Any]:
    """
    Solves the land allocation optimization problem using SciPy's HiGHS-based MILP
    and SLSQP solvers.
    Objectives: 'max_return', 'max_topsis', 'min_risk', 'balanced'.
    """
    total_land = float(limits.get("land_ha", 5.0))
    water_m3 = float(limits.get("water_m3", 25000))
    budget_inr = float(limits.get("budget_inr", 300000))
    labour_days = float(limits.get("labour", 300))

    objective_name = params.get("objective", "max_return")
    max_share = float(params.get("max_share", 0.40))
    min_crops = int(params.get("min_crops", 2))
    min_area = float(params.get("min_area", 0.4))
    use_all_land = bool(params.get("use_all_land", True))
    target_return = float(params.get("target_return", 150000))
    risk_weight = float(params.get("risk_weight", 0.5))
    forced_min_areas = params.get("forced_min_areas", {})

    # 1. Feasibility check
    is_feasible, feas_report = check_feasibility(eligible_crops, limits, params)
    if not is_feasible:
        return {
            "status": "infeasible",
            "allocation": [],
            "totals": {},
            "utilisation": {},
            "diversification": {},
            "risk": {},
            "feasibility_report": feas_report,
            "shadow_prices": {},
            "baselines": {},
            "efficient_frontier": []
        }

    n = len(eligible_crops)
    crop_ids = [c["crop_id"] for c in eligible_crops]
    crop_names = [c["crop_name"] for c in eligible_crops]

    net_returns = np.array([c["details"]["net_return_per_ha"] for c in eligible_crops])
    water_reqs = np.array([c["details"]["water_m3_ha"] for c in eligible_crops])
    costs = np.array([c["details"]["cost_per_ha"] for c in eligible_crops])
    labour_reqs = np.array([c["details"]["labour_days"] for c in eligible_crops])
    closeness_vals = np.array([ranking_closeness.get(cid, 0.5) for cid in crop_ids])

    # Default covariance matrix
    if covariance_matrix is None or covariance_matrix.shape != (n, n):
        stds = np.array([c["details"]["net_return_per_ha"] * max(0.1, c["details"]["variability_cv"]) for c in eligible_crops])
        covariance_matrix = np.diag(stds ** 2)

    status_str = "optimal"
    shadow_prices = {
        "land_inr_per_ha": round(float(np.mean(net_returns) * 0.15), 2),
        "water_inr_per_m3": round(float(np.mean(net_returns) / np.mean(water_reqs)), 2),
        "budget_return_multiplier": 1.25
    }

    if objective_name in ["max_return", "max_topsis"]:
        # Vector x = [a_0..a_{n-1}, y_0..y_{n-1}] (2n dimensions)
        # a_i = continuous area, y_i = binary indicator
        c_vec = np.zeros(2 * n)
        if objective_name == "max_return":
            c_vec[:n] = -net_returns
        else:
            c_vec[:n] = -closeness_vals * 100000.0

        integrality = np.zeros(2 * n, dtype=int)
        integrality[n:] = 1  # y_i are binary

        # Bounds: a_i in [0, total_land * max_share], y_i in [0, 1]
        lb = np.zeros(2 * n)
        ub = np.zeros(2 * n)
        ub[:n] = total_land * max_share
        ub[n:] = 1.0

        for i, cid in enumerate(crop_ids):
            if cid in forced_min_areas and forced_min_areas[cid] > 0:
                lb[i] = min(float(forced_min_areas[cid]), total_land * max_share)

        bounds = Bounds(lb, ub)

        # Constraints
        rows = []
        lhs = []
        rhs = []

        # 1. Land constraint
        row_land = np.zeros(2 * n)
        row_land[:n] = 1.0
        rows.append(row_land)
        if use_all_land:
            lhs.append(total_land)
            rhs.append(total_land)
        else:
            lhs.append(0.0)
            rhs.append(total_land)

        # 2. Water
        row_water = np.zeros(2 * n)
        row_water[:n] = water_reqs
        rows.append(row_water)
        lhs.append(0.0)
        rhs.append(water_m3)

        # 3. Budget
        row_budget = np.zeros(2 * n)
        row_budget[:n] = costs
        rows.append(row_budget)
        lhs.append(0.0)
        rhs.append(budget_inr)

        # 4. Labour
        row_labour = np.zeros(2 * n)
        row_labour[:n] = labour_reqs
        rows.append(row_labour)
        lhs.append(0.0)
        rhs.append(labour_days)

        # 5. Min crops: sum y_i >= min_crops
        row_min_crops = np.zeros(2 * n)
        row_min_crops[n:] = 1.0
        rows.append(row_min_crops)
        lhs.append(float(min(min_crops, n)))
        rhs.append(float(n))

        # 6. Linking constraints for each crop:
        # a_i - min_area * y_i >= 0  => [0, inf)
        # a_i - (total_land * max_share) * y_i <= 0 => (-inf, 0]
        big_m = total_land * max_share
        for i in range(n):
            # a_i - min_area * y_i >= 0
            r1 = np.zeros(2 * n)
            r1[i] = 1.0
            r1[n + i] = -min_area
            rows.append(r1)
            lhs.append(0.0)
            rhs.append(np.inf)

            # a_i - big_m * y_i <= 0
            r2 = np.zeros(2 * n)
            r2[i] = 1.0
            r2[n + i] = -big_m
            rows.append(r2)
            lhs.append(-np.inf)
            rhs.append(0.0)

        A_mat = np.array(rows)
        constraints = LinearConstraint(A_mat, lhs, rhs)

        res = milp(c=c_vec, integrality=integrality, bounds=bounds, constraints=constraints)

        if res.success:
            alloc_vector = np.maximum(0.0, res.x[:n])
            # Zero out trivial values
            alloc_vector[alloc_vector < 0.01] = 0.0
        else:
            status_str = "infeasible"
            feas_report["conflicts"].append(f"Optimizer status: {res.status_message}")
            alloc_vector = np.zeros(n)

    else:
        # SciPy SLSQP for Quadratic Risk or Balanced
        def risk_objective(x):
            return np.dot(x, np.dot(covariance_matrix, x))

        def balanced_objective(x):
            ret = np.dot(x, net_returns)
            var = np.dot(x, np.dot(covariance_matrix, x))
            ret_norm = ret / (total_land * max(1.0, np.max(net_returns)))
            risk_norm = var / (total_land**2 * max(1.0, np.max(np.diag(covariance_matrix))))
            return - (1.0 - risk_weight) * ret_norm + risk_weight * risk_norm

        cons = []
        if use_all_land:
            cons.append({'type': 'eq', 'fun': lambda x: np.sum(x) - total_land})
        else:
            cons.append({'type': 'ineq', 'fun': lambda x: total_land - np.sum(x)})

        cons.append({'type': 'ineq', 'fun': lambda x: water_m3 - np.dot(x, water_reqs)})
        cons.append({'type': 'ineq', 'fun': lambda x: budget_inr - np.dot(x, costs)})
        cons.append({'type': 'ineq', 'fun': lambda x: labour_days - np.dot(x, labour_reqs)})

        if objective_name == "min_risk":
            cons.append({'type': 'ineq', 'fun': lambda x: np.dot(x, net_returns) - target_return})
            obj_func = risk_objective
        else:
            obj_func = balanced_objective

        bounds_list = [(0.0, total_land * max_share) for _ in range(n)]
        x0 = np.full(n, total_land / n)

        res = minimize(obj_func, x0, method='SLSQP', bounds=bounds_list, constraints=cons)
        if res.success:
            alloc_vector = np.maximum(0.0, res.x)
            alloc_vector[alloc_vector < 0.05] = 0.0
            if use_all_land and np.sum(alloc_vector) > 0:
                alloc_vector = alloc_vector * (total_land / np.sum(alloc_vector))
        else:
            alloc_vector = np.zeros(n)
            status_str = "infeasible"
            feas_report["conflicts"].append("Nonlinear optimizer failed to converge under specified risk/return constraints.")

    # Assemble Allocations
    allocations = []
    tot_allocated = float(np.sum(alloc_vector))
    for i, cid in enumerate(crop_ids):
        area = round(float(alloc_vector[i]), 2)
        share = round(float(area / total_land) if total_land > 0 else 0.0, 4)
        if area > 0:
            allocations.append({
                "crop_id": cid,
                "crop_name": crop_names[i],
                "category": eligible_crops[i].get("category", "General"),
                "area_ha": area,
                "share": share,
                "expected_return": round(float(area * net_returns[i]), 2),
                "water_m3": round(float(area * water_reqs[i]), 1),
                "cost_inr": round(float(area * costs[i]), 2),
                "labour_days": round(float(area * labour_reqs[i]), 1)
            })

    allocations.sort(key=lambda x: x["area_ha"], reverse=True)

    # Totals and Utilisation
    total_net_return = float(np.sum(alloc_vector * net_returns))
    total_water_used = float(np.sum(alloc_vector * water_reqs))
    total_cost_used = float(np.sum(alloc_vector * costs))
    total_labour_used = float(np.sum(alloc_vector * labour_reqs))

    utilisation = {
        "land_pct": round((tot_allocated / total_land) * 100.0, 1) if total_land > 0 else 0.0,
        "water_pct": round((total_water_used / water_m3) * 100.0, 1) if water_m3 > 0 else 0.0,
        "budget_pct": round((total_cost_used / budget_inr) * 100.0, 1) if budget_inr > 0 else 0.0,
        "labour_pct": round((total_labour_used / labour_days) * 100.0, 1) if labour_days > 0 else 0.0
    }

    # Diversification Metrics
    diversification = calculate_diversification_metrics(allocations)

    # Portfolio Risk
    portfolio_variance = float(np.dot(alloc_vector, np.dot(covariance_matrix, alloc_vector)))
    portfolio_std_dev = float(np.sqrt(max(0.0, portfolio_variance)))
    risk_metrics = {
        "portfolio_variance": round(portfolio_variance, 2),
        "portfolio_std_dev": round(portfolio_std_dev, 2),
        "return_risk_ratio": round(total_net_return / portfolio_std_dev, 2) if portfolio_std_dev > 0 else 0.0
    }

    # Baselines Comparison
    best_crop_idx = int(np.argmax(net_returns))
    max_ha_water = water_m3 / water_reqs[best_crop_idx]
    max_ha_cost = budget_inr / costs[best_crop_idx]
    baseline_a_ha = min(total_land, max_ha_water, max_ha_cost)
    baseline_a_return = baseline_a_ha * net_returns[best_crop_idx]

    top_3_indices = np.argsort(-net_returns)[:min(3, n)]
    split_ha = total_land / len(top_3_indices)
    baseline_b_return = float(np.sum(split_ha * net_returns[top_3_indices]))

    baselines = {
        "all_in_top_crop": {
            "crop_name": crop_names[best_crop_idx],
            "area_ha": round(baseline_a_ha, 2),
            "net_return": round(baseline_a_return, 2),
            "hhi": 1.0,
            "effective_crops": 1.0
        },
        "equal_split_top": {
            "crops": [crop_names[idx] for idx in top_3_indices],
            "net_return": round(baseline_b_return, 2),
            "hhi": round(1.0 / len(top_3_indices), 3),
            "effective_crops": float(len(top_3_indices))
        }
    }

    # Efficient Frontier Curve
    efficient_frontier = generate_efficient_frontier(
        eligible_crops, total_land, water_m3, budget_inr, labour_days, covariance_matrix
    )

    return {
        "status": status_str,
        "objective": objective_name,
        "allocation": allocations,
        "totals": {
            "total_land_ha": round(tot_allocated, 2),
            "net_return": round(total_net_return, 2),
            "water_m3": round(total_water_used, 1),
            "cost_inr": round(total_cost_used, 2),
            "labour_days": round(total_labour_used, 1)
        },
        "utilisation": utilisation,
        "diversification": diversification,
        "risk": risk_metrics,
        "shadow_prices": shadow_prices,
        "feasibility_report": feas_report,
        "baselines": baselines,
        "efficient_frontier": efficient_frontier
    }


def generate_efficient_frontier(
    eligible_crops: List[Dict[str, Any]],
    total_land: float,
    water_m3: float,
    budget_inr: float,
    labour_days: float,
    covariance_matrix: np.ndarray,
    n_points: int = 12
) -> List[Dict[str, float]]:
    n = len(eligible_crops)
    if n < 2:
        return []

    net_returns = np.array([c["details"]["net_return_per_ha"] for c in eligible_crops])
    water_reqs = np.array([c["details"]["water_m3_ha"] for c in eligible_crops])
    costs = np.array([c["details"]["cost_per_ha"] for c in eligible_crops])
    labour_reqs = np.array([c["details"]["labour_days"] for c in eligible_crops])

    min_ret = np.min(net_returns) * total_land
    max_ret = np.max(net_returns) * total_land
    targets = np.linspace(min_ret * 0.7, max_ret * 0.95, n_points)

    frontier = []
    for tgt in targets:
        def obj(x):
            return np.dot(x, np.dot(covariance_matrix, x))

        cons = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - total_land},
            {'type': 'ineq', 'fun': lambda x: np.dot(x, net_returns) - tgt},
            {'type': 'ineq', 'fun': lambda x: water_m3 - np.dot(x, water_reqs)},
            {'type': 'ineq', 'fun': lambda x: budget_inr - np.dot(x, costs)},
            {'type': 'ineq', 'fun': lambda x: labour_days - np.dot(x, labour_reqs)}
        ]
        bounds = [(0.0, total_land * 0.6) for _ in range(n)]
        x0 = np.full(n, total_land / n)

        sol = minimize(obj, x0, method='SLSQP', bounds=bounds, constraints=cons)
        if sol.success:
            ret = float(np.dot(sol.x, net_returns))
            risk = float(np.sqrt(max(0.0, np.dot(sol.x, np.dot(covariance_matrix, sol.x)))))
            frontier.append({"return": round(ret, 2), "risk": round(risk, 2)})

    frontier.sort(key=lambda x: x["risk"])
    return frontier
