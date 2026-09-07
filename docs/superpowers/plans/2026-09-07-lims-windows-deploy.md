# LIMS Windows 原生部署 — 实现计划

- 日期：2026-09-07
- 工单：T-007
- 规格：`docs/superpowers/specs/2026-09-07-lims-windows-deploy-design.md`（已批准）
- 范围：后端静态托管 + Windows 部署/启动脚本 + 文档与冒烟

## Goal

无 Docker 的 Windows 机器上：`setup.ps1` 一次性部署 + 双击 `start.bat` 启动，浏览器访问 `http://localhost:8000` 登录使用；单 uvicorn 进程同时提供 API 与前端静态文件（SPA 回退）。

## Architecture

- 后端单进程：`create_app(static_dir)` 在已注册 `/api/*` 路由之后追加一个 GET catch-all 路由——`/api/` 前缀 404 返回 JSON；dist 内真实文件 `FileResponse` 直出；其余路径回退 `index.html`
- 静态目录来自 `Settings.static_dir`（env `STATIC_DIR`），模块级 `app = create_app(get_settings().static_dir)` 于进程启动时解析一次（避开 `get_settings` 的 lru_cache 对测试注入的影响）
- dev（vite dev）与 docker（api 容器无 dist）均为纯 API 模式，行为零变化

## Tech Stack

Python 3.10 / FastAPI / starlette FileResponse / pytest + TestClient；PowerShell 5.1（Win10/11 自带）/ bat；`.gitattributes` 行尾控制

## Global Constraints（逐任务继承）

- 测试命令：`cd backend && python3 -m pytest`（本机无 `python` 别名，勿用 `python`）
- 本机 8000 端口为 llama-server（**禁动**），冒烟一律用 8011
- 不改 `deploy/`（docker 路径）任何现有文件；不改 conftest 既有 fixture
- `create_app()` 无参调用必须保持纯 API 模式（存量 23 测试回归证明）
- `*.bat`/`*.ps1` 文件必须以 CRLF 行尾写入（git 检出于 Windows 后 bat 才能正确解析）
- 所有新代码风格沿用仓库现状（中文注释可、无 type: ignore、测试文件平铺 `tests/`）

## Tasks

### Task 1: 后端静态托管（config + main + test_static，TDD）

**Files**:
- Modify `backend/app/config.py`（Settings +1 字段）
- Modify `backend/app/main.py`（静态托管，重写为下方完整内容）
- Create `backend/tests/test_static.py`（13 用例，下方完整代码）

**Interfaces**:
- Consumes: 现有 `create_app()`（conftest 的 `client` fixture 无参调用它）
- Produces: `create_app(static_dir: str | None = None) -> FastAPI`；模块级 `app` 读 `Settings.static_dir`

**Steps**:

- [ ] 1.1 修改 `backend/app/config.py`，`Settings` 类加一行字段（在 `jwt_expire_min` 之后）：

```python
    static_dir: str | None = None
```

- [ ] 1.2 新建 `backend/tests/test_static.py`，完整内容：

```python
"""静态托管（SPA 回退）测试 — T-007 Task 1。

不依赖 db fixture：health/静态路由不触库。
"""
from fastapi.testclient import TestClient

from app.main import create_app


def _make_dist(tmp_path):
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<html>LIMS SPA</html>", encoding="utf-8")
    (dist / "assets" / "app.js").write_text("console.log(1)", encoding="utf-8")
    (dist / "favicon.svg").write_text("<svg></svg>", encoding="utf-8")
    return dist


def test_root_serves_index(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.get("/")
    assert r.status_code == 200
    assert "LIMS SPA" in r.text


def test_spa_fallback_for_client_route(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.get("/dashboard")
    assert r.status_code == 200
    assert "LIMS SPA" in r.text


def test_deep_spa_fallback(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.get("/samples/123/history")
    assert r.status_code == 200
    assert "LIMS SPA" in r.text


def test_static_file_served_with_type(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.get("/assets/app.js")
    assert r.status_code == 200
    assert "javascript" in r.headers["content-type"]
    assert r.text == "console.log(1)"


def test_top_level_static_file(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.get("/favicon.svg")
    assert r.status_code == 200
    assert "image/svg" in r.headers["content-type"]


def test_api_routes_unaffected(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_unknown_api_returns_json_404(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.get("/api/nope")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/json")
    assert "LIMS SPA" not in r.text


def test_unknown_api_post_returns_404(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.post("/api/nope", json={})
    assert r.status_code == 404


def test_path_traversal_blocked(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.get("/%2e%2e/%2e%2e/etc/passwd")
    assert "root:" not in r.text
    assert "LIMS SPA" in r.text  # 回退 index.html，不泄露系统文件


def test_pure_api_mode_unchanged():
    c = TestClient(create_app())
    assert c.get("/dashboard").status_code == 404
    assert c.get("/api/health").status_code == 200


def test_missing_dist_dir_falls_back_to_api_mode(tmp_path):
    c = TestClient(create_app(static_dir=str(tmp_path / "nope")))
    assert c.get("/dashboard").status_code == 404


def test_dist_without_index_falls_back_to_api_mode(tmp_path):
    (tmp_path / "d").mkdir()
    c = TestClient(create_app(static_dir=str(tmp_path / "d")))
    assert c.get("/").status_code == 404


def test_empty_full_path_is_index(tmp_path):
    c = TestClient(create_app(static_dir=str(_make_dist(tmp_path))))
    r = c.get("/")
    assert r.status_code == 200
    assert "LIMS SPA" in r.text
```

- [ ] 1.3 跑测试确认失败（实现前，`static_dir` 参数不存在 → TypeError）：`cd backend && python3 -m pytest tests/test_static.py -q` 预期 13 failed/error

- [ ] 1.4 重写 `backend/app/main.py` 为完整内容：

```python
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from .api.auth import router as auth_router
from .api.users import router as users_router
from .config import get_settings


def _static_dist(static_dir: str | None) -> Path | None:
    """有效 dist 目录（存在且含 index.html）→ 绝对路径；否则 None。"""
    if not static_dir:
        return None
    d = Path(static_dir)
    if d.is_dir() and (d / "index.html").is_file():
        return d.resolve()
    return None


def _mount_spa(app: FastAPI, dist: Path) -> None:
    """SPA 托管（注册在所有 /api 路由之后）：

    - /api/ 前缀未命中 → JSON 404（不吞 API 错误）
    - dist 内真实文件 → FileResponse 直出（自动 content-type）
    - 其余路径 → index.html（SPA 路由回退）
    - is_relative_to 守卫防路径穿越
    """

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_or_static(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        file = (dist / full_path).resolve()
        if full_path and file.is_file() and file.is_relative_to(dist):
            return FileResponse(file)
        return FileResponse(dist / "index.html")


def create_app(static_dir: str | None = None) -> FastAPI:
    app = FastAPI(title="LIMS API")
    app.include_router(auth_router)
    app.include_router(users_router)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    dist = _static_dist(static_dir)
    if dist is not None:
        _mount_spa(app, dist)

    return app


app = create_app(get_settings().static_dir)
```

- [ ] 1.5 跑 `cd backend && python3 -m pytest tests/test_static.py -q`，预期 13 passed

- [ ] 1.6 全量回归 `cd backend && python3 -m pytest -q`，预期 23 + 13 = 36 passed（纯 API 模式存量不回归）

- [ ] 1.7 commit：`git add backend && git commit -m "feat(backend): 静态托管+SPA 回退 (T-007 Task1)"`

---

### Task 2: Windows 部署脚本（setup.ps1 + start.bat + .gitattributes）

**Files**:
- Create `deploy/windows/setup.ps1`（CRLF）
- Create `deploy/windows/start.bat`（CRLF）
- Create `.gitattributes`（仓库根）

**Interfaces**:
- Consumes: Task 1 的 `STATIC_DIR` env 契约；`backend/`（pyproject 可 pip install）、`frontend/`（npm ci + build → dist）、alembic、`app.seed`
- Produces: 目标机一条命令部署 + 双击启动；约定端口 8000、SQLite、venv 位于 `backend\.venv`

**Steps**:

- [ ] 2.1 新建仓库根 `.gitattributes`：

```
# Windows 部署脚本强制 CRLF（bat 解析依赖）
*.bat text eol=crlf
*.ps1 text eol=crlf
```

- [ ] 2.2 新建 `deploy/windows/setup.ps1`，完整内容（**写入后转 CRLF**，见 2.5）：

```powershell
#Requires -Version 5.1
# LIMS Windows 一次性部署 — T-007
# 用法: powershell -ExecutionPolicy Bypass -File deploy\windows\setup.ps1
$ErrorActionPreference = "Stop"

$root = Split-Path $PSScriptRoot -Parent -Parent
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
Write-Host "== LIMS Windows 部署 (root: $root) =="

# 1/6 定位 Python >= 3.10（python 优先；商店别名会失败则退回 py launcher）
$pyCmd = $null
foreach ($candidate in @("python", "py")) {
    if (-not (Get-Command $candidate -ErrorAction SilentlyContinue)) { continue }
    $null = & $candidate -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>$null
    if ($LASTEXITCODE -eq 0) { $pyCmd = $candidate; break }
}
if (-not $pyCmd) {
    Write-Host "[ERROR] 未找到 Python 3.10+。请安装并勾选 'Add python.exe to PATH'（python.org/downloads）；若 python 打开 Microsoft Store，请用官方安装器。" -ForegroundColor Red
    exit 1
}
Write-Host "[1/6] Python OK: $(& $pyCmd --version)"

# 2/6 venv（幂等）
$venvPy = Join-Path $backend ".venv\Scripts\python.exe"
if (Test-Path $venvPy) {
    Write-Host "[2/6] venv 已存在，跳过"
} else {
    Write-Host "[2/6] 创建 venv..."
    & $pyCmd -m venv (Join-Path $backend ".venv")
}

# 3/6 后端依赖
Write-Host "[3/6] 安装后端依赖..."
& $venvPy -m pip install --disable-pip-version-check $backend

# 4/6 前端构建
$node = Get-Command node -ErrorAction SilentlyContinue
$npm = Get-Command npm -ErrorAction SilentlyContinue
if (-not $node -or -not $npm) {
    Write-Host "[ERROR] 未找到 Node.js/npm。请安装 Node.js 20+（nodejs.org）后重跑本脚本。" -ForegroundColor Red
    exit 1
}
Write-Host "[4/6] 构建前端 (npm ci + build)..."
Push-Location $frontend
try {
    & npm ci
    & npm run build
} finally {
    Pop-Location
}

# 5/6 迁移 + 初始 admin（幂等）
Write-Host "[5/6] 数据库迁移 + 初始 admin..."
Push-Location $backend
try {
    & $venvPy -m alembic upgrade head
    & $venvPy -m app.seed
} finally {
    Pop-Location
}

# 6/6 完成
Write-Host "[6/6] 部署完成!"
Write-Host "  启动: 双击 deploy\windows\start.bat（默认端口 8000，可改 start.bat 中 --port）"
Write-Host "  访问: http://localhost:8000  账号 admin / lims-admin-1"
```

- [ ] 2.3 新建 `deploy/windows/start.bat`，完整内容（**写入后转 CRLF**）：

```bat
@echo off
rem LIMS Windows 日常启动 — 双击即用（先跑过 setup.ps1）
cd /d "%~dp0..\..\backend"
set "STATIC_DIR=%~dp0..\..\frontend\dist"
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] backend\.venv 不存在，请先运行 deploy\windows\setup.ps1
    pause
    exit /b 1
)
.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
```

- [ ] 2.4 行尾转换并验证（两个脚本文件）：

```bash
cd /home/dkd/projects/lims
sed -i 's/$/\r/' deploy/windows/setup.ps1 deploy/windows/start.bat
file deploy/windows/setup.ps1 deploy/windows/start.bat   # 应显示 "with CRLF line terminators"
grep -c $'\r' deploy/windows/setup.ps1                    # 应等于总行数
```

- [ ] 2.5 bat 语法静态审查（逐行核对）：`@echo off` 首行；`cd /d` + `%~dp0..\..\` 上两级到仓库根；`set "VAR=..."` 带引号；`if not exist` 块括号配对；`pause` 收尾。ps1 审查：`$PSScriptRoot` 上两级到仓库根；`Push-Location/Pop-Location` 成对（try/finally）；无 PS7 专有语法（不用 `??`、`&&`、`ternary`）

- [ ] 2.6 确认 `.gitattributes` 生效：`git add .gitattributes && git check-attr -a deploy/windows/start.bat`，预期两行：

```
deploy/windows/start.bat: text: set
deploy/windows/start.bat: eol: crlf
```

- [ ] 2.7 commit：`git add .gitattributes deploy/windows && git commit -m "feat(deploy): Windows setup.ps1 + start.bat (T-007 Task2)"`

---

### Task 3: 文档 + 冒烟验证 + 附带改动

**Files**:
- Modify `README.md`（增「Windows 部署（无 Docker）」章节）
- 附带提交：`frontend/vite.config.ts`（工作区已有的 `LIMS_API_PROXY` 覆盖，dev 逃生口）

**Interfaces**:
- Consumes: Task 1 静态托管（冒烟依赖）、Task 2 脚本路径/约定
- Produces: README Windows 章节（含真机补跑清单）；本机冒烟证据

**Steps**:

- [ ] 3.1 冒烟（Task 1 代码在库后执行；端口 8011，**禁动 8000**）：

```bash
mkdir -p /tmp/lims-win-dist/assets
echo '<html>LIMS SPA</html>' > /tmp/lims-win-dist/index.html
echo 'console.log(1)' > /tmp/lims-win-dist/assets/app.js
cd /home/dkd/projects/lims/backend
STATIC_DIR=/tmp/lims-win-dist nohup python3 -m uvicorn app.main:app --port 8011 > /tmp/lims-win-smoke.log 2>&1 &
sleep 3
echo "1) 首页:";        curl -sf localhost:8011/ | grep -o "LIMS SPA"
echo "2) SPA 回退:";    curl -sf localhost:8011/dashboard | grep -o "LIMS SPA"
echo "3) 静态文件:";    curl -sf localhost:8011/assets/app.js
echo "4) health:";      curl -sf localhost:8011/api/health
echo "5) api 404:";     curl -s -o /dev/null -w "%{http_code}\n" localhost:8011/api/nope   # 期望 404
kill %1; rm -rf /tmp/lims-win-dist /tmp/lims-win-smoke.log
```

预期：1/2 输出 `LIMS SPA`；3 输出 `console.log(1)`；4 输出 `{"status":"ok"}`；5 输出 `404`。任何一项不符 → 回 Task 1 修复。

- [ ] 3.2 `cd frontend && npm run build` 确认通过（前端无改动，回归确认）

- [ ] 3.3 修改 `README.md`：在「## 部署（Docker）」章节**之后**插入以下完整章节（外层四反引号仅为本计划文档的嵌套围栏，README 中用普通三反引号）：

````markdown
## Windows 部署（无 Docker）

目标机无法安装 Docker 时使用。前提：Python 3.10+（安装时勾选 Add to PATH）与 Node 20+。

### 一次性部署

```powershell
powershell -ExecutionPolicy Bypass -File deploy\windows\setup.ps1
```

自动完成：创建 `backend\.venv` → 装后端依赖 → `npm ci && npm run build` 构建前端 → 数据库迁移 → 创建 admin。可重复执行（幂等）。

### 日常启动

双击 `deploy\windows\start.bat`，然后浏览器打开 `http://localhost:8000`。

默认账号：`admin` / `lims-admin-1`

### 注意

- **防火墙**：uvicorn 首次启动 Windows 防火墙会询问是否允许联网——选「允许」（局域网其他机器访问的前提）。
- **端口**：默认 8000；改端口编辑 `start.bat` 中的 `--port` 行。
- **执行策略**：若 `setup.ps1` 被执行策略拦截，用上面的 `-ExecutionPolicy Bypass` 命令运行。
- **数据库**：默认 SQLite（`backend\lims.db`）；PostgreSQL 为 docker 路径使用。

### Windows 真机验证清单（待补跑）

- [ ] `setup.ps1` 全流程（python 检测 / venv / pip / npm build / 迁移 / seed）
- [ ] `start.bat` 双击启动
- [ ] 浏览器登录 admin/lims-admin-1 → Dashboard 显示「管理：管理员」
- [ ] 直链 `/dashboard` 打开 + 刷新（SPA 回退）
- [ ] 局域网第二台机器访问（防火墙放行后）
- [ ] `setup.ps1` 重复执行幂等
````

- [ ] 3.4 前端附带改动确认：`git diff frontend/vite.config.ts` 应只含 `LIMS_API_PROXY` 覆盖两行（注释 + proxy 行），无其他意外改动

- [ ] 3.5 commit：`git add README.md frontend/vite.config.ts && git commit -m "docs: Windows 部署章节 + vite proxy 可覆盖 (T-007 Task3)"`

---

## 验收（计划完成标准）

- [ ] `cd backend && python3 -m pytest` 全绿（36 = 存量 23 + 静态 13）
- [ ] `cd frontend && npm run build` 通过
- [ ] Task 3.1 冒烟 5 项全过（端口 8011）
- [ ] `file` 确认 setup.ps1 / start.bat 为 CRLF
- [ ] `git check-attr` 确认 .gitattributes 对 bat/ps1 生效
- [ ] 真机补跑清单已随 README 交付（标注待补跑）
