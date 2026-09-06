from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from passlib.context import CryptContext

from database import get_db
from models import User, UserMLMapping


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# =========================
# REGISTER
# =========================
@router.post("/register")
def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    # Check if email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = pwd_context.hash(password)

    # Create new application user
    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password
    )

    db.add(new_user)

    # Generate users.id before creating ML mapping
    db.flush()

    # Find the highest ML user ID already assigned
    max_ml_id = (
        db.query(func.max(UserMLMapping.ml_user_id))
        .scalar()
    )

    # MovieLens users are 1-610
    # New application users start from 611
    if max_ml_id is None or max_ml_id < 611:
        new_ml_user_id = 611
    else:
        new_ml_user_id = max_ml_id + 1

    # Create mapping between application user and ML user
    ml_mapping = UserMLMapping(
        user_id=new_user.id,
        ml_user_id=new_ml_user_id
    )

    db.add(ml_mapping)

    # Save everything
    db.commit()

    # Refresh user object
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id,
        "ml_user_id": new_ml_user_id,
        "username": new_user.username,
        "email": new_user.email
    }


# =========================
# LOGIN
# =========================
@router.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    # Find user by email
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    if not pwd_context.verify(password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Get ML user ID
    ml_mapping = (
        db.query(UserMLMapping)
        .filter(UserMLMapping.user_id == user.id)
        .first()
    )

    ml_user_id = None

    if ml_mapping:
        ml_user_id = ml_mapping.ml_user_id

    return {
        "message": "Login successful",
        "user_id": user.id,
        "ml_user_id": ml_user_id,
        "username": user.username,
        "email": user.email
    }