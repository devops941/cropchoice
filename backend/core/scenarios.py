from typing import List, Dict, Any
from core.scoring import compute_crop_criteria
from core.topsis import run_topsis
from core.optimizer import solve_portfolio_optimization


def run_scenario(
    base_farm: Dict[str, Any],
    crops: List[Dict[str, Any]],
    economics_map: Dict[str, Dict[str, Any]],
    price_stats_map: Dict[str, Dict[str, Any]],
    criteria_weights: Dict[str, float],
    constraint_limits: Dict[str, float],
    constraint_params: Dict[str, Any],
    modifications: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Applies scenario modifications (drought, price shock, budget change)
    and re-runs scoring, ranking, and optimization.
    """
    # 1. Modify farm water
    farm = dict(base_farm)
    farm["water"] = dict(base_farm.get("water", {}))
    farm_rainfall = float(farm["water"].get("rainfall_mm", 600))
    farm_irrigation = float(farm["water"].get("irrigation_m3", 15000))

    rainfall_pct = float(modifications.get("rainfall_pct", 0.0))  # e.g. -30
    irrigation_pct = float(modifications.get("irrigation_pct", 0.0))  # e.g. -20
    budget_pct = float(modifications.get("budget_pct", 0.0))
    land_pct = float(modifications.get("land_pct", 0.0))
    price_pct = float(modifications.get("price_pct", 0.0))  # e.g. -25
    use_msp_support = bool(modifications.get("msp_support", False))

    farm["water"]["rainfall_mm"] = max(50.0, farm_rainfall * (1.0 + rainfall_pct / 100.0))
    farm["water"]["irrigation_m3"] = max(1000.0, farm_irrigation * (1.0 + irrigation_pct / 100.0))

    # 2. Modify limits
    limits = dict(constraint_limits)
    limits["water_m3"] = max(1000.0, float(limits.get("water_m3", 25000)) * (1.0 + irrigation_pct / 100.0))
    limits["budget_inr"] = max(10000.0, float(limits.get("budget_inr", 300000)) * (1.0 + budget_pct / 100.0))
    limits["land_ha"] = max(0.5, float(limits.get("land_ha", 5.0)) * (1.0 + land_pct / 100.0))

    # 3. Modify crop prices
    modified_prices = {}
    for cid, stats in price_stats_map.items():
        st = dict(stats)
        st["mean_price"] = float(st.get("mean_price", 2500)) * (1.0 + price_pct / 100.0)
        modified_prices[cid] = st

    # 4. Evaluate crops under modified scenario
    evaluations = []
    for crop in crops:
        cid = crop.get("id") or str(crop.get("_id", ""))
        econ = economics_map.get(cid)
        p_stats = modified_prices.get(cid)
        eval_item = compute_crop_criteria(
            crop, farm, econ, p_stats, use_msp_floor=use_msp_support
        )
        evaluations.append(eval_item)

    # 5. TOPSIS Ranking
    ranking_res = run_topsis(evaluations, criteria_weights)
    closeness_map = {r["crop_id"]: r["closeness"] for r in ranking_res["results"]}

    # 6. Optimize
    eligible = [e for e in evaluations if not e.get("is_excluded", False)]
    opt_res = solve_portfolio_optimization(
        eligible, closeness_map, limits, constraint_params
    )

    top_crops = [a["crop_name"] for a in opt_res.get("allocation", [])[:3]]

    summary = {
        "status": opt_res.get("status", "optimal"),
        "net_return": opt_res.get("totals", {}).get("net_return", 0),
        "water_m3": opt_res.get("totals", {}).get("water_m3", 0),
        "cost_inr": opt_res.get("totals", {}).get("cost_inr", 0),
        "risk_std_dev": opt_res.get("risk", {}).get("portfolio_std_dev", 0),
        "effective_crops": opt_res.get("diversification", {}).get("effective_crops", 1.0),
        "top_crops": top_crops,
        "utilisation": opt_res.get("utilisation", {})
    }

    return {
        "summary": summary,
        "ranking_results": ranking_res["results"],
        "optimization": opt_res,
        "limits": limits
    }
