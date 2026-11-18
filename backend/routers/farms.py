from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from deps import get_current_user
from schemas import FarmCreateRequest
from db.repositories.farm_repo import FarmRepository
from db.repositories.audit_repo import AuditRepository

router = APIRouter(prefix="/farms", tags=["Farms"])


@router.get("")
def list_farms(current_user: Dict[str, Any] = Depends(get_current_user)):
    repo = FarmRepository()
    return repo.list_farms(owner_id=str(current_user["_id"]))


@router.get("/{farm_id}")
def get_farm(farm_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    repo = FarmRepository()
    farm = repo.get_by_id(farm_id, owner_id=str(current_user["_id"]))
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm


@router.post("", status_code=status.HTTP_201_CREATED)
def create_farm(req: FarmCreateRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    repo = FarmRepository()
    audit_repo = AuditRepository()
    uid = str(current_user["_id"])

    created = repo.create_farm(req.model_dump(), owner_id=uid)
    audit_repo.log("create", "farms", user_id=uid, document_id=created["id"])
    return created


@router.put("/{farm_id}")
def update_farm(farm_id: str, data: Dict[str, Any], current_user: Dict[str, Any] = Depends(get_current_user)):
    repo = FarmRepository()
    audit_repo = AuditRepository()
    uid = str(current_user["_id"])

    updated = repo.update_farm(farm_id, data, owner_id=uid)
    if not updated:
        raise HTTPException(status_code=404, detail="Farm not found or unauthorized")
    audit_repo.log("update", "farms", user_id=uid, document_id=farm_id)
    return updated


@router.delete("/{farm_id}")
def delete_farm(farm_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    repo = FarmRepository()
    audit_repo = AuditRepository()
    uid = str(current_user["_id"])

    success = repo.delete_farm(farm_id, owner_id=uid)
    if not success:
        raise HTTPException(status_code=404, detail="Farm not found or unauthorized")
    audit_repo.log("delete", "farms", user_id=uid, document_id=farm_id)
    return {"message": "Farm deleted successfully"}
