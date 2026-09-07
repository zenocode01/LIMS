# LIMS Windows 原生部署设计规格

- 日期：2026-09-07
- 工单：T-007
- 状态：已批准（§1-§3 分节获用户确认）
- 范围：无 Docker 的 Windows 部署链路（后端静态托管 + 部署/启动脚本 + 文档）；不改 docker 生产路径

## 1. 背景与目标

目标实验室的 Windows 机器**无法安装 Docker**，现有 `deploy/`（docker compose + nginx）链路不可用。需要一条 Windows 原生部署路径：

- 前提环境：目标机已装 Python 3.10+ 与 Node 20+（用户确认）
- 交付形态：一次性部署脚本 + 日常双击启动脚本 + README 文档
- 成功标准：在目标 Windows 机上执行 `setup.ps1` 后双击 `start.bat`，浏览器访问 `http://localhost:8000` 可登录使用；局域网内其他机器可访问

**非目标**：Windows 安装包/绿色版（exe 打包）、PostgreSQL on Windows（Windows 路径默认 SQLite）、nginx for Windows。

## 2. 方案选择

| 方案 | 内容 | 结论 |
|---|---|---|
| **A（选定）** | 单进程：FastAPI 直接托管前端 dist（catch-all 路由），uvicorn 单进程单端口 | 改动最小；核心逻辑 OS 无关、Linux 可完整单测；无额外组件 |
| B | 双进程：uvicorn + 独立静态服务（vite preview 等）+ 反代 | 两进程两端口；vite preview 是 dev 工具；10 人实验室过重 |
| C | 打包 nginx for Windows | 额外组件 + 配置维护，杀鸡用牛刀 |

选定 A 的代价：uvicorn 无 gzip、无 etag（10 人局域网 + vite 产物带 hash 文件名，可接受，YAGNI）。docker 生产路径（nginx）保持不变。

## 3. §1 后端静态托管

**配置**：`Settings` 增加 `static_dir: str | None = None`（env `STATIC_DIR`，指向前端 dist 目录）。

**`create_app()` 末尾逻辑**（伪代码，实现以计划为准）：

```python
if static_dir and (d := Path(static_dir)).is_dir() and (d / "index.html").is_file():
    dist = d.resolve()

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_or_static(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(404)                      # 不存在的 API → JSON 404
        file = (dist / full_path).resolve()
        if full_path and file.is_file() and file.is_relative_to(dist):
            return FileResponse(file)                     # 真实静态文件
        return FileResponse(dist / "index.html")          # SPA 路由回退
```

**行为矩阵**（全部有单测）：

| 请求 | 结果 |
|---|---|
| `GET /`、`GET /dashboard`（任意前端路由） | 200，返回 `index.html`（SPA 回退） |
| `GET /assets/index-xxx.js`、`/favicon.svg` | 200，`FileResponse` 自动推断 content-type |
| 已注册 API（`/api/health` 等） | 不受影响（路由注册在先，优先匹配） |
| `GET/POST /api/不存在` | 404 JSON（不会误返回 index.html） |
| 路径穿越 `/%2e%2e/...` | `is_relative_to` 守卫 → 回退 index.html，不泄露文件 |
| `STATIC_DIR` 未设置 / 目录不存在 / 无 index.html | 纯 API 模式，行为与现在完全一致 |

**为什么不用 `StaticFiles(html=True)` mount**（已实测 starlette 1.2.1）：
1. 新版 `html=True` 只做「目录→index.html」和「404.html」，**无 SPA 回退**（`/dashboard` → 404 JSON）
2. mount `/` 会吞掉未注册 `/api/*` 的 404，SPA 语义下误返回 HTML，掩盖 API 错误

单个 catch-all 路由最简单、边界完全可控。

**零影响保证**：dev（vite dev，STATIC_DIR 未设置）、docker（api 容器无 dist）均为纯 API 模式，行为不变。

## 4. §2 Windows 部署脚本

**`deploy/windows/setup.ps1`**（一次性部署；PowerShell 5.1+ 兼容，不用 PS7 语法）：

0. 定位仓库根：`$root = Split-Path $PSScriptRoot -Parent -Parent`（脚本在 `deploy\windows\`，上两级），后续相对路径均基于 `$root`
1. 检查 `python --version` ≥ 3.10（解析 `python -c "import sys; print(sys.version_info[:2])"`）；失败提示装 Python 并勾选 Add to PATH（注意 Windows 商店别名：`python` 弹商店页时改用 `py -3`）
2. `python -m venv backend\.venv`（已存在跳过）
3. `backend\.venv\Scripts\python -m pip install backend`
4. 检查 node/npm → `cd frontend && npm ci && npm run build`（产出 `frontend\dist`）
5. `alembic upgrade head` + `python -m app.seed`（cwd=backend，venv python）
6. 打印完成提示：双击 start.bat 启动（默认端口 8000，可在 start.bat 修改），访问 http://localhost:8000

**`deploy/windows/start.bat`**（日常启动，双击即用）：

```bat
@echo off
rem 脚本位于 deploy\windows\，上两级为仓库根
cd /d "%~dp0..\..\backend"
set "STATIC_DIR=%~dp0..\..\frontend\dist"
.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
```

**约定**：
- 端口默认 8000；改端口编辑 start.bat 一行，README 说明
- 数据库默认 SQLite（`backend\lims.db`，`.gitignore` 已覆盖 `*.db`）；PG 留给 docker 路径
- 行尾：`*.bat`/`*.ps1` 存 CRLF（新增 `.gitattributes`：`text eol=crlf`，防 git 检出行尾错乱导致 bat 解析失败）
- 首次启动 Windows 防火墙弹窗 → README 提示「选择允许」（局域网其他机器访问的前提）
- 执行策略拦截时：`powershell -ExecutionPolicy Bypass -File deploy\windows\setup.ps1`

## 5. §3 验证策略

**本机（Linux）可验证 —— 验收标准**：
1. 新增 `backend/tests/test_static.py`：§3 行为矩阵全过（SPA 回退 / 静态文件 / API 不受影响 / api 404 / 路径穿越 / 纯 API 模式）
2. 存量 23 个测试保持绿（纯 API 模式回归）
3. `cd frontend && npm run build` 通过
4. 临时 dist 起真 uvicorn 冒烟（curl：/ → index.html、/dashboard → 回退、/assets → 200、/api/health、/api/不存在 404）；端口避开 8000（本机 8000 为 llama-server，禁动）
5. 脚本静态审查：bat 逐行核对语法；本机无 pwsh 则人工审查 ps1 语法

**真 Windows 机补跑清单**（随 README 交付，与 docker 容器链路同样性质，留待补跑）：
- [ ] `setup.ps1` 全流程（python 检测 / venv / pip / npm build / 迁移 / seed）
- [ ] `start.bat` 双击启动
- [ ] 浏览器 `http://localhost:8000` 登录 admin/lims-admin-1 → Dashboard「管理：管理员」
- [ ] 直链 `/dashboard` 打开 + 刷新（SPA 回退）
- [ ] 局域网第二台机器访问（防火墙放行后）
- [ ] `setup.ps1` 重复执行幂等（venv/迁移/seed 均不报错）

## 6. 文档与交付物

- 后端：`backend/app/config.py`（+static_dir）、`backend/app/main.py`（静态托管）、`backend/tests/test_static.py`
- 脚本：`deploy/windows/setup.ps1`、`deploy/windows/start.bat`、根 `.gitattributes`
- 文档：`README.md` 增「Windows 部署（无 Docker）」章节（前提 → setup.ps1 → start.bat → 访问/账号 → 防火墙/端口/执行策略提示 + 真机补跑清单）
- 附带：`frontend/vite.config.ts` proxy 支持 `LIMS_API_PROXY` 环境变量覆盖（默认 8000 不变；dev 端口被占时的逃生口）

## 7. 验收标准

- [ ] `cd backend && python3 -m pytest` 全绿（存量 23 + 新增静态托管用例）
- [ ] `cd frontend && npm run build` 通过
- [ ] 本机 uvicorn 冒烟（§5.4）5 项全过
- [ ] 真 Windows 机补跑清单（§5）交付于 README，标注「待补跑」
- [ ] dev / docker 两条既有路径行为零变化（纯 API 模式回归测试证明）
