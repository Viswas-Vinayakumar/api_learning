from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.exc import IntegrityError
from database import SessionLocal
from models import User
from schemas import UserCreate, UserResponse, UserUpdate
from schemas import PaginatedResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ GET all users with pagination - Sorting command included

@router.get("/", response_model=PaginatedResponse[UserResponse])
def get_users(
    limit: int = 10,
    offset: int = 0,
    email: str | None = None,
    name_contains: str | None = None,
    name_startswith: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(User)

    if email:
        query = query.filter(User.email == email)

    if name_contains:
        query = query.filter(User.name.ilike(f"%{name_contains}%"))

    if name_startswith:
        query = query.filter(User.name.ilike(f"{name_startswith}%"))

    total = query.count()

    users = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_next": offset + limit < total,
        "has_prev": offset > 0,
        "data": users
    }



# ✅ POST create a new user
@router.post("/", response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    new_user = User(name=user.name, email=user.email)
    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    return new_user

# Get user by ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

# Update user by ID
@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.name is not None:
        user.name = user_update.name

    if user_update.email is not None:
        user.email = user_update.email

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    return user

# Delete user by ID
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return None

