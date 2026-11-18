from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from deps import get_current_user
from schemas import ScenarioCreateRequest
from db.repositories.farm_repo import FarmRepository
from db.repositories.crop_repo import CropRepository
from db.repositories.price_repo import PriceRepository
from db.repositories.ranking_repo import RankingRepository
from db.repositories.optimizer_repo import OptimizerRepository
from db.repositories.scenario_repo import ScenarioRepository
from core.scenarios import run_scenario

router = APIRouter(prefix="/scenarios", tags=["Scenario Manager"])


@router.get("")
def list_scenarios(farm_id: Optional[str] = Query(None), current_user: Dict[str, Any] = Depends(get_current_user)):
    repo = ScenarioRepository()
    return repo.list_scenarios(owner_id=str(current_user["_id"]), farm_id=farm_id)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_and_run_scenario(req: ScenarioCreateRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    uid = str(current_user["_id"])
    farm_repo = FarmRepository()
    crop_repo = CropRepository()
    price_repo = PriceRepository()
    scenario_repo = ScenarioRepository()
    optimizer_repo = OptimizerRepository()

    farm = farm_repo.get_by_id(req.farm_id, owner_id=uid)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    crops = crop_repo.list_crops()
    all_econ = {e["crop_id"]: e for e in crop_repo.list_all_economics()}
    price_stats_map = {c["id"]: price_repo.get_crop_stats(c["id"]) for c in crops}

    limits = {
        "land_ha": farm.get("land_ha", 5.0),
        "water_m3": farm.get("water", {}).get("irrigation_m3", 25000),
        "budget_inr": farm.get("budget_inr", 350000),
        "labour": farm.get("labour_person_days", 300)
    }

    opt_params = {
        "objective": "max_return",
        "max_share": 0.40,
        "min_crops": 2,
        "min_area": 0.4,
        "use_all_land": True
    }

    scenario_res = run_scenario(
        base_farm=farm,
        crops=crops,
        economics_map=all_econ,
        price_stats_map=price_stats_map,
        criteria_weights={"water": 0.25, "soil": 0.25, "return": 0.25, "variability": 0.25},
        constraint_limits=limits,
        constraint_params=opt_params,
        modifications=req.modifications
    )

    saved = scenario_repo.save_scenario({
        "farm_id": req.farm_id,
        "farm_name": farm["name"],
        "name": req.name,
        "description": req.description,
        "base_optimization_id": req.base_optimization_id or "",
        "modifications": req.modifications,
        "result_optimization_id": "",
        "summary": scenario_res["summary"]
    }, owner_id=uid)

    return saved


@router.post("/compare")
def compare_scenarios(scenario_ids: List[str], current_user: Dict[str, Any] = Depends(get_current_user)):
    repo = ScenarioRepository()
    items = []
    for sid in scenario_ids:
        sc = repo.get_by_id(sid, owner_id=str(current_user["_id"]))
        if sc:
            items.append(sc)
    return {"scenarios": items}


@router.delete("/{scenario_id}")
def delete_scenario(scenario_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    repo = ScenarioRepository()
    success = repo.delete_scenario(scenario_id, owner_id=str(current_user["_id"]))
    if not success:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return {"message": "Scenario deleted successfully"}
