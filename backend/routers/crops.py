from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from deps import get_current_user, require_admin
from schemas import CropCreateRequest
from db.repositories.crop_repo import CropRepository
from db.repositories.farm_repo import FarmRepository
from core.soil import calculate_soil_suitability

router = APIRouter(prefix="/crops", tags=["Crop Library"])


@router.get("")
def list_crops(
    category: Optional[str] = Query(None),
    season: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    repo = CropRepository()
    return repo.list_crops(category=category, season=season, search=search)


@router.get("/{crop_id}")
def get_crop(crop_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    repo = CropRepository()
    crop = repo.get_by_id(crop_id)
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return crop


@router.post("", status_code=status.HTTP_201_CREATED)
def create_crop(req: CropCreateRequest, admin: Dict[str, Any] = Depends(require_admin)):
    repo = CropRepository()
    existing = repo.get_by_name(req.name)
    if existing:
        raise HTTPException(status_code=400, detail="A crop with this name already exists.")
    created = repo.create_crop(req.model_dump(), user_id=str(admin["_id"]))
    return created


@router.put("/{crop_id}")
def update_crop(crop_id: str, data: Dict[str, Any], admin: Dict[str, Any] = Depends(require_admin)):
    repo = CropRepository()
    updated = repo.update_crop(crop_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Crop not found")
    return updated


@router.delete("/{crop_id}")
def delete_crop(crop_id: str, admin: Dict[str, Any] = Depends(require_admin)):
    repo = CropRepository()
    success = repo.delete_crop(crop_id)
    if not success:
        raise HTTPException(status_code=404, detail="Crop not found")
    return {"message": "Crop deleted successfully"}


@router.get("/{crop_id}/soil-fit")
def get_crop_soil_fit(
    crop_id: str,
    farm_id: str = Query(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    crop_repo = CropRepository()
    farm_repo = FarmRepository()

    crop = crop_repo.get_by_id(crop_id)
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    farm = farm_repo.get_by_id(farm_id, owner_id=str(current_user["_id"]))
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    soil_score, breakdown, is_excluded = calculate_soil_suitability(crop.get("soil", {}), farm.get("soil", {}))

    return {
        "crop_id": crop_id,
        "crop_name": crop["name"],
        "farm_id": farm_id,
        "overall_score": soil_score,
        "breakdown": breakdown,
        "is_excluded": is_excluded
    }
