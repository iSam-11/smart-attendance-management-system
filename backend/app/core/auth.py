# from datetime import datetime, timedelta, timezone

# import jwt

# from backend.app.core.config import settings


# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 60


# def create_access_token(
#     user_id: int,
#     role: str,
# ) -> str:
#     expire = datetime.now(timezone.utc) + timedelta(
#         minutes=ACCESS_TOKEN_EXPIRE_MINUTES
#     )

#     payload = {
#         "sub": str(user_id),
#         "role": role,
#         "exp": expire,
#     }

#     return jwt.encode(
#         payload,
#         settings.jwt_secret_key,
#         algorithm=ALGORITHM,
#     )




from datetime import datetime, timedelta, timezone

import jwt

from backend.app.core.config import settings


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(
    user_id: int,
    role: str,
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[ALGORITHM],
    )