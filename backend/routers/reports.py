import io
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from deps import get_current_user
from db.repositories.farm_repo import FarmRepository
from db.repositories.ranking_repo import RankingRepository
from db.repositories.optimizer_repo import OptimizerRepository
from db.repositories.scenario_repo import ScenarioRepository
from db.repositories.simulation_repo import SimulationRepository

router = APIRouter(prefix="/reports", tags=["Decision Reports"])


@router.post("/generate")
def generate_decision_report(data: Dict[str, Any], current_user: Dict[str, Any] = Depends(get_current_user)):
    uid = str(current_user["_id"])
    farm_id = data.get("farm_id")
    if not farm_id:
        raise HTTPException(status_code=400, detail="farm_id is required")

    farm_repo = FarmRepository()
    ranking_repo = RankingRepository()
    opt_repo = OptimizerRepository()
    scenario_repo = ScenarioRepository()
    sim_repo = SimulationRepository()

    farm = farm_repo.get_by_id(farm_id, owner_id=uid)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    ranking = ranking_repo.get_latest_for_farm(farm_id, uid)
    opt = opt_repo.get_latest_for_farm(farm_id, uid)
    scenarios = scenario_repo.list_scenarios(uid, farm_id)

    sim = None
    if opt:
        sim = sim_repo.get_by_optimization(opt["id"], owner_id=uid)

    report_id = f"rep_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    return {
        "report_id": report_id,
        "title": f"CropChoice Strategic Decision Report - {farm['name']}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "farm": farm,
        "ranking": ranking,
        "optimization": opt,
        "scenarios": scenarios,
        "simulation": sim,
        "disclaimer": "This report provides analytical decision support based on multi-criteria analysis and mathematical optimization. Real agronomic outcomes depend on unpredictable weather and market forces."
    }
