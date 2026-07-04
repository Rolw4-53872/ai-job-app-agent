from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.schemas.schemas import UserCreate, UserResponse, Token
from app.models.models import User, Profile
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user and automatically create an empty profile."""
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system."
        )
        
    hashed_password = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create empty profile linked to user
    profile = Profile(
        user_id=user.id,
        full_name="New Applicant"
    )
    db.add(profile)
    db.commit()
    
    return user

@router.post("/token", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """OAuth2 compatible token login, retrieve JWT access token."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
        
    return {
        "access_token": create_access_token(subject=user.id),
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve details of the logged-in user."""
    return current_user
