from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from db.mongo import get_db, serialize_doc


class SimulationRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else get_db()

    def save_simulation(self, data: Dict[str, Any], owner_id: str) -> Dict[str, Any]:
        doc = {
            "owner_id": str(owner_id),
            "optimization_id": str(data["optimization_id"]),
            "n_runs": int(data.get("n_runs", 5000)),
            "seed": int(data.get("seed", 42)),
            "method": data.get("method", "bootstrap"),
            "stats": data.get("stats", {}),
            "histogram": data.get("histogram", {}),
            "risk_contribution": data.get("risk_contribution", {}),
            "created_at": datetime.now(timezone.utc)
        }
        res = self.db.simulations.insert_one(doc)
        doc["_id"] = res.inserted_id
        return serialize_doc(doc)

    def get_by_optimization(self, opt_id: str, owner_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            query: Dict[str, Any] = {"optimization_id": str(opt_id)}
            if owner_id:
                query["owner_id"] = str(owner_id)
            doc = self.db.simulations.find_one(query, sort=[("created_at", -1)])
            return serialize_doc(doc)
        except Exception:
            return None

    def get_by_id(self, sim_id: str, owner_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            query: Dict[str, Any] = {"_id": ObjectId(sim_id)}
            if owner_id:
                query["owner_id"] = str(owner_id)
            doc = self.db.simulations.find_one(query)
            return serialize_doc(doc)
        except Exception:
            return None
