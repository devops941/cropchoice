import pytest
from core.topsis import run_topsis


def test_topsis_simple_decision():
    # Two alternatives: Crop A has higher return, lower water, better soil
    crop_evals = [
        {
            "crop_id": "c1",
            "crop_name": "Crop Excellent",
            "criteria_values": {"water": 300, "soil": 0.95, "return": 80000, "variability": 0.10}
        },
        {
            "crop_id": "c2",
            "crop_name": "Crop Poor",
            "criteria_values": {"water": 1200, "soil": 0.40, "return": 20000, "variability": 0.35}
        }
    ]
    weights = {"water": 0.25, "soil": 0.25, "return": 0.25, "variability": 0.25}
    res = run_topsis(crop_evals, weights)

    results = res["results"]
    assert len(results) == 2
    assert results[0]["crop_name"] == "Crop Excellent"
    assert results[0]["rank"] == 1
    assert results[0]["closeness"] > results[1]["closeness"]
