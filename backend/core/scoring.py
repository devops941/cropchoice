from typing import List, Dict, Any, Optional
from core.soil import calculate_soil_suitability


def compute_crop_criteria(
    crop: Dict[str, Any],
    farm: Dict[str, Any],
    economics: Optional[Dict[str, Any]] = None,
    price_stats: Optional[Dict[str, Any]] = None,
    use_msp_floor: bool = True
) -> Dict[str, Any]:
    """
    Computes all 4 key criteria plus extra criteria for a single crop given farm profile.
    Directions:
      - water: cost (lower is better)
      - soil: benefit (higher is better)
      - return: benefit (higher is better)
      - variability: cost (lower is better)
    """
    # 1. Soil Suitability
    soil_spec = crop.get("soil", {})
    farm_soil = farm.get("soil", {})
    soil_score, soil_breakdown, is_excluded = calculate_soil_suitability(soil_spec, farm_soil)

    # 2. Water Demand & Water Stress Ratio (WSR)
    water_req_mm = float(crop.get("water_req_mm", 500))
    farm_water = farm.get("water", {})
    rainfall_mm = float(farm_water.get("rainfall_mm", 600))
    eff_rainfall_pct = float(farm_water.get("effective_rainfall_pct", 70)) / 100.0
    irrigation_m3 = float(farm_water.get("irrigation_m3", 10000))
    land_ha = max(0.1, float(farm.get("land_ha", 5.0)))

    # Total available water per hectare in mm (1 mm = 10 m3/ha)
    water_avail_mm_per_ha = (rainfall_mm * eff_rainfall_pct) + (irrigation_m3 / (land_ha * 10.0))
    wsr = water_req_mm / max(50.0, water_avail_mm_per_ha)

    # 3. Economics & Expected Return (INR/ha)
    econ = economics or {}
    cost_per_ha = float(econ.get("cost_per_ha", 35000))
    expected_yield_t_ha = float(econ.get("expected_yield_t_ha", crop.get("typical_yield_t_ha", 3.0)))
    msp_per_quintal = float(econ.get("msp_per_quintal", 0))

    # Price stats
    stats = price_stats or {}
    mean_price = float(stats.get("mean_price", 2500))
    if use_msp_floor and msp_per_quintal > mean_price:
        effective_price = msp_per_quintal
    else:
        effective_price = mean_price

    # 1 tonne = 10 quintals
    revenue_per_ha = expected_yield_t_ha * 10.0 * effective_price
    net_return_per_ha = revenue_per_ha - cost_per_ha

    # 4. Price Variability (CV = std / mean)
    variability = float(stats.get("cv", 0.18))
    if variability <= 0:
        variability = 0.15

    # Optional criteria
    labour_days = float(crop.get("labour_person_days_ha", 45))
    duration_days = int(crop.get("duration_days", 120))
    water_m3_ha = water_req_mm * 10.0
    profit_per_water = (net_return_per_ha / water_m3_ha) if water_m3_ha > 0 else 0.0

    return {
        "crop_id": crop.get("id") or str(crop.get("_id", "")),
        "crop_name": crop.get("name", "Unknown"),
        "category": crop.get("category", "General"),
        "seasons": crop.get("seasons", ["kharif"]),
        "is_excluded": is_excluded,
        "criteria_values": {
            "water": round(water_req_mm, 1),
            "wsr": round(wsr, 3),
            "soil": round(soil_score, 4),
            "return": round(net_return_per_ha, 2),
            "variability": round(variability, 4),
            "labour": round(labour_days, 1),
            "duration": duration_days,
            "profit_per_water": round(profit_per_water, 2)
        },
        "details": {
            "water_req_mm": water_req_mm,
            "water_m3_ha": water_m3_ha,
            "soil_score": soil_score,
            "soil_breakdown": soil_breakdown,
            "cost_per_ha": cost_per_ha,
            "expected_yield_t_ha": expected_yield_t_ha,
            "effective_price": effective_price,
            "revenue_per_ha": revenue_per_ha,
            "net_return_per_ha": net_return_per_ha,
            "variability_cv": variability,
            "duration_days": duration_days,
            "labour_days": labour_days
        }
    }
