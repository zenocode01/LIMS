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

## Windows 部署（无 Docker）

目标机无法安装 Docker 时使用。前提：Python 3.10+（安装时勾选 Add to PATH）与 Node 20+。

### 一次性部署

```powershell
powershell -ExecutionPolicy Bypass -File deploy\windows\setup.ps1
```

自动完成：创建 `backend\.venv` → 装后端依赖 → `npm ci && npm run build` 构建前端 → 数据库迁移 → 创建 admin。可重复执行（幂等）。

### 日常启动 / 停止

双击 `deploy\windows\start.bat`（后台最小化窗口运行，日志写 `backend\lims.log`），然后浏览器打开 `http://localhost:8000`。停止双击 `deploy\windows\stop.bat`（按端口精准杀进程，不误伤其他程序）。

默认账号：`admin` / `lims-admin-1`

### 注意

- **防火墙**：uvicorn 首次启动 Windows 防火墙会询问是否允许联网——选「允许」（局域网其他机器访问的前提）。
- **端口**：默认 8000；改端口时 `start.bat` 与 `stop.bat` 顶部的 `PORT` 变量要一致。
- **执行策略**：若 `setup.ps1` 被执行策略拦截，用上面的 `-ExecutionPolicy Bypass` 命令运行。
- **数据库**：默认 SQLite（`backend\lims.db`）；PostgreSQL 为 docker 路径使用。

### Windows 真机验证清单（待补跑）

- [ ] `setup.ps1` 全流程（python 检测 / venv / pip / npm build / 迁移 / seed）
- [ ] `start.bat` 双击启动
- [ ] 浏览器登录 admin/lims-admin-1 → Dashboard 显示「管理：管理员」
- [ ] 直链 `/dashboard` 打开 + 刷新（SPA 回退）
- [ ] 局域网第二台机器访问（防火墙放行后）
- [ ] `setup.ps1` 重复执行幂等

## 工单工作台

本仓库使用 zcode 工单工作台管理开发流程（见 `AGENTS.md`）：

```
zcode ticket context    # 接手仓库先看这个
zcode ticket next       # 建议下一步
zcode ticket log        # 流转历史
```
