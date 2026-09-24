from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user
from backend.app.db.dependencies import get_db
from backend.app.db.models.user import User
from backend.app.schemas.auth import LoginRequest, LoginResponse
from backend.app.schemas.user import UserResponse
from backend.app.services.auth_service import authenticate_user


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post("/login", response_model=LoginResponse)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
):
    access_token = authenticate_user(
        db=db,
        username=credentials.username,
        password=credentials.password,
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
    )


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = int(current_user["sub"])

    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or inactive",
        )

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
    )