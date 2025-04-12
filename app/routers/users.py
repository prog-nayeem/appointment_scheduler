from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import User
from app.schemas.schemas import User as UserSchema
from app.utils.auth import get_current_active_user
from typing import List

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.get("/doctors", response_model=List[UserSchema])
def get_all_doctors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all doctors"""
    doctors = db.query(User).filter(User.role == "doctor", User.is_active == True).all()
    return doctors

@router.get("/{user_id}", response_model=UserSchema)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific user's information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user 