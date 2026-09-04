from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import security
from ..db import get_db
from ..deps import require_role
from ..models.user import User
from ..schemas.auth import UserOut
from ..schemas.user import ROLES, UserCreate, UserUpdate

router = APIRouter(
    prefix="/api/users", tags=["users"], dependencies=[Depends(require_role("admin"))]
)


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.post("", response_model=UserOut, status_code=201)
def create_user(body: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(409, "用户名已存在")
    if body.role not in ROLES:
        raise HTTPException(422, "非法角色")
    u = User(
        username=body.username,
        name=body.name,
        role=body.role,
        password_hash=security.hash_password(body.password),
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if u is None:
        raise HTTPException(404, "用户不存在")
    if body.role is not None:
        if body.role not in ROLES:
            raise HTTPException(422, "非法角色")
        u.role = body.role
    if body.is_active is not None:
        u.is_active = body.is_active
    if body.password:
        u.password_hash = security.hash_password(body.password)
    db.commit()
    db.refresh(u)
    return u
