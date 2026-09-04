from pydantic import BaseModel

ROLES = ("business", "engineer", "admin")


class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    role: str = "engineer"


class UserUpdate(BaseModel):
    role: str | None = None
    is_active: bool | None = None
    password: str | None = None
