import logging
from typing import Optional, Any, Dict
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.database import Database
from config import get_settings

logger = logging.getLogger(__name__)

_mongo_client: Optional[MongoClient] = None


def get_client() -> MongoClient:
    global _mongo_client
    if _mongo_client is None:
        settings = get_settings()
        _mongo_client = MongoClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=settings.MONGODB_TIMEOUT_MS,
            appname="CropChoice2026"
        )
    return _mongo_client


def get_db(db_name: Optional[str] = None) -> Database:
    client = get_client()
    settings = get_settings()
    name = db_name or settings.MONGODB_DB_NAME
    return client[name]


def ping() -> bool:
    try:
        client = get_client()
        res = client.admin.command("ping")
        return bool(res.get("ok") == 1)
    except Exception as e:
        logger.error(f"MongoDB ping failed: {e}")
        return False


def close_client():
    global _mongo_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None


def ensure_indexes(db: Optional[Database] = None):
    """Create essential unique and search indexes for all collections."""
    if db is None:
        db = get_db()

    # users
    db.users.create_index([("email", ASCENDING)], unique=True)

    # crops
    db.crops.create_index([("name", ASCENDING)], unique=True)
    db.crops.create_index([("category", ASCENDING)])
    db.crops.create_index([("active", ASCENDING)])

    # crop_economics
    db.crop_economics.create_index(
        [("crop_id", ASCENDING), ("region", ASCENDING), ("season", ASCENDING), ("year", ASCENDING)],
        unique=True
    )

    # price_history
    db.price_history.create_index(
        [("crop_id", ASCENDING), ("market", ASCENDING), ("month", ASCENDING)],
        unique=True
    )

    # farms
    db.farms.create_index([("owner_id", ASCENDING), ("name", ASCENDING)])

    # criteria_profiles
    db.criteria_profiles.create_index([("owner_id", ASCENDING), ("name", ASCENDING)])

    # rankings
    db.rankings.create_index([("owner_id", ASCENDING), ("farm_id", ASCENDING), ("created_at", DESCENDING)])

    # optimizations
    db.optimizations.create_index([("owner_id", ASCENDING), ("farm_id", ASCENDING), ("created_at", DESCENDING)])

    # scenarios
    db.scenarios.create_index([("owner_id", ASCENDING), ("farm_id", ASCENDING)])

    # simulations
    db.simulations.create_index([("owner_id", ASCENDING), ("optimization_id", ASCENDING)])

    # audit_log
    db.audit_log.create_index([("collection", ASCENDING), ("at", DESCENDING)])
    db.audit_log.create_index([("user_id", ASCENDING)])

    # import_jobs
    db.import_jobs.create_index([("uploaded_by", ASCENDING), ("uploaded_at", DESCENDING)])

    logger.info("MongoDB indexes verified successfully.")


def serialize_doc(doc: Any) -> Any:
    """Recursively convert ObjectId and datetime into serializable JSON formats."""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        new_doc = {}
        for k, v in doc.items():
            if k == "_id":
                new_doc["id"] = str(v)
            else:
                new_doc[k] = serialize_doc(v)
        return new_doc
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, datetime):
        return doc.isoformat()
    return doc
