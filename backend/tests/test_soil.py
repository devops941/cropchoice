import pytest
from core.soil import trapezoidal_membership, calculate_soil_suitability


def test_trapezoidal_membership_boundaries():
    # Inside optimum [6.0, 7.5] -> 1.0
    assert trapezoidal_membership(6.8, 5.0, 6.0, 7.5, 8.5) == 1.0
    assert trapezoidal_membership(6.0, 5.0, 6.0, 7.5, 8.5) == 1.0
    assert trapezoidal_membership(7.5, 5.0, 6.0, 7.5, 8.5) == 1.0

    # Outside absolute limits -> 0.0
    assert trapezoidal_membership(4.5, 5.0, 6.0, 7.5, 8.5) == 0.0
    assert trapezoidal_membership(9.0, 5.0, 6.0, 7.5, 8.5) == 0.0

    # Linear interpolation on left shoulder (5.5 is halfway between 5.0 and 6.0)
    assert abs(trapezoidal_membership(5.5, 5.0, 6.0, 7.5, 8.5) - 0.5) < 0.001


def test_soil_suitability_geometric_mean():
    crop_spec = {
        "ph": {"abs_min": 5.0, "opt_min": 6.0, "opt_max": 7.5, "abs_max": 8.5},
        "ec": {"abs_min": 0.0, "opt_min": 0.0, "opt_max": 2.0, "abs_max": 4.0},
        "oc": {"abs_min": 0.2, "opt_min": 0.5, "opt_max": 1.5, "abs_max": 3.0},
        "texture_suitability": {"loam": 1.0},
        "drainage_suitability": {"good": 1.0}
    }
    farm_soil = {"ph": 6.8, "ec": 0.5, "oc": 0.8, "texture": "loam", "drainage": "good"}

    overall, breakdown, is_excluded = calculate_soil_suitability(crop_spec, farm_soil)
    assert overall == 1.0
    assert not is_excluded
    assert breakdown["ph"] == 1.0
    assert breakdown["texture"] == 1.0
