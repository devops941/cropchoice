from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from db.mongo import get_db, serialize_doc


class ImportRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else get_db()

    def create_job(self, kind: str, filename: str, uploaded_by: str) -> Dict[str, Any]:
        doc = {
            "kind": kind,  # crops, prices, economics, farms
            "filename": filename,
            "uploaded_by": str(uploaded_by),
            "uploaded_at": datetime.now(timezone.utc),
            "status": "pending",
            "n_rows": 0,
            "n_errors": 0,
            "errors": [],
            "preview_data": []
        }
        res = self.db.import_jobs.insert_one(doc)
        doc["_id"] = res.inserted_id
        return serialize_doc(doc)

    def update_job(self, job_id: str, updates: Dict[str, Any]):
        try:
            self.db.import_jobs.update_one({"_id": ObjectId(job_id)}, {"$set": updates})
        except Exception:
            pass

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        try:
            doc = self.db.import_jobs.find_one({"_id": ObjectId(job_id)})
            return serialize_doc(doc)
        except Exception:
            return None

    def list_jobs(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = {}
        if user_id:
            query["uploaded_by"] = str(user_id)
        docs = list(self.db.import_jobs.find(query).sort("uploaded_at", -1).limit(50))
        return [serialize_doc(d) for d in docs]
