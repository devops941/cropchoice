from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from deps import require_admin
from db.repositories.user_repo import UserRepository
from db.repositories.audit_repo import AuditRepository
from db.mongo import get_db, ping

router = APIRouter(prefix="/admin", tags=["System Administration"])


@router.get("/users")
def list_all_users(admin: Dict[str, Any] = Depends(require_admin)):
    repo = UserRepository()
    return repo.list_users()


@router.put("/users/{user_id}/role")
def set_user_role(user_id: str, data: Dict[str, str], admin: Dict[str, Any] = Depends(require_admin)):
    role = data.get("role", "planner")
    if role not in ["admin", "planner"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'admin' or 'planner'.")
    repo = UserRepository()
    repo.set_role(user_id, role)
    return {"message": f"User role updated to {role}"}


@router.put("/users/{user_id}/toggle-lock")
def toggle_user_lock(user_id: str, data: Dict[str, bool], admin: Dict[str, Any] = Depends(require_admin)):
    lock = data.get("lock", True)
    repo = UserRepository()
    repo.toggle_lock(user_id, lock)
    return {"message": f"User {'locked' if lock else 'unlocked'} successfully"}


@router.get("/audit-log")
def get_audit_log(
    limit: int = Query(100, ge=10, le=500),
    collection: Optional[str] = Query(None),
    admin: Dict[str, Any] = Depends(require_admin)
):
    repo = AuditRepository()
    return repo.list_logs(limit=limit, collection=collection)


@router.get("/system")
def get_system_health(admin: Dict[str, Any] = Depends(require_admin)):
    db = get_db()
    is_db_alive = ping()

    counts = {
        "users": db.users.count_documents({}),
        "crops": db.crops.count_documents({}),
        "prices": db.price_history.count_documents({}),
        "farms": db.farms.count_documents({}),
        "rankings": db.rankings.count_documents({}),
        "optimizations": db.optimizations.count_documents({}),
        "scenarios": db.scenarios.count_documents({}),
        "audit_logs": db.audit_log.count_documents({})
    }

    return {
        "database_connected": is_db_alive,
        "database_name": db.name,
        "collections": counts,
        "environment": "production"
    }
