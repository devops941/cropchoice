from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from deps import get_current_user
from schemas import OptimizationRunRequest
from db.repositories.farm_repo import FarmRepository
from db.repositories.crop_repo import CropRepository
from db.repositories.price_repo import PriceRepository
from db.repositories.ranking_repo import RankingRepository
from db.repositories.optimizer_repo import OptimizerRepository
from core.scoring import compute_crop_criteria
from core.topsis import run_topsis
from core.optimizer import solve_portfolio_optimization
from core.feasibility import check_feasibility

router = APIRouter(prefix="/optimizations", tags=["Portfolio Optimizer"])


@router.post("")
def run_optimization(req: OptimizationRunRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    uid = str(current_user["_id"])
    farm_repo = FarmRepository()
    crop_repo = CropRepository()
    price_repo = PriceRepository()
    ranking_repo = RankingRepository()
    optimizer_repo = OptimizerRepository()

    farm = farm_repo.get_by_id(req.farm_id, owner_id=uid)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    crops = crop_repo.list_crops()
    all_econ = {e["crop_id"]: e for e in crop_repo.list_all_economics()}
    price_stats_map = {c["id"]: price_repo.get_crop_stats(c["id"]) for c in crops}

    evaluations = []
    for crop in crops:
        cid = crop["id"]
        econ = all_econ.get(cid)
        p_stats = price_stats_map.get(cid)
        eval_item = compute_crop_criteria(crop, farm, econ, p_stats)
        evaluations.append(eval_item)

    # Ranking closeness
    ranking = None
    if req.ranking_id:
        ranking = ranking_repo.get_by_id(req.ranking_id, owner_id=uid)

    if not ranking:
        ranking = ranking_repo.get_latest_for_farm(req.farm_id, uid)

    if ranking:
        closeness_map = {r["crop_id"]: r["closeness"] for r in ranking.get("results", [])}
        ranking_id = ranking["id"]
    else:
        rank_res = run_topsis(evaluations, {"water": 0.25, "soil": 0.25, "return": 0.25, "variability": 0.25})
        closeness_map = {r["crop_id"]: r["closeness"] for r in rank_res["results"]}
        ranking_id = ""

    eligible_crops = [e for e in evaluations if not e.get("is_excluded", False)]

    limits = {
        "land_ha": farm.get("land_ha", 5.0),
        "water_m3": farm.get("water", {}).get("irrigation_m3", 25000),
        "budget_inr": farm.get("budget_inr", 350000),
        "labour": farm.get("labour_person_days", 300)
    }

    opt_params = {
        "objective": req.objective,
        "max_share": req.max_share,
        "min_crops": req.min_crops,
        "min_area": req.min_area,
        "use_all_land": req.use_all_land,
        "target_return": req.target_return,
        "risk_weight": req.risk_weight,
        "forced_min_areas": req.forced_min_areas
    }

    opt_result = solve_portfolio_optimization(eligible_crops, closeness_map, limits, opt_params)

    saved = optimizer_repo.save_optimization({
        "farm_id": req.farm_id,
        "farm_name": farm["name"],
        "ranking_id": ranking_id,
        "objective": req.objective,
        "status": opt_result["status"],
        "allocation": opt_result["allocation"],
        "totals": opt_result["totals"],
        "utilisation": opt_result["utilisation"],
        "diversification": opt_result["diversification"],
        "risk": opt_result["risk"],
        "shadow_prices": opt_result["shadow_prices"],
        "feasibility_report": opt_result["feasibility_report"],
        "baselines": opt_result["baselines"],
        "efficient_frontier": opt_result["efficient_frontier"]
    }, owner_id=uid)

    return saved


@router.post("/feasibility-check")
def feasibility_check(req: OptimizationRunRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    uid = str(current_user["_id"])
    farm_repo = FarmRepository()
    crop_repo = CropRepository()
    price_repo = PriceRepository()

    farm = farm_repo.get_by_id(req.farm_id, owner_id=uid)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    crops = crop_repo.list_crops()
    all_econ = {e["crop_id"]: e for e in crop_repo.list_all_economics()}
    price_stats_map = {c["id"]: price_repo.get_crop_stats(c["id"]) for c in crops}

    evaluations = []
    for crop in crops:
        cid = crop["id"]
        econ = all_econ.get(cid)
        p_stats = price_stats_map.get(cid)
        eval_item = compute_crop_criteria(crop, farm, econ, p_stats)
        evaluations.append(eval_item)

    eligible_crops = [e for e in evaluations if not e.get("is_excluded", False)]

    limits = {
        "land_ha": farm.get("land_ha", 5.0),
        "water_m3": farm.get("water", {}).get("irrigation_m3", 25000),
        "budget_inr": farm.get("budget_inr", 350000),
        "labour": farm.get("labour_person_days", 300)
    }

    is_feasible, report = check_feasibility(eligible_crops, limits, req.model_dump())
    return report


@router.get("")
def list_optimizations(farm_id: Optional[str] = Query(None), current_user: Dict[str, Any] = Depends(get_current_user)):
    repo = OptimizerRepository()
    return repo.list_optimizations(owner_id=str(current_user["_id"]), farm_id=farm_id)


@router.get("/{opt_id}")
def get_optimization(opt_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    repo = OptimizerRepository()
    opt = repo.get_optimization(opt_id, owner_id=str(current_user["_id"]))
    if not opt:
        raise HTTPException(status_code=404, detail="Optimization not found")
    return opt
