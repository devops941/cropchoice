from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from db.repositories.user_repo import UserRepository
from db.repositories.audit_repo import AuditRepository
from security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from schemas import (
    RegisterRequest, LoginRequest, TokenResponse, RefreshRequest,
    ChangePasswordRequest, ForgotPasswordRequest, ResetPasswordRequest
)
from deps import get_current_user
from db.mongo import serialize_doc

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest):
    user_repo = UserRepository()
    audit_repo = AuditRepository()

    existing = user_repo.find_by_email(req.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    pwd_hash = hash_password(req.password)
    user = user_repo.create_user(name=req.name, email=req.email, password_hash=pwd_hash, role="planner")
    uid = str(user["_id"])

    audit_repo.log("register", "users", user_id=uid, document_id=uid)

    access_token = create_access_token({"sub": uid, "role": "planner", "email": req.email})
    refresh_token = create_refresh_token({"sub": uid})

    user_info = serialize_doc(user)
    if "password_hash" in user_info:
        del user_info["password_hash"]

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_info
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    user_repo = UserRepository()
    audit_repo = AuditRepository()

    user = user_repo.find_by_email(req.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    if user_repo.is_locked(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked due to excessive failed logins. Try again later."
        )

    if not verify_password(req.password, user.get("password_hash", "")):
        locked = user_repo.record_login_failure(user["_id"])
        if locked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account has now been locked due to multiple failed login attempts."
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    user_repo.record_login_success(user["_id"])
    uid = str(user["_id"])
    audit_repo.log("login", "users", user_id=uid, document_id=uid)

    access_token = create_access_token({"sub": uid, "role": user.get("role", "planner"), "email": user["email"]})
    refresh_token = create_refresh_token({"sub": uid})

    user_info = serialize_doc(user)
    if "password_hash" in user_info:
        del user_info["password_hash"]

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_info
    )


@router.post("/refresh")
def refresh(req: RefreshRequest):
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token."
        )

    uid = payload.get("sub")
    user_repo = UserRepository()
    user = user_repo.get_by_id(uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    access_token = create_access_token({"sub": uid, "role": user.get("role", "planner"), "email": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    user_info = serialize_doc(current_user)
    if "password_hash" in user_info:
        del user_info["password_hash"]
    return user_info


@router.put("/me")
def update_me(data: Dict[str, Any], current_user: Dict[str, Any] = Depends(get_current_user)):
    user_repo = UserRepository()
    uid = str(current_user["_id"])
    user_repo.update_profile(uid, name=data.get("name"), preferences=data.get("preferences"))
    updated = user_repo.get_by_id(uid)
    info = serialize_doc(updated)
    if "password_hash" in info:
        del info["password_hash"]
    return info


@router.post("/change-password")
def change_password(req: ChangePasswordRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    if not verify_password(req.old_password, current_user.get("password_hash", "")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password does not match.")
    user_repo = UserRepository()
    user_repo.update_password(str(current_user["_id"]), hash_password(req.new_password))
    return {"message": "Password updated successfully."}


@router.post("/forgot")
def forgot_password(req: ForgotPasswordRequest):
    user_repo = UserRepository()
    user = user_repo.find_by_email(req.email)
    if user:
        reset_token = f"reset_{datetime.now(timezone.utc).timestamp()}"
        expires = datetime.now(timezone.utc) + timedelta(hours=2)
        user_repo.set_reset_token(str(user["_id"]), hash_password(reset_token), expires)
    return {"message": "If this email is registered, a password reset token has been generated."}


@router.post("/logout")
def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {"message": "Logged out successfully."}
