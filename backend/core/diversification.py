import math
from typing import List, Dict, Any


def calculate_diversification_metrics(allocations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes HHI, effective number of crops (1/HHI), and Shannon entropy
    for a portfolio land allocation.
    """
    valid_shares = [a["share"] for a in allocations if a.get("share", 0) > 0.0001]

    if not valid_shares:
        return {
            "hhi": 1.0,
            "effective_crops": 1.0,
            "entropy": 0.0,
            "diversification_rating": "Monoculture",
            "active_crops_count": 0
        }

    total_share = sum(valid_shares)
    norm_shares = [s / total_share for s in valid_shares]

    # HHI = sum(s_i^2)
    hhi = sum(s ** 2 for s in norm_shares)

    # Effective crops = 1 / HHI
    effective_crops = 1.0 / hhi if hhi > 0 else 1.0

    # Shannon Entropy = - sum(s_i * ln(s_i))
    entropy = -sum(s * math.log(s) for s in norm_shares if s > 0)

    # Qualitative Rating
    if effective_crops >= 3.5:
        rating = "High Diversification"
    elif effective_crops >= 2.2:
        rating = "Moderate Diversification"
    elif effective_crops > 1.2:
        rating = "Low Diversification / Concentrated"
    else:
        rating = "Monoculture Risk"

    return {
        "hhi": round(hhi, 4),
        "effective_crops": round(effective_crops, 2),
        "entropy": round(entropy, 4),
        "diversification_rating": rating,
        "active_crops_count": len(norm_shares)
    }
