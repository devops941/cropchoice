from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from deps import get_current_user
from schemas import SimulationRunRequest
from db.repositories.optimizer_repo import OptimizerRepository
from db.repositories.simulation_repo import SimulationRepository
from core.simulation import run_monte_carlo_simulation

router = APIRouter(prefix="/simulations", tags=["Monte Carlo Risk Simulation"])


@router.post("", status_code=status.HTTP_201_CREATED)
def run_simulation(req: SimulationRunRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    uid = str(current_user["_id"])
    opt_repo = OptimizerRepository()
    sim_repo = SimulationRepository()

    opt = opt_repo.get_optimization(req.optimization_id, owner_id=uid)
    if not opt:
        raise HTTPException(status_code=404, detail="Optimization not found")

    allocations = opt.get("allocation", [])
    if not allocations:
        raise HTTPException(status_code=400, detail="Optimization has no active crop allocations to simulate.")

    sim_res = run_monte_carlo_simulation(
        allocations=allocations,
        n_runs=req.n_runs,
        seed=req.seed,
        method=req.method
    )

    saved = sim_repo.save_simulation({
        "optimization_id": req.optimization_id,
        "n_runs": req.n_runs,
        "seed": req.seed,
        "method": req.method,
        "stats": sim_res["stats"],
        "histogram": sim_res["histogram"],
        "risk_contribution": sim_res["risk_contribution"]
    }, owner_id=uid)

    return saved


@router.get("/by-optimization/{opt_id}")
def get_simulation_for_opt(opt_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    sim_repo = SimulationRepository()
    sim = sim_repo.get_by_optimization(opt_id, owner_id=str(current_user["_id"]))
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found for this optimization")
    return sim


@router.get("/{sim_id}")
def get_simulation(sim_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    sim_repo = SimulationRepository()
    sim = sim_repo.get_by_id(sim_id, owner_id=str(current_user["_id"]))
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim
