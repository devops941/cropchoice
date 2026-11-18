import pytest
from core.optimizer import solve_portfolio_optimization


def test_optimizer_land_allocation():
    eligible = [
        {
            "crop_id": "c1",
            "crop_name": "Maize",
            "details": {
                "net_return_per_ha": 65000,
                "water_m3_ha": 5000,
                "cost_per_ha": 30000,
                "labour_days": 35,
                "variability_cv": 0.14
            }
        },
        {
            "crop_id": "c2",
            "crop_name": "Groundnut",
            "details": {
                "net_return_per_ha": 58000,
                "water_m3_ha": 4500,
                "cost_per_ha": 35000,
                "labour_days": 40,
                "variability_cv": 0.16
            }
        },
        {
            "crop_id": "c3",
            "crop_name": "Ragi",
            "details": {
                "net_return_per_ha": 42000,
                "water_m3_ha": 3500,
                "cost_per_ha": 24000,
                "labour_days": 30,
                "variability_cv": 0.12
            }
        }
    ]

    closeness = {"c1": 0.85, "c2": 0.75, "c3": 0.65}
    limits = {"land_ha": 5.0, "water_m3": 30000, "budget_inr": 250000, "labour": 250}
    params = {"objective": "max_return", "max_share": 0.50, "min_crops": 2, "min_area": 0.5, "use_all_land": True}

    res = solve_portfolio_optimization(eligible, closeness, limits, params)

    assert res["status"] == "optimal"
    assert len(res["allocation"]) >= 2
    assert abs(res["totals"]["total_land_ha"] - 5.0) < 0.1
    # Check max share constraint
    for a in res["allocation"]:
        assert a["area_ha"] <= 5.0 * 0.50 + 0.01
