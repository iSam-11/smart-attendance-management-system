from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.auth import create_access_token
from backend.app.core.security import verify_password
from backend.app.db.models.user import User
from backend.app.repositories.user_repository import get_user_by_username


def authenticate_user(
    db: Session,
    username: str,
    password: str,
) -> str:
    user: User | None = get_user_by_username(db, username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return create_access_token(
        user_id=user.id,
        role=user.role,
    )