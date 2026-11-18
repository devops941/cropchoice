from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from db.mongo import get_db, serialize_doc


class CriteriaRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else get_db()

    def list_profiles(self, owner_id: str) -> List[Dict[str, Any]]:
        docs = list(self.db.criteria_profiles.find({"owner_id": str(owner_id)}).sort("created_at", -1))
        return [serialize_doc(d) for d in docs]

    def get_by_id(self, profile_id: str, owner_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            query: Dict[str, Any] = {"_id": ObjectId(profile_id)}
            if owner_id:
                query["owner_id"] = str(owner_id)
            doc = self.db.criteria_profiles.find_one(query)
            return serialize_doc(doc)
        except Exception:
            return None

    def create_profile(self, data: Dict[str, Any], owner_id: str) -> Dict[str, Any]:
        doc = {
            "owner_id": str(owner_id),
            "name": data.get("name", "Default Profile").strip(),
            "mode": data.get("mode", "direct"),  # "direct" or "ahp"
            "criteria": data.get("criteria", ["water", "soil", "return", "variability"]),
            "weights": data.get("weights", {"water": 0.25, "soil": 0.25, "return": 0.25, "variability": 0.25}),
            "ahp_matrix": data.get("ahp_matrix"),
            "ahp_cr": data.get("ahp_cr"),
            "normalization": data.get("normalization", "vector"),
            "created_at": datetime.now(timezone.utc)
        }
        res = self.db.criteria_profiles.insert_one(doc)
        doc["_id"] = res.inserted_id
        return serialize_doc(doc)

    def delete_profile(self, profile_id: str, owner_id: str) -> bool:
        try:
            res = self.db.criteria_profiles.delete_one({"_id": ObjectId(profile_id), "owner_id": str(owner_id)})
            return res.deleted_count > 0
        except Exception:
            return False
