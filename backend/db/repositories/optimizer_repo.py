from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from db.mongo import get_db, serialize_doc


class OptimizerRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else get_db()

    def save_constraint_set(self, data: Dict[str, Any], owner_id: str) -> Dict[str, Any]:
        doc = {
            "owner_id": str(owner_id),
            "farm_id": str(data["farm_id"]),
            "name": data.get("name", "Default Constraints"),
            "objective": data.get("objective", "max_return"),
            "params": data.get("params", {
                "max_share": 0.4,
                "min_crops": 2,
                "max_crops": 5,
                "min_area": 0.5,
                "use_all_land": True,
                "target_return": 150000,
                "risk_weight": 0.5
            }),
            "limits": data.get("limits", {}),
            "forced_min_areas": data.get("forced_min_areas", {}),
            "excluded_crops": data.get("excluded_crops", []),
            "created_at": datetime.now(timezone.utc)
        }
        res = self.db.constraint_sets.insert_one(doc)
        doc["_id"] = res.inserted_id
        return serialize_doc(doc)

    def save_optimization(self, data: Dict[str, Any], owner_id: str) -> Dict[str, Any]:
        doc = {
            "owner_id": str(owner_id),
            "farm_id": str(data["farm_id"]),
            "farm_name": data.get("farm_name", ""),
            "constraint_set_id": str(data.get("constraint_set_id", "")),
            "ranking_id": str(data.get("ranking_id", "")),
            "status": data.get("status", "optimal"),
            "objective": data.get("objective", "max_return"),
            "allocation": data.get("allocation", []),
            "totals": data.get("totals", {}),
            "utilisation": data.get("utilisation", {}),
            "diversification": data.get("diversification", {}),
            "risk": data.get("risk", {}),
            "shadow_prices": data.get("shadow_prices", {}),
            "feasibility_report": data.get("feasibility_report", {}),
            "baselines": data.get("baselines", {}),
            "efficient_frontier": data.get("efficient_frontier", []),
            "created_at": datetime.now(timezone.utc)
        }
        res = self.db.optimizations.insert_one(doc)
        doc["_id"] = res.inserted_id
        return serialize_doc(doc)

    def get_optimization(self, opt_id: str, owner_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            query: Dict[str, Any] = {"_id": ObjectId(opt_id)}
            if owner_id:
                query["owner_id"] = str(owner_id)
            doc = self.db.optimizations.find_one(query)
            return serialize_doc(doc)
        except Exception:
            return None

    def get_latest_for_farm(self, farm_id: str, owner_id: str) -> Optional[Dict[str, Any]]:
        try:
            doc = self.db.optimizations.find_one(
                {"owner_id": str(owner_id), "farm_id": str(farm_id)},
                sort=[("created_at", -1)]
            )
            return serialize_doc(doc)
        except Exception:
            return None

    def list_optimizations(self, owner_id: str, farm_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {"owner_id": str(owner_id)}
        if farm_id:
            query["farm_id"] = str(farm_id)
        docs = list(self.db.optimizations.find(query).sort("created_at", -1))
        return [serialize_doc(d) for d in docs]
