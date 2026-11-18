import re
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from db.mongo import get_db, serialize_doc


class CropRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else get_db()

    def list_crops(
        self,
        category: Optional[str] = None,
        season: Optional[str] = None,
        active_only: bool = True,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if active_only:
            query["active"] = True
        if category:
            query["category"] = category
        if season:
            query["seasons"] = {"$in": [season.lower()]}
        if search:
            query["name"] = {"$regex": re.escape(search.strip()), "$options": "i"}

        docs = list(self.db.crops.find(query).sort("name", 1))
        return [serialize_doc(d) for d in docs]

    def get_by_id(self, crop_id: str) -> Optional[Dict[str, Any]]:
        try:
            doc = self.db.crops.find_one({"_id": ObjectId(crop_id)})
            return serialize_doc(doc)
        except Exception:
            return None

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        escaped = re.escape(name.strip())
        doc = self.db.crops.find_one({"name": {"$regex": f"^{escaped}$", "$options": "i"}})
        return serialize_doc(doc)

    def create_crop(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "name": data["name"].strip(),
            "category": data.get("category", "Cereals"),
            "seasons": [s.lower() for s in data.get("seasons", ["kharif", "rabi"])],
            "duration_days": int(data.get("duration_days", 120)),
            "water_req_mm": float(data.get("water_req_mm", 500)),
            "labour_person_days_ha": float(data.get("labour_person_days_ha", 45)),
            "typical_yield_t_ha": float(data.get("typical_yield_t_ha", 3.5)),
            "soil": data.get("soil", {}),
            "active": data.get("active", True),
            "source_note": data.get("source_note", "Official Package of Practices"),
            "created_by": str(user_id),
            "created_at": now,
            "updated_at": now
        }
        res = self.db.crops.insert_one(doc)
        doc["_id"] = res.inserted_id
        return serialize_doc(doc)

    def update_crop(self, crop_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            update_fields = dict(data)
            update_fields["updated_at"] = datetime.now(timezone.utc)
            if "id" in update_fields:
                del update_fields["id"]
            if "_id" in update_fields:
                del update_fields["_id"]

            res = self.db.crops.find_one_and_update(
                {"_id": ObjectId(crop_id)},
                {"$set": update_fields},
                return_document=True
            )
            return serialize_doc(res)
        except Exception:
            return None

    def delete_crop(self, crop_id: str) -> bool:
        try:
            res = self.db.crops.delete_one({"_id": ObjectId(crop_id)})
            return res.deleted_count > 0
        except Exception:
            return False

    def get_economics(self, crop_id: str, season: Optional[str] = None, region: Optional[str] = None) -> Optional[Dict[str, Any]]:
        query: Dict[str, Any] = {"crop_id": str(crop_id)}
        if season:
            query["season"] = season.lower()
        if region:
            query["region"] = region
        doc = self.db.crop_economics.find_one(query, sort=[("year", -1)])
        return serialize_doc(doc)

    def list_all_economics(self) -> List[Dict[str, Any]]:
        docs = list(self.db.crop_economics.find().sort("crop_id", 1))
        return [serialize_doc(d) for d in docs]

    def upsert_economics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        filter_query = {
            "crop_id": str(data["crop_id"]),
            "region": data.get("region", "Default"),
            "season": data.get("season", "kharif").lower(),
            "year": int(data.get("year", datetime.now().year))
        }
        doc = {
            "crop_id": str(data["crop_id"]),
            "crop_name": data.get("crop_name", ""),
            "region": data.get("region", "Default"),
            "season": data.get("season", "kharif").lower(),
            "cost_per_ha": float(data.get("cost_per_ha", 30000)),
            "expected_yield_t_ha": float(data.get("expected_yield_t_ha", 3.0)),
            "msp_per_quintal": float(data.get("msp_per_quintal", 0)),
            "year": int(data.get("year", datetime.now().year)),
            "notes": data.get("notes", "")
        }
        self.db.crop_economics.update_one(filter_query, {"$set": doc}, upsert=True)
        return doc
