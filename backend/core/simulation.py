import numpy as np
from typing import List, Dict, Any, Tuple


def run_monte_carlo_simulation(
    allocations: List[Dict[str, Any]],
    n_runs: int = 5000,
    seed: int = 42,
    yield_volatility: float = 0.15,
    method: str = "bootstrap"
) -> Dict[str, Any]:
    """
    Simulates portfolio returns under stochastic price and yield variations.
    Produces histogram distribution, VaR (5th percentile), Expected Shortfall, and P(loss).
    """
    if not allocations:
        return {
            "stats": {"mean": 0, "median": 0, "std": 0, "p_loss": 0, "p5": 0, "expected_shortfall": 0},
            "histogram": {"bins": [], "counts": []},
            "risk_contribution": {}
        }

    rng = np.random.default_rng(seed)
    active_crops = [a for a in allocations if a.get("area_ha", 0) > 0]
    n_crops = len(active_crops)

    areas = np.array([a["area_ha"] for a in active_crops])
    base_returns = np.array([a["expected_return"] / a["area_ha"] for a in active_crops])
    costs = np.array([a["cost_inr"] / a["area_ha"] for a in active_crops])
    revenues = base_returns + costs

    # Simulated returns matrix (n_runs x n_crops)
    # Price variation: lognormal with mean=1.0 and sigma=0.18
    # Yield variation: normal with mean=1.0 and sigma=yield_volatility
    price_shocks = rng.lognormal(mean=-0.5 * 0.18**2, sigma=0.18, size=(n_runs, n_crops))
    yield_shocks = rng.normal(loc=1.0, scale=yield_volatility, size=(n_runs, n_crops))
    combined_shocks = np.maximum(0.2, price_shocks * yield_shocks)

    sim_revenues = np.zeros((n_runs, n_crops))
    for j in range(n_crops):
        sim_revenues[:, j] = revenues[j] * combined_shocks[:, j]

    sim_crop_returns = sim_revenues - costs
    sim_portfolio_returns = np.dot(sim_crop_returns, areas)

    mean_ret = float(np.mean(sim_portfolio_returns))
    median_ret = float(np.median(sim_portfolio_returns))
    std_ret = float(np.std(sim_portfolio_returns))

    p_loss = float(np.sum(sim_portfolio_returns < 0) / n_runs)
    p5_ret = float(np.percentile(sim_portfolio_returns, 5))
    p95_ret = float(np.percentile(sim_portfolio_returns, 95))

    worst_5_pct = sim_portfolio_returns[sim_portfolio_returns <= p5_ret]
    expected_shortfall = float(np.mean(worst_5_pct)) if len(worst_5_pct) > 0 else p5_ret

    # Histogram calculation (25 bins)
    counts, bin_edges = np.histogram(sim_portfolio_returns, bins=25)
    histogram_bins = []
    for k in range(len(counts)):
        mid_val = (bin_edges[k] + bin_edges[k + 1]) / 2.0
        histogram_bins.append({
            "bin_min": round(float(bin_edges[k]), 0),
            "bin_max": round(float(bin_edges[k + 1]), 0),
            "mid": round(float(mid_val), 0),
            "count": int(counts[k]),
            "pct": round(float(counts[k] / n_runs) * 100.0, 2)
        })

    # Per-crop risk contribution (covariance with total portfolio return)
    risk_contributions = {}
    total_var = np.var(sim_portfolio_returns)
    for j in range(n_crops):
        c_name = active_crops[j]["crop_name"]
        crop_tot_returns = sim_crop_returns[:, j] * areas[j]
        cov = np.cov(crop_tot_returns, sim_portfolio_returns)[0, 1]
        pct_contrib = (cov / total_var * 100.0) if total_var > 0 else (100.0 / n_crops)
        risk_contributions[c_name] = round(float(max(0.0, pct_contrib)), 1)

    return {
        "stats": {
            "mean": round(mean_ret, 2),
            "median": round(median_ret, 2),
            "std": round(std_ret, 2),
            "p_loss": round(p_loss, 4),
            "p_loss_pct": round(p_loss * 100.0, 2),
            "p5_var": round(p5_ret, 2),
            "p95": round(p95_ret, 2),
            "expected_shortfall": round(expected_shortfall, 2)
        },
        "histogram": {
            "bins": histogram_bins,
            "var_threshold": round(p5_ret, 0)
        },
        "risk_contribution": risk_contributions,
        "n_runs": n_runs,
        "seed": seed,
        "method": method
    }
