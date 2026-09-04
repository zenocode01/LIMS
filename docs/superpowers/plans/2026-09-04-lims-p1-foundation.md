# Plan P1-基础：项目骨架 + 认证 + RBAC + 编号服务 + 部署

- 日期：2026-09-04
- 规格：docs/superpowers/specs/2026-09-04-lims-mvp-design.md
- 对应里程碑：M1
- 工单建议：执行时开 1 张工单（如 T-005 "P1-基础"），每完成一个 Task 勾选并提交
- **执行偏差（2026-09-04）**：本机仅 Python 3.10（装 3.12 需 GitHub 镜像，网络受限）→ 版本约束降为 `>=3.10`，Dockerfile 用 `python:3.10-slim`；docker 缺失 → Task 8 冒烟改为本机 uvicorn+vite 直跑，容器链路待补跑

## Goal

交付可部署的 LIMS 基础底座：FastAPI 后端骨架、JWT 认证、三角色 RBAC、编号服务（编号规则 v2 全部格式）、React 登录页、docker compose 部署。完成后 `pytest` 全绿、`npm run build` 通过、`docker compose up` 可登录。

## Architecture

- 后端单仓 `backend/`：FastAPI + SQLAlchemy 2 + Alembic + PostgreSQL 16（测试用 SQLite）
- 前端单仓 `frontend/`：Vite + React 18 + AntD 5，登录页 + 路由守卫
- 编号服务：`numbering/sequence.py` 表（prefix, date, last_no），`take_number()` 统一出口
- 部署：`deploy/docker-compose.yml` = postgres + api + nginx（前端静态 + /api 反代）

## Tech Stack

Python 3.10+ / FastAPI / SQLAlchemy 2 / Pydantic v2 / Alembic / PyJWT / bcrypt / pytest + httpx / Node 22 / Vite / React 18 / AntD 5 / nginx / PostgreSQL 16

## Global Constraints（自规格逐字继承）

- 编号统一骨架：`前缀[-业务线][-层级][模板号]-YYYYMMDD-流水`，流水 3 位、**按日归零**
- 具体格式：报价 `Q-日期-流水`；委托 `C-日期-流水`；样品 `S-EMC-日期-流水`；任务 `T-日期-流水`；技术记录 `TR{层}-{模板号}-日期-流水`；质量记录 `QR{层}-{模板号}-日期-流水`；报告 `R-{委托单号}-{批次2位}`；设备 `EQ-流水`（静态）；客户 `CU-流水`（静态）
- 表单层级 1 位码：1=手册 2=程序文件 3=作业指导书 4=纯记录
- 角色：business / engineer / admin，RBAC 在 API 层强制（deps 依赖注入）
- 静态编号（EQ/CU）：无日期段，全局递增 3 位
- 部署内网单机；测试 DB 用 SQLite，生产 PG（模型只用跨库类型：String/Integer/DateTime/Boolean/JSON）
- 测试命令：`cd backend && python -m pytest`（Task 1 完成后配置 TestCommand: `cd backend && python -m pytest`）

## 文件结构

```
lims/
├── backend/
│   ├── pyproject.toml            # 依赖 + pytest 配置
│   ├── .env.example              # DATABASE_URL / JWT_SECRET / JWT_EXPIRE_MIN
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       ├── 0001_users.py
│   │       └── 0002_numbering_sequence.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # create_app(), /api/health
│   │   ├── config.py             # settings (pydantic-settings)
│   │   ├── db.py                 # engine/SessionLocal/Base/get_db
│   │   ├── seed.py               # 初始 admin（幂等）
│   │   ├── security.py           # hash/verify 密码, JWT
│   │   ├── deps.py               # get_current_user / require_role
│   │   ├── models/
│   │   │   ├── __init__.py       # 导出全部 model（alembic autogenerate 依赖）
│   │   │   ├── user.py           # User
│   │   │   └── sequence.py       # NumberingSequence
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           # LoginRequest / TokenResponse / UserOut
│   │   │   └── user.py           # UserCreate / UserUpdate
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           # POST /api/auth/login, GET /api/auth/me
│   │   │   └── users.py          # /api/users (admin only)
│   │   └── numbering/
│   │       ├── __init__.py
│   │       └── service.py        # take_number() + 各格式 builder
│   └── tests/
│       ├── conftest.py           # TestClient + sqlite 测试库 + seed 用户
│       ├── test_health.py
│       ├── test_security.py
│       ├── test_auth.py
│       ├── test_users_rbac.py
│       ├── test_numbering.py
│       └── test_alembic.py
├── frontend/
│   ├── package.json
│   ├── vite.config.ts            # /api → :8000 代理
│   ├── tsconfig.json
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx               # 路由 + 登录守卫
│       ├── api/client.ts         # fetch 封装 + token
│       ├── types.ts              # 共享类型（UserOut 等）
│       └── pages/
│           ├── LoginPage.tsx
│           └── DashboardPage.tsx
└── deploy/
    ├── docker-compose.yml
    ├── Dockerfile.api
    ├── Dockerfile.frontend
    └── nginx.conf
```

## Tasks

---

### Task 1: 后端骨架 + health + 测试基线

**Files**: Create `backend/pyproject.toml`, `backend/.env.example`, `backend/app/__init__.py`, `backend/app/main.py`, `backend/app/config.py`, `backend/app/db.py`, `backend/tests/test_health.py`

**Interfaces**:
- Produces: `app.main.create_app() -> FastAPI`；`app.db.Base`（DeclarativeBase）；`app.db.get_db()`（依赖）；`app.config.get_settings() -> Settings`
- Consumes: 无

**Steps**:

- [ ] 1.1 写 `backend/pyproject.toml`：

```toml
[project]
name = "lims-backend"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
  "fastapi>=0.111",
  "uvicorn[standard]>=0.30",
  "sqlalchemy>=2.0",
  "alembic>=1.13",
  "pydantic>=2.7",
  "pydantic-settings>=2.3",
  "pyjwt>=2.8",
  "bcrypt>=4.1",
  "psycopg[binary]>=3.1",
]

[project.optional-dependencies]
dev = ["pytest>=8", "httpx>=0.27"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] 1.2 写 `backend/tests/test_health.py`（先写测试）：

```python
from fastapi.testclient import TestClient
from app.main import create_app

def test_health():
    client = TestClient(create_app())
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
```

- [ ] 1.3 跑测试确认失败：`cd backend && python -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]" && python -m pytest tests/test_health.py`（预期 ImportError: app.main 不存在）

- [ ] 1.4 写 `backend/app/config.py`：

```python
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./lims.db"
    jwt_secret: str = "change-me"
    jwt_expire_min: int = 720

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

- [ ] 1.5 写 `backend/app/db.py`：

```python
from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from .config import get_settings

settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] 1.6 写 `backend/app/main.py` 和 `backend/app/__init__.py`（空）、`backend/app/.env.example`：

```python
# app/main.py
from fastapi import FastAPI

def create_app() -> FastAPI:
    app = FastAPI(title="LIMS API")

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app
```

```
# .env.example
DATABASE_URL=sqlite:///./lims.db
JWT_SECRET=change-me
JWT_EXPIRE_MIN=720
```

- [ ] 1.7 跑测试确认通过：`python -m pytest tests/test_health.py`（1 passed）

- [ ] 1.8 commit：`git add backend && git commit -m "feat(backend): 骨架+health+测试基线"`

---

### Task 2: User 模型 + Alembic 0001

**Files**: Create `backend/app/models/__init__.py`, `backend/app/models/user.py`, `backend/alembic.ini`, `backend/alembic/env.py`, `backend/alembic/versions/0001_users.py`, `backend/tests/test_alembic.py`

**Interfaces**:
- Produces: `app.models.user.User`（id, username, password_hash, name, role, is_active, created_at）；`app.models.User` 导出
- Consumes: `app.db.Base`

**Steps**:

- [ ] 2.1 写 `backend/app/models/user.py`：

```python
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from ..db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    name: Mapped[str] = mapped_column(String(64))
    role: Mapped[str] = mapped_column(String(16), default="engineer")  # business/engineer/admin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

- [ ] 2.2 写 `backend/app/models/__init__.py`：

```python
from .user import User
from .sequence import NumberingSequence  # noqa: F401  (Task 6 前会断，先只导出 User)
```

注意：Task 2 阶段 `sequence.py` 还不存在，本文件先只写 `from .user import User`；Task 6 完成后再补第二行。

- [ ] 2.3 初始化 Alembic：`cd backend && python -m alembic init alembic`，改 `alembic/env.py`：`from app.db import Base` + `target_metadata = Base.metadata`，`alembic.ini` 的 `sqlalchemy.url` 留空（env.py 从 `app.config` 读）：

```python
# alembic/env.py 关键段
from app.config import get_settings
from app.db import Base
from app import models  # noqa: F401

config.set_main_option("sqlalchemy.url", get_settings().database_url)
target_metadata = Base.metadata
```

- [ ] 2.4 手写 `backend/alembic/versions/0001_users.py`：

```python
"""users"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None

def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(64), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(128), nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("role", sa.String(16), nullable=False, server_default="engineer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_username", "users", ["username"])

def downgrade():
    op.drop_index("ix_users_username", "users")
    op.drop_table("users")
```

- [ ] 2.5 写 `backend/tests/test_alembic.py`（迁移可执行测试；测试命令从 backend 目录启动，cwd 用 `"."`）：

```python
import os
import subprocess
import sys

def test_alembic_upgrade_head(tmp_path):
    db_file = tmp_path / "alembic_test.db"
    env = {**os.environ, "DATABASE_URL": f"sqlite:///{db_file}"}
    r = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=".", env=env, capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    assert db_file.exists()
```

- [ ] 2.6 跑测试：`cd backend && python -m pytest tests/test_alembic.py`（1 passed）

- [ ] 2.7 commit：`git add backend && git commit -m "feat(backend): User 模型 + alembic 0001"`

---

### Task 3: 密码哈希 + JWT

**Files**: Create `backend/app/security.py`, `backend/tests/test_security.py`

**Interfaces**:
- Produces: `hash_password(pw: str) -> str`；`verify_password(pw: str, hash: str) -> bool`；`create_access_token(user_id: int) -> str`；`decode_token(token: str) -> dict`（过期/非法抛 `jwt.PyJWTError`）
- Consumes: `app.config.get_settings`

**Steps**:

- [ ] 3.1 写 `backend/tests/test_security.py`：

```python
import time
import pytest
import jwt
from app import security
from app.config import get_settings

def test_password_roundtrip():
    h = security.hash_password("s3cret")
    assert security.verify_password("s3cret", h)
    assert not security.verify_password("wrong", h)

def test_password_hash_not_plaintext():
    assert security.hash_password("s3cret") != "s3cret"

def test_jwt_roundtrip():
    tok = security.create_access_token(42)
    payload = security.decode_token(tok)
    assert payload["sub"] == "42"

def test_jwt_expired():
    old = security._make_token(1, exp_seconds=-10)
    with pytest.raises(jwt.ExpiredSignatureError):
        security.decode_token(old)
```

- [ ] 3.2 跑确认失败（ModuleNotFoundError: app.security）

- [ ] 3.3 写 `backend/app/security.py`：

```python
import time
from typing import Any
import bcrypt
import jwt
from .config import get_settings

def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def verify_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())

def _make_token(user_id: int, exp_seconds: int) -> str:
    s = get_settings()
    return jwt.encode(
        {"sub": str(user_id), "exp": int(time.time()) + exp_seconds},
        s.jwt_secret, algorithm="HS256",
    )

def create_access_token(user_id: int) -> str:
    return _make_token(user_id, get_settings().jwt_expire_min * 60)

def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
```

- [ ] 3.4 跑确认通过：`python -m pytest tests/test_security.py`（4 passed）

- [ ] 3.5 commit：`git add backend && git commit -m "feat(backend): bcrypt + JWT"`

---

### Task 4: 登录 + /me（含 conftest 测试基建）

**Files**: Create `backend/app/schemas/__init__.py`, `backend/app/schemas/auth.py`, `backend/app/deps.py`, `backend/app/api/__init__.py`, `backend/app/api/auth.py`, `backend/tests/conftest.py`, `backend/tests/test_auth.py`；Modify `backend/app/main.py`

**Interfaces**:
- Produces: `POST /api/auth/login {username,password} -> {access_token, token_type}`（401 失败）；`GET /api/auth/me -> UserOut`（401 无 token）；`app.deps.get_current_user`（后续所有受保护路由复用）
- Consumes: Task 2 `User`，Task 3 `security`

**Steps**:

- [ ] 4.1 写 `backend/app/schemas/auth.py`：

```python
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    username: str
    name: str
    role: str
    class Config:
        from_attributes = True
```

- [ ] 4.2 写 `backend/app/deps.py`：

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from .db import get_db
from .models.user import User
from . import security

bearer = HTTPBearer(auto_error=False)

def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "未提供凭证")
    try:
        payload = security.decode_token(creds.credentials)
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "凭证无效或过期")
    user = db.get(User, int(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "用户不存在或已禁用")
    return user
```

- [ ] 4.3 写 `backend/app/api/auth.py`：

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import get_db
from ..models.user import User
from ..schemas.auth import LoginRequest, TokenResponse, UserOut
from .. import security
from ..deps import get_current_user

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
```

- [ ] 4.4 修改 `backend/app/main.py` 挂载路由（create_app 内）：

```python
from .api.auth import router as auth_router
from .api.users import router as users_router  # Task 5 提供；本步先只挂 auth_router

app = FastAPI(title="LIMS API")
app.include_router(auth_router)
```

（users_router 在 Task 5 补挂。）

- [ ] 4.5 写 `backend/tests/conftest.py`（全测试共用基建）：

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db
from app.main import create_app
from app import models  # noqa: F401  (确保全部 model 注册到 Base.metadata, create_all 不漏表)
from app.models.user import User
from app import security

@pytest.fixture()
def db_session(tmp_path):
    url = f"sqlite:///{tmp_path}/test.db"
    eng = create_engine(url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(eng)
    Session = sessionmaker(bind=eng, expire_on_commit=False)
    s = Session()
    yield s
    s.close()

@pytest.fixture()
def client(db_session):
    app = create_app()
    def override():
        yield db_session
    app.dependency_overrides[get_db] = override
    # seed 三个角色用户
    for uname, role in [("admin", "admin"), ("biz", "business"), ("eng", "engineer")]:
        db_session.add(User(username=uname, password_hash=security.hash_password("pw"), name=uname, role=role))
    db_session.commit()
    return TestClient(app)

@pytest.fixture()
def admin_token(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "pw"})
    return r.json()["access_token"]

def auth_hdr(tok: str) -> dict:
    return {"Authorization": f"Bearer {tok}"}
```

（`auth_hdr` 是模块级工具函数，测试文件 `from conftest import auth_hdr`。）

- [ ] 4.6 写 `backend/tests/test_auth.py`：

```python
from conftest import auth_hdr

def test_login_ok(client):
    r = client.post("/api/auth/login", json={"username": "eng", "password": "pw"})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"

def test_login_bad_password(client):
    r = client.post("/api/auth/login", json={"username": "eng", "password": "nope"})
    assert r.status_code == 401

def test_me_with_token(client):
    tok = client.post("/api/auth/login", json={"username": "eng", "password": "pw"}).json()["access_token"]
    r = client.get("/api/auth/me", headers=auth_hdr(tok))
    assert r.status_code == 200
    assert r.json()["role"] == "engineer"

def test_me_without_token(client):
    assert client.get("/api/auth/me").status_code == 401
```

- [ ] 4.7 跑：`python -m pytest`（全绿，含之前任务）

- [ ] 4.8 commit：`git add backend && git commit -m "feat(backend): 登录 + /me + 测试 conftest"`

---

### Task 5: RBAC + 用户管理 + seed

**Files**: Create `backend/app/schemas/user.py`, `backend/app/api/users.py`, `backend/app/seed.py`, `backend/tests/test_users_rbac.py`；Modify `backend/app/deps.py`, `backend/app/main.py`

**Interfaces**:
- Produces: `app.deps.require_role(*roles) -> 依赖工厂`；`GET /api/users -> list[UserOut]`（admin）；`POST /api/users (UserCreate)`（admin）；`PATCH /api/users/{id} (UserUpdate: role/is_active/password?)`（admin）；`python -m app.seed`（幂等创建 admin）
- Consumes: Task 4 `get_current_user`, `UserOut`

**Steps**:

- [ ] 5.1 追加 `backend/app/deps.py`：

```python
def require_role(*roles: str):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "权限不足")
        return user
    return checker
```

- [ ] 5.2 写 `backend/app/schemas/user.py`：

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    role: str = "engineer"

class UserUpdate(BaseModel):
    role: str | None = None
    is_active: bool | None = None
    password: str | None = None
```

- [ ] 5.3 写 `backend/app/api/users.py`：

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import get_db
from ..models.user import User
from ..schemas.auth import UserOut
from ..schemas.user import UserCreate, UserUpdate
from ..deps import require_role
from .. import security

router = APIRouter(prefix="/api/users", tags=["users"], dependencies=[Depends(require_role("admin"))])

@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.post("", response_model=UserOut, status_code=201)
def create_user(body: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(409, "用户名已存在")
    if body.role not in ("business", "engineer", "admin"):
        raise HTTPException(422, "非法角色")
    u = User(username=body.username, name=body.name, role=body.role,
             password_hash=security.hash_password(body.password))
    db.add(u); db.commit(); db.refresh(u)
    return u

@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if u is None:
        raise HTTPException(404, "用户不存在")
    if body.role is not None:
        if body.role not in ("business", "engineer", "admin"):
            raise HTTPException(422, "非法角色")
        u.role = body.role
    if body.is_active is not None:
        u.is_active = body.is_active
    if body.password:
        u.password_hash = security.hash_password(body.password)
    db.commit(); db.refresh(u)
    return u
```

- [ ] 5.4 写 `backend/app/seed.py`：

```python
"""幂等创建初始 admin：python -m app.seed  （密码取 env SEED_ADMIN_PASSWORD，默认 lims-admin-1）"""
import os
from .db import SessionLocal
from .models.user import User
from . import security

def seed():
    db = SessionLocal()
    pw = os.environ.get("SEED_ADMIN_PASSWORD", "lims-admin-1")
    if not db.query(User).filter(User.username == "admin").first():
        db.add(User(username="admin", name="管理员", role="admin", password_hash=security.hash_password(pw)))
        db.commit()
        print("created admin")
    else:
        print("admin exists, skipped")

if __name__ == "__main__":
    seed()
```

- [ ] 5.5 修改 `backend/app/main.py`：`from .api.users import router as users_router` + `app.include_router(users_router)`

- [ ] 5.6 写 `backend/tests/test_users_rbac.py`：

```python
from conftest import auth_hdr

def _tok(client, u="admin"):
    return client.post("/api/auth/login", json={"username": u, "password": "pw"}).json()["access_token"]

def test_admin_list_users(client):
    r = client.get("/api/users", headers=auth_hdr(_tok(client, "admin")))
    assert r.status_code == 200 and len(r.json()) >= 3
    assert "password" not in r.json()[0]  # 不泄漏密码

def test_engineer_forbidden(client):
    r = client.get("/api/users", headers=auth_hdr(_tok(client, "eng")))
    assert r.status_code == 403

def test_business_forbidden(client):
    r = client.post("/api/users", json={"username": "x", "password": "p", "name": "x"},
                    headers=auth_hdr(_tok(client, "biz")))
    assert r.status_code == 403

def test_admin_create_and_patch(client):
    h = auth_hdr(_tok(client, "admin"))
    r = client.post("/api/users", json={"username": "eng2", "password": "p2", "name": "E2", "role": "engineer"}, headers=h)
    assert r.status_code == 201
    uid = r.json()["id"]
    r = client.patch(f"/api/users/{uid}", json={"is_active": False}, headers=h)
    assert r.json()["is_active"] is False
    # 禁用后登录 403
    assert client.post("/api/auth/login", json={"username": "eng2", "password": "p2"}).status_code == 403

def test_seed_idempotent(db_session):
    from app.seed import seed
    seed(); seed()
    from app.models.user import User
    assert db_session.query(User).filter(User.username == "admin").count() == 1
```

- [ ] 5.7 跑：`python -m pytest`（全绿）

- [ ] 5.8 commit：`git add backend && git commit -m "feat(backend): RBAC + 用户管理 + seed"`

---

### Task 6: 编号服务（编号规则 v2 全格式）

**Files**: Create `backend/app/models/sequence.py`, `backend/app/numbering/__init__.py`, `backend/app/numbering/service.py`, `backend/alembic/versions/0002_numbering_sequence.py`；Modify `backend/app/models/__init__.py`, `backend/tests/test_numbering.py`（Create）

**Interfaces**:
- Produces（`app/numbering/service.py`）：
  - `take_daily(db, prefix: str) -> int`（prefix 当日流水+1，按日归零）
  - `take_static(db, prefix: str) -> int`（全局递增，无日期）
  - `no_quote(db) -> str` → `Q-20260904-001`
  - `no_entrustment(db) -> str` → `C-20260904-001`
  - `no_sample(db, biz: str = "EMC") -> str` → `S-EMC-20260904-001`
  - `no_task(db) -> str` → `T-20260904-001`
  - `no_record(db, prefix: str, level: int, template_no: int) -> str` → `TR4-004-20250623-001`（prefix=TR/QR）
  - `no_report(db, entrust_no: str) -> str` → `R-C20260904-001-01`（委托单内批次+1）
  - `no_equipment(db) -> str` → `EQ-001`；`no_customer(db) -> str` → `CU-001`
  - `take_number(db, key: str, day: str | None = None) -> int`（底层：key 在 day（默认今天）/全局（day="static"）流水，并发安全）
- Consumes: `app.db`

**Steps**:

- [ ] 6.1 写 `backend/app/models/sequence.py`：

```python
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from ..db import Base

class NumberingSequence(Base):
    """key=前缀或业务键；date=YYYYMMDD（静态编号为 'static'）；last_no=当日/全局已发最大流水"""
    __tablename__ = "numbering_sequences"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    date: Mapped[str] = mapped_column(String(10), primary_key=True)
    last_no: Mapped[int] = mapped_column(Integer, default=0)
```

- [ ] 6.2 写 `backend/app/numbering/service.py`：

```python
from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..models.sequence import NumberingSequence

def take_number(db: Session, key: str, day: str | None = None) -> int:
    """key 在 day（默认今天）内的下一流水。PG 下用行锁防并发；SQLite 单进程天然串行。"""
    d = day or date.today().strftime("%Y%m%d")
    row = (
        db.query(NumberingSequence)
        .filter_by(key=key, date=d)
        .with_for_update()
        .first()
    )
    if row is None:
        row = NumberingSequence(key=key, date=d, last_no=0)
        db.add(row)
        db.flush()
        row = (
            db.query(NumberingSequence)
            .filter_by(key=key, date=d)
            .with_for_update()
            .first()
        )
    row.last_no += 1
    db.flush()
    return row.last_no

def take_daily(db: Session, prefix: str) -> int:
    return take_number(db, prefix)

def take_static(db: Session, prefix: str) -> int:
    return take_number(db, prefix, day="static")

def no_quote(db: Session) -> str:
    n = take_daily(db, "Q")
    return f"Q-{date.today():%Y%m%d}-{n:03d}"

def no_entrustment(db: Session) -> str:
    n = take_daily(db, "C")
    return f"C-{date.today():%Y%m%d}-{n:03d}"

def no_sample(db: Session, biz: str = "EMC") -> str:
    n = take_daily(db, f"S-{biz}")
    return f"S-{biz}-{date.today():%Y%m%d}-{n:03d}"

def no_task(db: Session) -> str:
    n = take_daily(db, "T")
    return f"T-{date.today():%Y%m%d}-{n:03d}"

def no_record(db: Session, prefix: str, level: int, template_no: int) -> str:
    assert prefix in ("TR", "QR"), f"非法记录前缀 {prefix}"
    n = take_daily(db, f"{prefix}{level}-{template_no:03d}")
    return f"{prefix}{level}-{template_no:03d}-{date.today():%Y%m%d}-{n:03d}"

def no_report(db: Session, entrust_no: str) -> str:
    n = take_number(db, f"R-{entrust_no}", day="static")
    return f"R-{entrust_no}-{n:02d}"

def no_equipment(db: Session) -> str:
    return f"EQ-{take_static(db, 'EQ'):03d}"

def no_customer(db: Session) -> str:
    return f"CU-{take_static(db, 'CU'):03d}"
```

- [ ] 6.3 修改 `backend/app/models/__init__.py` 补第二行：

```python
from .user import User
from .sequence import NumberingSequence
```

- [ ] 6.4 写 `backend/alembic/versions/0002_numbering_sequence.py`：

```python
"""numbering_sequences"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"

def upgrade():
    op.create_table(
        "numbering_sequences",
        sa.Column("key", sa.String(64), primary_key=True),
        sa.Column("date", sa.String(10), primary_key=True),
        sa.Column("last_no", sa.Integer(), nullable=False, server_default="0"),
    )

def downgrade():
    op.drop_table("numbering_sequences")
```

- [ ] 6.5 写 `backend/tests/test_numbering.py`：

```python
from datetime import date, timedelta
import pytest
from app.numbering import service as ns

def test_quote_format(db_session):
    assert ns.no_quote(db_session) == f"Q-{date.today():%Y%m%d}-001"

def test_daily_sequence_increments(db_session):
    a = ns.no_entrustment(db_session)
    b = ns.no_entrustment(db_session)
    assert a.endswith("-001") and b.endswith("-002")

def test_daily_reset(db_session):
    d1 = (date.today() - timedelta(days=1)).strftime("%Y%m%d")
    ns.take_number(db_session, "C", day=d1)
    ns.take_number(db_session, "C", day=d1)
    n = ns.take_number(db_session, "C")  # 今天
    assert n == 1

def test_sample_biz_segment(db_session):
    assert ns.no_sample(db_session) .startswith("S-EMC-")
    assert ns.no_sample(db_session, biz="SAF").startswith("S-SAF-")

def test_record_format(db_session):
    r = ns.no_record(db_session, "TR", 4, 4)
    assert r.startswith("TR4-004-") and r.endswith("-001")
    r2 = ns.no_record(db_session, "QR", 1, 1)
    assert r2.startswith("QR1-001-")

def test_record_bad_prefix(db_session):
    with pytest.raises(AssertionError):
        ns.no_record(db_session, "XX", 1, 1)

def test_report_batch_per_entrustment(db_session):
    a = ns.no_report(db_session, "C-20260904-001")
    b = ns.no_report(db_session, "C-20260904-001")
    c = ns.no_report(db_session, "C-20260904-002")
    assert a == "R-C-20260904-001-01"
    assert b == "R-C-20260904-001-02"
    assert c == "R-C-20260904-002-01"

def test_static_sequence(db_session):
    assert ns.no_equipment(db_session) == "EQ-001"
    assert ns.no_customer(db_session) == "CU-001"
    assert ns.no_equipment(db_session) == "EQ-002"
```

- [ ] 6.6 跑：`python -m pytest tests/test_numbering.py`（8 passed）；再 `python -m pytest` 全绿

- [ ] 6.7 commit：`git add backend && git commit -m "feat(backend): 编号服务 v2 全格式"`

---

### Task 7: 前端骨架 + 登录页

**Files**: Create `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`, `frontend/index.html`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/api/client.ts`, `frontend/src/pages/LoginPage.tsx`, `frontend/src/pages/DashboardPage.tsx`

**Interfaces**:
- Produces: 登录页（POST /api/auth/login，存 token，跳 /dashboard）；路由守卫（无 token 跳 /login）；`api/client.ts` 的 `apiFetch(path, opts)` 自动带 Bearer
- Consumes: Task 4 后端 API

**Steps**:

- [ ] 7.1 脚手架：`cd frontend && npm create vite@latest . -- --template react-ts`（现有目录非空时逐项确认保留已有文件）；`npm i antd react-router-dom`

- [ ] 7.2 写 `frontend/vite.config.ts`：

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { '/api': 'http://localhost:8000' },
  },
})
```

- [ ] 7.3 写 `frontend/src/api/client.ts`：

```ts
const TOKEN_KEY = 'lims_token'
export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (t: string | null) =>
  t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY)

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {}),
      ...(init.headers || {}),
    },
  })
  if (res.status === 401) {
    setToken(null)
    window.location.href = '/login'
  }
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`)
  return res.status === 204 ? (undefined as T) : res.json()
}
```

- [ ] 7.4 写 `frontend/src/pages/LoginPage.tsx`：

```tsx
import { useState } from 'react'
import { Form, Input, Button, Card, App as AntApp } from 'antd'
import { useNavigate } from 'react-router-dom'
import { apiFetch, setToken } from '../api/client'

export default function LoginPage() {
  const nav = useNavigate()
  const { message } = AntApp.useApp()
  const [busy, setBusy] = useState(false)

  const onFinish = async (v: { username: string; password: string }) => {
    setBusy(true)
    try {
      const r = await apiFetch<{ access_token: string }>('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify(v),
      })
      setToken(r.access_token)
      nav('/dashboard')
    } catch (e) {
      message.error(e instanceof Error ? e.message : '登录失败')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f0f2f5' }}>
      <Card title="LIMS 实验室信息管理系统" style={{ width: 380 }}>
        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item name="username" label="用户名" rules={[{ required: true }]}>
            <Input autoFocus />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true }]}>
            <Input.Password />
          </Form.Item>
          <Button type="primary" htmlType="submit" block loading={busy}>登录</Button>
        </Form>
      </Card>
    </div>
  )
}
```

- [ ] 7.5 写 `frontend/src/pages/DashboardPage.tsx`：

```tsx
import { useEffect, useState } from 'react'
import { Layout, Menu, Tag, Button } from 'antd'
import { apiFetch, getToken, setToken } from '../api/client'
import { useNavigate } from 'react-router-dom'
import type { UserOut } from '../types'

export default function DashboardPage() {
  const nav = useNavigate()
  const [me, setMe] = useState<UserOut | null>(null)
  useEffect(() => {
    apiFetch<UserOut>('/api/auth/me').then(setMe).catch(() => nav('/login'))
  }, [nav])
  const roleTag = { business: '业务', engineer: '工程师', admin: '管理' }
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Layout.Header style={{ display: 'flex', justifyContent: 'space-between' }}>
        <b>LIMS</b>
        <span>
          {me && <Tag color="blue">{roleTag[me.role]}：{me.name}</Tag>}
          <Button size="small" onClick={() => { setToken(null); nav('/login') }}>退出</Button>
        </span>
      </Layout.Header>
      <Layout.Content style={{ padding: 24 }}>
        <p>基础底座就绪。后续模块（客户/报价/委托/样品…）见计划 P2。</p>
      </Layout.Content>
    </Layout>
  )
}
```

- [ ] 7.6 写 `frontend/src/types.ts`：

```ts
export interface UserOut { id: number; username: string; name: string; role: 'business' | 'engineer' | 'admin' }
```

- [ ] 7.7 写 `frontend/src/App.tsx`（守卫）和 `frontend/src/main.tsx`：

```tsx
// App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider, App as AntApp } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import { getToken } from './api/client'

export default function App() {
  const guarded = (el: JSX.Element) => (getToken() ? el : <Navigate to="/login" replace />)
  return (
    <ConfigProvider locale={zhCN}>
      <AntApp>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/dashboard" element={guarded(<DashboardPage />)} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </AntApp>
    </ConfigProvider>
  )
}
```

```tsx
// main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>)
```

- [ ] 7.8 验证：`cd frontend && npm run build`（tsc + vite build 通过，无类型错误）

- [ ] 7.9 commit：`git add frontend && git commit -m "feat(frontend): 骨架+登录页+路由守卫"`

---

### Task 8: 部署（docker compose + nginx）

**Files**: Create `deploy/docker-compose.yml`, `deploy/Dockerfile.api`, `deploy/Dockerfile.frontend`, `deploy/nginx.conf`, `backend/.dockerignore`, `frontend/.dockerignore`, 根 `README.md`；Modify `backend/app/main.py`（末尾 `app = create_app()`）

**Interfaces**:
- Produces: `docker compose -f deploy/docker-compose.yml up --build` → 3000 端口可登录
- Consumes: 全部

**Steps**:

- [ ] 8.1 写 `deploy/Dockerfile.api`：

```dockerfile
FROM python:3.10-slim
WORKDIR /srv
COPY backend/ .
RUN pip install --no-cache-dir .
RUN alembic upgrade head
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

注意：`app.main:app` 需要模块级 app 实例——本任务同时修改 `backend/app/main.py` 末尾加一行 `app = create_app()`（随本任务 commit）。

- [ ] 8.2 写 `deploy/Dockerfile.frontend`：

```dockerfile
FROM node:22-alpine AS build
WORKDIR /srv
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /srv/dist /usr/share/nginx/html
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
```

- [ ] 8.3 写 `deploy/nginx.conf`：

```nginx
server {
  listen 3000;
  root /usr/share/nginx/html;
  index index.html;
  location /api/ {
    proxy_pass http://api:8000;
    proxy_set_header Host $host;
  }
  location / {
    try_files $uri /index.html;
  }
}
```

- [ ] 8.4 写 `deploy/docker-compose.yml`：

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: lims
      POSTGRES_USER: lims
      POSTGRES_PASSWORD: lims
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U lims"]
      interval: 5s
      timeout: 3s
      retries: 10
  api:
    build: { context: .., dockerfile: deploy/Dockerfile.api }
    environment:
      DATABASE_URL: postgresql+psycopg://lims:lims@db:5432/lims
      JWT_SECRET: change-me-in-prod
    depends_on:
      db: { condition: service_healthy }
    command: sh -c "python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port 8000"
  web:
    build: { context: .., dockerfile: deploy/Dockerfile.frontend }
    ports: ["3000:3000"]
    depends_on: [api]
volumes:
  pgdata:
```

- [ ] 8.5 验证（冒烟清单，逐项执行）：
  1. `docker compose -f deploy/docker-compose.yml up --build -d`
  2. `curl -sf localhost:3000/api/health` → `{"status":"ok"}`
  3. `curl -sf -X POST localhost:3000/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"lims-admin-1"}'` → 返回 access_token
  4. 浏览器开 `localhost:3000` → 登录页 → 用 admin/lims-admin-1 登录 → Dashboard 显示"管理"
  5. `docker compose -f deploy/docker-compose.yml down` 收尾

- [ ] 8.6 commit：`git add deploy backend/app/main.py README.md && git commit -m "feat(deploy): docker compose + nginx"`

---

## 验收（计划完成标准）

- [ ] `cd backend && python -m pytest` 全绿（health/security/auth/rbac/numbering/alembic）
- [ ] `cd frontend && npm run build` 通过
- [ ] docker compose 冒烟清单（Task 8.5）5 项全过
- [ ] 编号服务 8 个格式函数单测覆盖（Q/C/S-EMC/T/TR{层}-{模板}/QR/R-委托批次/EQ/CU）
- [ ] 完成后把 `docs/CONTEXT.md` 的 `TestCommand:` 配为 `cd backend && python -m pytest`

## 后续计划接口（写 P2 计划时引用）

- 认证：`get_current_user` / `require_role(*roles)` 依赖
- 编号：`app.numbering.service` 全部函数
- 测试基建：`tests/conftest.py` 的 `client` / `db_session` / `admin_token` fixture + `auth_hdr`
- 前端：`apiFetch` + `UserOut` 类型 + 路由结构（P2 在 `/dashboard` 下加菜单与子路由）
