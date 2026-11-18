from typing import List, Dict, Any, Tuple


def check_feasibility(
    eligible_crops: List[Dict[str, Any]],
    limits: Dict[str, float],
    params: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    """
    Evaluates physical and operational feasibility before solving the LP/MILP.
    If conflicts are present, tests constraint relaxation and produces clear diagnostic messages.
    """
    total_land = float(limits.get("land_ha", 5.0))
    water_m3 = float(limits.get("water_m3", 25000))
    budget_inr = float(limits.get("budget_inr", 300000))
    labour_days = float(limits.get("labour", 300))

    min_crops = int(params.get("min_crops", 2))
    max_share = float(params.get("max_share", 0.40))
    min_area = float(params.get("min_area", 0.5))
    use_all_land = bool(params.get("use_all_land", True))

    n_eligible = len(eligible_crops)
    conflicts = []
    relaxation_hints = []

    # 1. Eligible crops count
    if n_eligible < min_crops:
        conflicts.append(f"Required at least {min_crops} crops, but only {n_eligible} crops are eligible after soil/season filtering.")
        relaxation_hints.append(f"Lower min_crops to {n_eligible} or adjust soil exclusion threshold.")

    # 2. Diversification geometry check: if use_all_land, max_share * n_eligible >= 1.0
    if use_all_land and (max_share * n_eligible) < 1.0:
        conflicts.append(
            f"Cannot allocate 100% land with max share {int(max_share*100)}% across {n_eligible} crops. "
            f"Maximum achievable is {int(max_share * n_eligible * 100)}%."
        )
        required_share = round(1.0 / max(1, n_eligible), 2)
        relaxation_hints.append(f"Increase max_share to at least {required_share:.2f} or select more crops.")

    # 3. Minimum area check
    if min_crops * min_area > total_land:
        conflicts.append(f"Minimum required area ({min_crops} crops * {min_area} ha = {min_crops * min_area} ha) exceeds total farm land ({total_land} ha).")
        relaxation_hints.append(f"Decrease min_area to {round(total_land / min_crops, 2)} ha.")

    # 4. Resource requirements vs lowest cost combinations
    if eligible_crops:
        water_reqs = [c["details"]["water_m3_ha"] for c in eligible_crops]
        cost_reqs = [c["details"]["cost_per_ha"] for c in eligible_crops]
        labour_reqs = [c["details"]["labour_days"] for c in eligible_crops]

        min_water_rate = min(water_reqs)
        min_cost_rate = min(cost_reqs)
        min_labour_rate = min(labour_reqs)

        # Cheapest water allocation for total_land
        if use_all_land and (total_land * min_water_rate > water_m3):
            supported_ha = round(water_m3 / max(1.0, min_water_rate), 2)
            conflicts.append(
                f"Available water ({water_m3:,.0f} m³) supports at most {supported_ha} ha even with the lowest-water crop mix; "
                f"farm land is {total_land} ha."
            )
            relaxation_hints.append(f"Increase water availability by {int(total_land * min_water_rate - water_m3):,} m³ or uncheck 'Use All Land'.")

        if use_all_land and (total_land * min_cost_rate > budget_inr):
            supported_ha = round(budget_inr / max(1.0, min_cost_rate), 2)
            conflicts.append(
                f"Working budget (₹{budget_inr:,.0f}) is insufficient for {total_land} ha (minimum needed: ₹{total_land * min_cost_rate:,.0f})."
            )
            relaxation_hints.append(f"Increase budget by ₹{int(total_land * min_cost_rate - budget_inr):,} or allow partial land cultivation.")

        if use_all_land and (total_land * min_labour_rate > labour_days):
            supported_ha = round(labour_days / max(1.0, min_labour_rate), 2)
            conflicts.append(
                f"Available labour ({labour_days:,.0f} person-days) is below minimum required ({total_land * min_labour_rate:,.0f} person-days)."
            )
            relaxation_hints.append("Relax labour constraint or increase available labour.")

    is_feasible = len(conflicts) == 0

    return is_feasible, {
        "is_feasible": is_feasible,
        "eligible_crops_count": n_eligible,
        "conflicts": conflicts,
        "relaxation_hints": relaxation_hints
    }
