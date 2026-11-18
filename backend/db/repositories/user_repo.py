from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from bson import ObjectId
from db.mongo import get_db, serialize_doc
from config import get_settings


class UserRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else get_db()
        self.settings = get_settings()

    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        doc = self.db.users.find_one({"email": email.strip().lower()})
        return doc

    def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            doc = self.db.users.find_one({"_id": ObjectId(user_id)})
            return doc
        except Exception:
            return None

    def create_user(
        self,
        name: str,
        email: str,
        password_hash: str,
        role: str = "planner",
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        user_doc = {
            "name": name.strip(),
            "email": email.strip().lower(),
            "password_hash": password_hash,
            "role": role,
            "preferences": preferences or {
                "area_unit": "ha",
                "currency": "INR",
                "region": "South India"
            },
            "failed_logins": 0,
            "locked_until": None,
            "reset_token_hash": None,
            "reset_expires": None,
            "created_at": now,
            "last_login": None
        }
        res = self.db.users.insert_one(user_doc)
        user_doc["_id"] = res.inserted_id
        return user_doc

    def record_login_success(self, user_id: ObjectId):
        self.db.users.update_one(
            {"_id": user_id},
            {"$set": {"failed_logins": 0, "locked_until": None, "last_login": datetime.now(timezone.utc)}}
        )

    def record_login_failure(self, user_id: ObjectId) -> bool:
        """Increments failed_logins; if exceeds threshold, locks user for lockout minutes."""
        now = datetime.now(timezone.utc)
        user = self.db.users.find_one({"_id": user_id})
        if not user:
            return False
        failed = user.get("failed_logins", 0) + 1
        update_data: Dict[str, Any] = {"failed_logins": failed}
        locked = False
        if failed >= self.settings.MAX_FAILED_LOGINS:
            lockout_time = now + timedelta(minutes=self.settings.LOCKOUT_MINUTES)
            update_data["locked_until"] = lockout_time
            locked = True
        self.db.users.update_one({"_id": user_id}, {"$set": update_data})
        return locked

    def is_locked(self, user: Dict[str, Any]) -> bool:
        locked_until = user.get("locked_until")
        if not locked_until:
            return False
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) < locked_until

    def update_profile(self, user_id: str, name: Optional[str] = None, preferences: Optional[Dict[str, Any]] = None):
        fields = {}
        if name:
            fields["name"] = name.strip()
        if preferences:
            fields["preferences"] = preferences
        if fields:
            self.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": fields})

    def update_password(self, user_id: str, new_password_hash: str):
        self.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password_hash": new_password_hash, "reset_token_hash": None, "reset_expires": None}}
        )

    def set_reset_token(self, user_id: str, token_hash: str, expires_at: datetime):
        self.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"reset_token_hash": token_hash, "reset_expires": expires_at}}
        )

    def list_users(self) -> List[Dict[str, Any]]:
        docs = list(self.db.users.find({}, {"password_hash": 0, "reset_token_hash": 0}).sort("created_at", -1))
        return [serialize_doc(d) for d in docs]

    def set_role(self, user_id: str, role: str):
        self.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": role}})

    def toggle_lock(self, user_id: str, lock: bool):
        locked_until = (datetime.now(timezone.utc) + timedelta(days=365)) if lock else None
        self.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"locked_until": locked_until, "failed_logins": 0 if not lock else 99}}
        )
