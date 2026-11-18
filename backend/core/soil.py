import math
from typing import Dict, Any, Tuple


def trapezoidal_membership(val: float, abs_min: float, opt_min: float, opt_max: float, abs_max: float) -> float:
    """
    Computes standard FAO-style trapezoidal membership score [0.0, 1.0].
    Outside [abs_min, abs_max] -> 0.0
    Inside [opt_min, opt_max] -> 1.0
    Linearly interpolated on shoulders.
    """
    if val <= abs_min or val >= abs_max:
        return 0.0
    if opt_min <= val <= opt_max:
        return 1.0
    if abs_min < val < opt_min:
        return (val - abs_min) / (opt_min - abs_min) if opt_min > abs_min else 1.0
    if opt_max < val < abs_max:
        return (abs_max - val) / (abs_max - opt_max) if abs_max > opt_max else 1.0
    return 0.0


def calculate_soil_suitability(
    crop_soil_spec: Dict[str, Any],
    farm_soil: Dict[str, Any],
    combination_rule: str = "geometric_mean"
) -> Tuple[float, Dict[str, float], bool]:
    """
    Evaluates soil suitability of a crop given the farm's soil test data.
    Returns:
      - overall_score (0.0 to 1.0)
      - breakdown dict of scores for each parameter
      - is_excluded (True if overall_score < threshold)
    """
    breakdown = {}

    # 1. pH
    ph_range = crop_soil_spec.get("ph", {"abs_min": 5.0, "opt_min": 6.0, "opt_max": 7.5, "abs_max": 8.5})
    farm_ph = float(farm_soil.get("ph", 6.8))
    breakdown["ph"] = round(trapezoidal_membership(
        farm_ph,
        float(ph_range.get("abs_min", 5.0)),
        float(ph_range.get("opt_min", 6.0)),
        float(ph_range.get("opt_max", 7.5)),
        float(ph_range.get("abs_max", 8.5))
    ), 4)

    # 2. EC (Electrical Conductivity / Salinity)
    ec_range = crop_soil_spec.get("ec", {"abs_min": 0.0, "opt_min": 0.0, "opt_max": 2.0, "abs_max": 4.0})
    farm_ec = float(farm_soil.get("ec", 0.6))
    breakdown["ec"] = round(trapezoidal_membership(
        farm_ec,
        float(ec_range.get("abs_min", 0.0)),
        float(ec_range.get("opt_min", 0.0)),
        float(ec_range.get("opt_max", 2.0)),
        float(ec_range.get("abs_max", 4.0))
    ), 4)

    # 3. Organic Carbon (OC %)
    oc_range = crop_soil_spec.get("oc", {"abs_min": 0.2, "opt_min": 0.5, "opt_max": 1.5, "abs_max": 3.0})
    farm_oc = float(farm_soil.get("oc", 0.75))
    breakdown["oc"] = round(trapezoidal_membership(
        farm_oc,
        float(oc_range.get("abs_min", 0.2)),
        float(oc_range.get("opt_min", 0.5)),
        float(oc_range.get("opt_max", 1.5)),
        float(oc_range.get("abs_max", 3.0))
    ), 4)

    # 4. Texture
    texture_scores = crop_soil_spec.get("texture_suitability", {
        "loam": 1.0, "sandy_loam": 0.9, "clay_loam": 0.85, "clay": 0.7, "sandy": 0.5
    })
    farm_texture = str(farm_soil.get("texture", "loam")).lower().replace(" ", "_")
    breakdown["texture"] = round(float(texture_scores.get(farm_texture, 0.7)), 4)

    # 5. Drainage
    drainage_scores = crop_soil_spec.get("drainage_suitability", {
        "good": 1.0, "moderate": 0.85, "poor": 0.4, "excessive": 0.6
    })
    farm_drainage = str(farm_soil.get("drainage", "good")).lower()
    breakdown["drainage"] = round(float(drainage_scores.get(farm_drainage, 0.8)), 4)

    # Combination
    scores = list(breakdown.values())
    if combination_rule == "minimum":
        # Liebig's law of the minimum
        overall = min(scores)
    else:
        # Geometric mean
        # avoid zero collapse by using small epsilon if needed, but 0 outside absolute limits is 0
        if any(s <= 0.0 for s in scores):
            overall = 0.0
        else:
            product = 1.0
            for s in scores:
                product *= s
            overall = product ** (1.0 / len(scores))

    overall = round(overall, 4)
    is_excluded = overall < 0.30

    return overall, breakdown, is_excluded
