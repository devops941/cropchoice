from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from deps import get_current_user
from schemas import RankingRunRequest
from db.repositories.farm_repo import FarmRepository
from db.repositories.crop_repo import CropRepository
from db.repositories.price_repo import PriceRepository
from db.repositories.ranking_repo import RankingRepository
from core.scoring import compute_crop_criteria
from core.topsis import run_topsis
from core.sensitivity import run_sensitivity_analysis

router = APIRouter(prefix="/rankings", tags=["TOPSIS Crop Ranking"])


@router.post("")
def run_and_save_ranking(req: RankingRunRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    uid = str(current_user["_id"])
    farm_repo = FarmRepository()
    crop_repo = CropRepository()
    price_repo = PriceRepository()
    ranking_repo = RankingRepository()

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

    ranking_res = run_topsis(evaluations, req.weights, use_wsr=req.use_wsr)

    saved = ranking_repo.save_ranking({
        "farm_id": req.farm_id,
        "farm_name": farm["name"],
        "profile_id": req.profile_id or "",
        "profile_name": req.profile_name or "Custom Weights",
        "inputs_snapshot": {"weights": req.weights, "use_wsr": req.use_wsr},
        "results": ranking_res["results"],
        "rank_correlation": ranking_res["rank_correlation"],
        "weights": req.weights
    }, owner_id=uid)

    return saved


@router.get("")
def list_rankings(farm_id: Optional[str] = Query(None), current_user: Dict[str, Any] = Depends(get_current_user)):
    repo = RankingRepository()
    return repo.list_rankings(owner_id=str(current_user["_id"]), farm_id=farm_id)


@router.get("/{ranking_id}")
def get_ranking(ranking_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    repo = RankingRepository()
    ranking = repo.get_by_id(ranking_id, owner_id=str(current_user["_id"]))
    if not ranking:
        raise HTTPException(status_code=404, detail="Ranking not found")
    return ranking


@router.post("/{ranking_id}/sensitivity")
def compute_sensitivity(ranking_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    uid = str(current_user["_id"])
    ranking_repo = RankingRepository()
    crop_repo = CropRepository()
    farm_repo = FarmRepository()
    price_repo = PriceRepository()

    ranking = ranking_repo.get_by_id(ranking_id, owner_id=uid)
    if not ranking:
        raise HTTPException(status_code=404, detail="Ranking not found")

    farm = farm_repo.get_by_id(ranking["farm_id"], owner_id=uid)
    if not farm:
        raise HTTPException(status_code=404, detail="Associated farm not found")

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

    base_weights = ranking.get("weights", {"water": 0.25, "soil": 0.25, "return": 0.25, "variability": 0.25})
    sens_res = run_sensitivity_analysis(evaluations, base_weights)

    saved = ranking_repo.save_sensitivity(ranking_id, sens_res)
    return saved
