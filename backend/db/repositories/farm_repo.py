from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from db.mongo import get_db, serialize_doc


class FarmRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else get_db()

    def list_farms(self, owner_id: str) -> List[Dict[str, Any]]:
        docs = list(self.db.farms.find({"owner_id": str(owner_id)}).sort("updated_at", -1))
        return [serialize_doc(d) for d in docs]

    def get_by_id(self, farm_id: str, owner_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            query: Dict[str, Any] = {"_id": ObjectId(farm_id)}
            if owner_id:
                query["owner_id"] = str(owner_id)
            doc = self.db.farms.find_one(query)
            return serialize_doc(doc)
        except Exception:
            return None

    def create_farm(self, data: Dict[str, Any], owner_id: str) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "owner_id": str(owner_id),
            "name": data["name"].strip(),
            "location": data.get("location", {"state": "Tamil Nadu", "district": "Coimbatore", "lat": 11.0168, "lon": 76.9558}),
            "land_ha": float(data.get("land_ha", 5.0)),
            "season": data.get("season", "kharif").lower(),
            "soil": {
                "ph": float(data.get("soil", {}).get("ph", 6.8)),
                "ec": float(data.get("soil", {}).get("ec", 0.6)),
                "oc": float(data.get("soil", {}).get("oc", 0.75)),
                "n": float(data.get("soil", {}).get("n", 280)),
                "p": float(data.get("soil", {}).get("p", 22)),
                "k": float(data.get("soil", {}).get("k", 310)),
                "texture": data.get("soil", {}).get("texture", "loam"),
                "drainage": data.get("soil", {}).get("drainage", "good")
            },
            "water": {
                "rainfall_mm": float(data.get("water", {}).get("rainfall_mm", 650)),
                "effective_rainfall_pct": float(data.get("water", {}).get("effective_rainfall_pct", 70)),
                "irrigation_m3": float(data.get("water", {}).get("irrigation_m3", 18000))
            },
            "budget_inr": float(data.get("budget_inr", 350000)),
            "labour_person_days": float(data.get("labour_person_days", 300)),
            "created_at": now,
            "updated_at": now
        }
        res = self.db.farms.insert_one(doc)
        doc["_id"] = res.inserted_id
        return serialize_doc(doc)

    def update_farm(self, farm_id: str, data: Dict[str, Any], owner_id: str) -> Optional[Dict[str, Any]]:
        try:
            update_fields = dict(data)
            update_fields["updated_at"] = datetime.now(timezone.utc)
            if "id" in update_fields:
                del update_fields["id"]
            if "_id" in update_fields:
                del update_fields["_id"]
            if "owner_id" in update_fields:
                del update_fields["owner_id"]

            res = self.db.farms.find_one_and_update(
                {"_id": ObjectId(farm_id), "owner_id": str(owner_id)},
                {"$set": update_fields},
                return_document=True
            )
            return serialize_doc(res)
        except Exception:
            return None

    def delete_farm(self, farm_id: str, owner_id: str) -> bool:
        try:
            res = self.db.farms.delete_one({"_id": ObjectId(farm_id), "owner_id": str(owner_id)})
            return res.deleted_count > 0
        except Exception:
            return False
