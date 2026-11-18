from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from db.mongo import get_db, serialize_doc


class RankingRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else get_db()

    def save_ranking(self, data: Dict[str, Any], owner_id: str) -> Dict[str, Any]:
        doc = {
            "owner_id": str(owner_id),
            "farm_id": str(data["farm_id"]),
            "farm_name": data.get("farm_name", ""),
            "profile_id": str(data.get("profile_id", "")),
            "profile_name": data.get("profile_name", ""),
            "method": "topsis",
            "inputs_snapshot": data.get("inputs_snapshot", {}),
            "results": data.get("results", []),
            "rank_correlation": data.get("rank_correlation", {}),
            "weights": data.get("weights", {}),
            "created_at": datetime.now(timezone.utc)
        }
        res = self.db.rankings.insert_one(doc)
        doc["_id"] = res.inserted_id
        return serialize_doc(doc)

    def get_by_id(self, ranking_id: str, owner_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            query: Dict[str, Any] = {"_id": ObjectId(ranking_id)}
            if owner_id:
                query["owner_id"] = str(owner_id)
            doc = self.db.rankings.find_one(query)
            return serialize_doc(doc)
        except Exception:
            return None

    def get_latest_for_farm(self, farm_id: str, owner_id: str) -> Optional[Dict[str, Any]]:
        try:
            doc = self.db.rankings.find_one(
                {"owner_id": str(owner_id), "farm_id": str(farm_id)},
                sort=[("created_at", -1)]
            )
            return serialize_doc(doc)
        except Exception:
            return None

    def list_rankings(self, owner_id: str, farm_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {"owner_id": str(owner_id)}
        if farm_id:
            query["farm_id"] = str(farm_id)
        docs = list(self.db.rankings.find(query).sort("created_at", -1))
        return [serialize_doc(d) for d in docs]

    def save_sensitivity(self, ranking_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        doc = {
            "ranking_id": str(ranking_id),
            "one_at_a_time": data.get("one_at_a_time", []),
            "monte_carlo": data.get("monte_carlo", {}),
            "created_at": datetime.now(timezone.utc)
        }
        self.db.sensitivity_runs.update_one(
            {"ranking_id": str(ranking_id)},
            {"$set": doc},
            upsert=True
        )
        return serialize_doc(doc)

    def get_sensitivity(self, ranking_id: str) -> Optional[Dict[str, Any]]:
        doc = self.db.sensitivity_runs.find_one({"ranking_id": str(ranking_id)})
        return serialize_doc(doc)
