from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import security
from ..db import get_db
from ..deps import get_current_user
from ..models.user import User
from ..schemas.auth import LoginRequest, TokenResponse, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if user is None or not security.verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "用户已禁用")
    return TokenResponse(access_token=security.create_access_token(user.id))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
