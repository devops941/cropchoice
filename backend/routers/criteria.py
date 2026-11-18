from pathlib import Path
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
import yaml
from deps import get_current_user
from schemas import AhpComputeRequest, CriteriaProfileCreate
from db.repositories.criteria_repo import CriteriaRepository
from core.ahp import compute_ahp_weights

router = APIRouter(prefix="/criteria", tags=["Criteria & Weights"])
CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


@router.get("/presets")
def get_presets():
    try:
        preset_file = CONFIG_DIR / "presets.yaml"
        if preset_file.exists():
            with open(preset_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data.get("presets", [])
        raise FileNotFoundError()
    except Exception:
        return [
            {"id": "balanced", "name": "Balanced Planning", "weights": {"water": 0.25, "soil": 0.25, "return": 0.25, "variability": 0.25}},
            {"id": "water_saving", "name": "Water-Saving & Conservation", "weights": {"water": 0.50, "soil": 0.20, "return": 0.20, "variability": 0.10}},
            {"id": "profit_first", "name": "Profit Maximization", "weights": {"water": 0.10, "soil": 0.20, "return": 0.60, "variability": 0.10}},
            {"id": "low_risk", "name": "Low Risk & Price Stability", "weights": {"water": 0.20, "soil": 0.20, "return": 0.20, "variability": 0.40}}
        ]


@router.post("/ahp")
def calculate_ahp(req: AhpComputeRequest):
    try:
        weights, cr, lambda_max, is_consistent, hints = compute_ahp_weights(req.matrix, req.criteria_names)
        return {
            "weights": weights,
            "consistency_ratio": cr,
            "lambda_max": lambda_max,
            "is_consistent": is_consistent,
            "inconsistency_hints": hints
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"AHP calculation error: {str(e)}")


@router.get("/profiles")
def list_profiles(current_user: Dict[str, Any] = Depends(get_current_user)):
    repo = CriteriaRepository()
    return repo.list_profiles(owner_id=str(current_user["_id"]))


@router.post("/profiles", status_code=status.HTTP_201_CREATED)
def create_profile(req: CriteriaProfileCreate, current_user: Dict[str, Any] = Depends(get_current_user)):
    repo = CriteriaRepository()
    return repo.create_profile(req.model_dump(), owner_id=str(current_user["_id"]))


@router.delete("/profiles/{profile_id}")
def delete_profile(profile_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    repo = CriteriaRepository()
    success = repo.delete_profile(profile_id, owner_id=str(current_user["_id"]))
    if not success:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"message": "Profile deleted successfully"}
