# LIMS — EMC 实验室信息管理系统

面向 10 人 EMC（电磁兼容）检测实验室的 LIMS。当前用 Excel/Word/纸质管理，痛点：样品流转无留痕、测试布置手工指定易错、报告制作半天~一天/份。

**核心价值**：数据沿业务流自然沉淀，报告从"人工拼"变成"数据组装"；全程留痕满足 CMA/CNAS 认可体系要求。

> 当前进度见 `STATUS.md`；设计规格 `docs/superpowers/specs/`；实现计划 `docs/superpowers/plans/`；术语表 `docs/UBIQUITOUS_LANGUAGE.md`。

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.10+ / FastAPI / SQLAlchemy 2 / Alembic / PyJWT / bcrypt |
| 前端 | React 19 / TypeScript / Vite / Ant Design / react-router |
| 数据库 | 开发 SQLite；生产 PostgreSQL 16 |
| 部署 | Docker Compose + nginx（`deploy/`） |

## 目录结构

```
backend/            FastAPI 应用（app/ 业务代码、alembic/ 迁移、tests/ 测试）
frontend/           React 前端（src/pages 页面、src/api 客户端）
deploy/             docker compose + Dockerfile + nginx 配置
docs/               设计规格 / 实现计划 / ADR / 术语表 / CONTEXT
tickets.md          工单列表（zcode 工作台）
STATUS.md           当前状态总览（自动生成）
```

## 本地开发

### 后端

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head          # 建表（默认 sqlite:///./lims.db）
python -m app.seed            # 幂等创建 admin（密码 env SEED_ADMIN_PASSWORD，默认 lims-admin-1）
uvicorn app.main:app --reload --port 8000
```

API 文档：`http://localhost:8000/docs`

### 前端

```bash
cd frontend
npm ci
npm run dev                   # http://localhost:5173，/api 代理到 :8000
```

默认账号：`admin` / `lims-admin-1`

### 测试

```bash
cd backend && python3 -m pytest    # 后端（health/security/auth/rbac/numbering/alembic）
cd frontend && npm run build       # 前端类型检查 + 构建
```

## 部署（Docker）

```bash
docker compose -f deploy/docker-compose.yml up --build -d
# → http://localhost:3000（nginx 前端 + /api 反代 api:8000；postgres 持久化在 pgdata 卷）
```

api 容器启动时自动执行 `alembic upgrade head` 与幂等 seed。生产环境必须修改 `JWT_SECRET` 与数据库口令。

## 工单工作台

本仓库使用 zcode 工单工作台管理开发流程（见 `AGENTS.md`）：

```
zcode ticket context    # 接手仓库先看这个
zcode ticket next       # 建议下一步
zcode ticket log        # 流转历史
```
