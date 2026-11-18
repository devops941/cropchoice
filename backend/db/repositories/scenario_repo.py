from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from db.mongo import get_db, serialize_doc


class ScenarioRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else get_db()

    def list_scenarios(self, owner_id: str, farm_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {"owner_id": str(owner_id)}
        if farm_id:
            query["farm_id"] = str(farm_id)
        docs = list(self.db.scenarios.find(query).sort("created_at", -1))
        return [serialize_doc(d) for d in docs]

    def get_by_id(self, scenario_id: str, owner_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            query: Dict[str, Any] = {"_id": ObjectId(scenario_id)}
            if owner_id:
                query["owner_id"] = str(owner_id)
            doc = self.db.scenarios.find_one(query)
            return serialize_doc(doc)
        except Exception:
            return None

    def save_scenario(self, data: Dict[str, Any], owner_id: str) -> Dict[str, Any]:
        doc = {
            "owner_id": str(owner_id),
            "farm_id": str(data["farm_id"]),
            "farm_name": data.get("farm_name", ""),
            "name": data.get("name", "Custom Scenario"),
            "description": data.get("description", ""),
            "base_optimization_id": str(data.get("base_optimization_id", "")),
            "modifications": data.get("modifications", {}),
            "result_optimization_id": str(data.get("result_optimization_id", "")),
            "summary": data.get("summary", {}),
            "created_at": datetime.now(timezone.utc)
        }
        res = self.db.scenarios.insert_one(doc)
        doc["_id"] = res.inserted_id
        return serialize_doc(doc)

    def delete_scenario(self, scenario_id: str, owner_id: str) -> bool:
        try:
            res = self.db.scenarios.delete_one({"_id": ObjectId(scenario_id), "owner_id": str(owner_id)})
            return res.deleted_count > 0
        except Exception:
            return False
