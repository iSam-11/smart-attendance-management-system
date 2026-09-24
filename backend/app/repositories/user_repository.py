from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.models.user import User


def get_user_by_username(
    db: Session,
    username: str,
) -> User | None:
    statement = select(User).where(User.username == username)

    return db.execute(statement).scalar_one_or_none()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)