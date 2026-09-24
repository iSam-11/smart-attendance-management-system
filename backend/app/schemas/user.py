from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool