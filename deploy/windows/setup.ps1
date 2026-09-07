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
