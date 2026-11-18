import pytest
from core.ahp import compute_ahp_weights


def test_ahp_consistent_matrix():
    # Textbook 3x3 consistent matrix
    matrix = [
        [1.0, 2.0, 4.0],
        [0.5, 1.0, 2.0],
        [0.25, 0.5, 1.0]
    ]
    criteria = ["C1", "C2", "C3"]
    weights, cr, lambda_max, is_consistent, hints = compute_ahp_weights(matrix, criteria)

    assert is_consistent
    assert cr <= 0.10
    assert abs(sum(weights.values()) - 1.0) < 0.001
    assert weights["C1"] > weights["C2"] > weights["C3"]


def test_ahp_identity_matrix():
    # Equal importance 4x4
    matrix = [
        [1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0]
    ]
    criteria = ["water", "soil", "return", "variability"]
    weights, cr, lambda_max, is_consistent, hints = compute_ahp_weights(matrix, criteria)

    assert is_consistent
    assert cr == 0.0
    for c in criteria:
        assert abs(weights[c] - 0.25) < 0.001
