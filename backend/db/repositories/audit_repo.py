from datetime import datetime, timezone
from typing import Optional, Any, Dict, List
from db.mongo import get_db, serialize_doc


class AuditRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else get_db()

    def log(
        self,
        action: str,
        collection: str,
        user_id: Optional[str] = None,
        document_id: Optional[str] = None,
        old_val: Optional[Any] = None,
        new_val: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        record = {
            "user_id": str(user_id) if user_id else "system",
            "action": action,
            "collection": collection,
            "document_id": str(document_id) if document_id else None,
            "old": old_val,
            "new": new_val,
            "details": details or {},
            "at": datetime.now(timezone.utc)
        }
        res = self.db.audit_log.insert_one(record)
        return str(res.inserted_id)

    def list_logs(self, limit: int = 100, collection: Optional[str] = None, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = {}
        if collection:
            query["collection"] = collection
        if user_id:
            query["user_id"] = user_id
        cursor = self.db.audit_log.find(query).sort("at", -1).limit(limit)
        return [serialize_doc(d) for d in cursor]
