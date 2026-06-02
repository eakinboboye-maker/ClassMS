"""
Copy this endpoint into your existing backend/app/api/auth.py.

Assumptions based on your current backend shape:
- users table has users.hashed_password.
- auth.py already has a router for /api/auth/login and /api/auth/me.
- your backend already has get_db, get_current_user, verify_password, hash_password.

Adjust import paths to match your project if needed.
This snippet avoids Pydantic v2-only validators, so it works with both Pydantic v1 and v2.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

# Use your existing imports if these paths are different:
# from app.api.deps import get_db, get_current_user
# from app.core.security import verify_password, hash_password
# from app.models.user import User


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Allow a logged-in student/user to change their own password."""

    if payload.new_password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirmation do not match",
        )

    if not getattr(current_user, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    if payload.current_password == payload.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password",
        )

    current_user.hashed_password = hash_password(payload.new_password)
    db.add(current_user)
    db.commit()

    return {"ok": True, "message": "Password changed successfully"}
