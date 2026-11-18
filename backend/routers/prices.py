from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from deps import get_current_user
from schemas import PriceCreateRequest
from db.repositories.price_repo import PriceRepository
from db.repositories.crop_repo import CropRepository

router = APIRouter(prefix="/prices", tags=["Price History & Mandi Data"])


@router.get("")
def list_prices(
    crop_id: Optional[str] = Query(None),
    market: Optional[str] = Query(None),
    from_month: Optional[str] = Query(None),
    to_month: Optional[str] = Query(None),
    limit: int = Query(240, ge=1, le=500),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    repo = PriceRepository()
    return repo.get_prices(
        crop_id=crop_id,
        market=market,
        from_month=from_month,
        to_month=to_month,
        limit=limit
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def add_price(req: PriceCreateRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    repo = PriceRepository()
    crop_repo = CropRepository()
    crop = crop_repo.get_by_id(req.crop_id)
    cname = crop["name"] if crop else (req.crop_name or "Unknown Crop")

    data = req.model_dump()
    data["crop_name"] = cname
    added = repo.add_price(data)
    return added


@router.get("/{crop_id}/stats")
def get_price_stats(
    crop_id: str,
    months: int = Query(36, ge=6, le=120),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    repo = PriceRepository()
    return repo.get_crop_stats(crop_id, last_n_months=months)
