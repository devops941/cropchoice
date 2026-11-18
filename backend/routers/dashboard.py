from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from deps import get_current_user
from db.repositories.farm_repo import FarmRepository
from db.repositories.crop_repo import CropRepository
from db.repositories.price_repo import PriceRepository
from db.repositories.ranking_repo import RankingRepository
from db.repositories.optimizer_repo import OptimizerRepository
from db.repositories.scenario_repo import ScenarioRepository

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview")
def get_dashboard_overview(
    farm_id: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    uid = str(current_user["_id"])
    farm_repo = FarmRepository()
    ranking_repo = RankingRepository()
    optimizer_repo = OptimizerRepository()
    scenario_repo = ScenarioRepository()
    crop_repo = CropRepository()
    price_repo = PriceRepository()

    farms = farm_repo.list_farms(uid)
    if not farms:
        return {
            "farm": None,
            "farms_list": [],
            "kpis": {},
            "top_ranking": [],
            "allocation": [],
            "scenarios": [],
            "data_completeness": {"score_pct": 100, "missing_items": []}
        }

    # Pick selected farm or default to first farm
    selected_farm = None
    if farm_id:
        selected_farm = next((f for f in farms if f["id"] == farm_id), None)
    if not selected_farm and farms:
        selected_farm = farms[0]

    fid = selected_farm["id"]

    # Latest ranking
    ranking = ranking_repo.get_latest_for_farm(fid, uid)
    top_ranking = ranking.get("results", [])[:5] if ranking else []

    # Latest optimization
    optimization = optimizer_repo.get_latest_for_farm(fid, uid)
    allocations = optimization.get("allocation", []) if optimization else []
    totals = optimization.get("totals", {}) if optimization else {}
    utilisation = optimization.get("utilisation", {}) if optimization else {}
    diversification = optimization.get("diversification", {}) if optimization else {}
    risk = optimization.get("risk", {}) if optimization else {}

    # Scenarios list
    scenarios = scenario_repo.list_scenarios(uid, fid)[:4]

    # Data completeness check
    all_crops = crop_repo.list_crops()
    missing_items = []
    for c in all_crops:
        cid = c["id"]
        stats = price_repo.get_crop_stats(cid)
        if stats.get("count", 0) < 12:
            missing_items.append({
                "type": "price",
                "crop_id": cid,
                "crop_name": c["name"],
                "message": f"Only {stats.get('count', 0)} price points recorded. Recommend at least 24."
            })
        if not c.get("soil", {}).get("ph"):
            missing_items.append({
                "type": "soil",
                "crop_id": cid,
                "crop_name": c["name"],
                "message": "Missing soil pH range specification."
            })

    total_checks = len(all_crops) * 2
    comp_score = max(20, int(((total_checks - len(missing_items)) / max(1, total_checks)) * 100))

    # Top crop
    top_crop_name = top_ranking[0]["crop_name"] if top_ranking else (allocations[0]["crop_name"] if allocations else "N/A")

    kpis = {
        "top_crop": top_crop_name,
        "net_return": totals.get("net_return", 0),
        "water_pct": utilisation.get("water_pct", 0),
        "budget_pct": utilisation.get("budget_pct", 0),
        "effective_crops": diversification.get("effective_crops", 1.0),
        "diversification_rating": diversification.get("diversification_rating", "N/A"),
        "portfolio_risk_std": risk.get("portfolio_std_dev", 0),
        "total_land_ha": selected_farm.get("land_ha", 5.0)
    }

    return {
        "farm": selected_farm,
        "farms_list": [{"id": f["id"], "name": f["name"], "land_ha": f["land_ha"], "season": f.get("season", "kharif")} for f in farms],
        "kpis": kpis,
        "top_ranking": top_ranking,
        "allocation": allocations,
        "totals": totals,
        "utilisation": utilisation,
        "scenarios": scenarios,
        "data_completeness": {
            "score_pct": comp_score,
            "missing_items": missing_items[:5],
            "total_issues": len(missing_items)
        }
    }
