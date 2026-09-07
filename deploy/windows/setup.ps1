#Requires -Version 5.1
# LIMS Windows one-time setup - T-007/T-008/T-011
# NOTE: pure ASCII on purpose. cmd/PowerShell 5.1 read scripts without BOM as
# ANSI/GBK on zh-CN Windows; CJK chars get garbled and can corrupt parsing.
# NOTE: $ErrorActionPreference=Stop does NOT catch native-command (pip/npm/...)
# exit codes, so every step below checks $LASTEXITCODE and fails fast.
# Usage: powershell -ExecutionPolicy Bypass -File deploy\windows\setup.ps1
$ErrorActionPreference = "Stop"

$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
Write-Host "== LIMS Windows setup (root: $root) =="

# 1/6 Locate Python >= 3.10 (try 'python' first; fall back to 'py' launcher if
# the Microsoft Store alias or an old version fails)
$pyCmd = $null
foreach ($candidate in @("python", "py")) {
    if (-not (Get-Command $candidate -ErrorAction SilentlyContinue)) { continue }
    $null = & $candidate -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>$null
    if ($LASTEXITCODE -eq 0) { $pyCmd = $candidate; break }
}
if (-not $pyCmd) {
    Write-Host "[ERROR] Python 3.10+ not found. Install Python 3.10+ with 'Add python.exe to PATH' checked (python.org/downloads). If 'python' opens Microsoft Store, use the official installer." -ForegroundColor Red
    exit 1
}
Write-Host "[1/6] Python OK: $(& $pyCmd --version)"

# 2/6 venv (idempotent)
$venvPy = Join-Path $backend ".venv\Scripts\python.exe"
if (Test-Path $venvPy) {
    Write-Host "[2/6] venv exists, skip"
} else {
    Write-Host "[2/6] Creating venv..."
    & $pyCmd -m venv (Join-Path $backend ".venv")
    if ($LASTEXITCODE -ne 0) { Write-Host "[ERROR] venv creation failed (exit $LASTEXITCODE)." -ForegroundColor Red; exit 1 }
}

# 3/6 Backend deps
Write-Host "[3/6] Installing backend deps..."
& $venvPy -m pip install --disable-pip-version-check $backend
if ($LASTEXITCODE -ne 0) { Write-Host "[ERROR] pip install failed (exit $LASTEXITCODE). See output above." -ForegroundColor Red; exit 1 }

# 4/6 Frontend build
$node = Get-Command node -ErrorAction SilentlyContinue
$npm = Get-Command npm -ErrorAction SilentlyContinue
if (-not $node -or -not $npm) {
    Write-Host "[ERROR] Node.js/npm not found. Install Node.js 20+ (nodejs.org) and re-run this script." -ForegroundColor Red
    exit 1
}
Write-Host "[4/6] Building frontend (npm ci + build)..."
Push-Location $frontend
try {
    & npm ci
    if ($LASTEXITCODE -ne 0) { Write-Host "[ERROR] npm ci failed (exit $LASTEXITCODE)." -ForegroundColor Red; exit 1 }
    & npm run build
    if ($LASTEXITCODE -ne 0) { Write-Host "[ERROR] npm run build failed (exit $LASTEXITCODE)." -ForegroundColor Red; exit 1 }
} finally {
    Pop-Location
}

# 5/6 Migrations + initial admin (idempotent)
Write-Host "[5/6] DB migration + initial admin..."
Push-Location $backend
try {
    & $venvPy -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) { Write-Host "[ERROR] alembic upgrade failed (exit $LASTEXITCODE)." -ForegroundColor Red; exit 1 }
    & $venvPy -m app.seed
    if ($LASTEXITCODE -ne 0) { Write-Host "[ERROR] app.seed failed (exit $LASTEXITCODE)." -ForegroundColor Red; exit 1 }
} finally {
    Pop-Location
}

# 6/6 Done
Write-Host "[6/6] Setup complete!"
Write-Host "  Start: double-click deploy\windows\start.bat (default port 8000, edit --port in start.bat to change)"
Write-Host "  Open: http://localhost:8000   login: admin / lims-admin-1"
