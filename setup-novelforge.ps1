$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$Log = Join-Path $Root "setup.log"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host $Message -ForegroundColor Cyan
    Add-Content -Path $Log -Value ""
    Add-Content -Path $Log -Value $Message
}

function Write-Info {
    param([string]$Message)
    Write-Host $Message
    Add-Content -Path $Log -Value $Message
}

function Write-Fail {
    param([string]$Message)
    Write-Host ""
    Write-Host "[ERROR] $Message" -ForegroundColor Red
    Add-Content -Path $Log -Value "[ERROR] $Message"
    Write-Host ""
    Write-Host "Setup failed. Please copy the last lines of setup.log to ChatGPT." -ForegroundColor Yellow
    Write-Host "Log file: $Log"
    Read-Host "Press Enter to exit"
    exit 1
}

function Run-Cmd {
    param(
        [string]$WorkingDirectory,
        [string]$FilePath,
        [string[]]$Arguments
    )

    Write-Info "RUN: $FilePath $($Arguments -join ' ')"
    Write-Info "DIR: $WorkingDirectory"

    Push-Location $WorkingDirectory
    try {
        & $FilePath @Arguments 2>&1 | Tee-Object -FilePath $Log -Append
        if ($LASTEXITCODE -ne 0) {
            Write-Fail "Command failed: $FilePath $($Arguments -join ' ')"
        }
    }
    finally {
        Pop-Location
    }
}

"========================================" | Set-Content -Path $Log
"NovelForge setup log" | Add-Content -Path $Log
"Root: $Root" | Add-Content -Path $Log
"Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Add-Content -Path $Log
"========================================" | Add-Content -Path $Log

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "NovelForge Setup" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

try {
    Write-Step "[1/7] Checking project folders..."
    $ApiDir = Join-Path $Root "apps\api"
    $WebDir = Join-Path $Root "apps\web"
    if (!(Test-Path $ApiDir)) { Write-Fail "apps\api was not found. Please run this file in the project root." }
    if (!(Test-Path $WebDir)) { Write-Fail "apps\web was not found. Please run this file in the project root." }
    Write-Info "Project folders OK."

    Write-Step "[2/7] Checking Python..."
    $PyCmd = $null
    $PyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($PyLauncher) {
        $PyCmd = "py"
    } else {
        $PythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if ($PythonCmd) { $PyCmd = "python" }
    }
    if (!$PyCmd) { Write-Fail "Python was not found. Please install Python 3.12+ and add it to PATH." }
    Run-Cmd -WorkingDirectory $Root -FilePath $PyCmd -Arguments @("--version")

    Write-Step "[3/7] Creating backend virtual environment..."
    $VenvPython = Join-Path $ApiDir ".venv\Scripts\python.exe"
    if (!(Test-Path $VenvPython)) {
        Run-Cmd -WorkingDirectory $ApiDir -FilePath $PyCmd -Arguments @("-m", "venv", ".venv")
    } else {
        Write-Info "Existing .venv found."
    }

    Write-Step "[4/7] Installing backend dependencies..."
    Run-Cmd -WorkingDirectory $ApiDir -FilePath $VenvPython -Arguments @("-m", "pip", "install", "--upgrade", "pip")
    Run-Cmd -WorkingDirectory $ApiDir -FilePath $VenvPython -Arguments @("-m", "pip", "install", "-r", "requirements.txt")

    Write-Step "[5/7] Checking Node.js and npm..."
    $NodeCmd = Get-Command node -ErrorAction SilentlyContinue
    $NpmCmd = Get-Command npm.cmd -ErrorAction SilentlyContinue
    if (!$NodeCmd) { Write-Fail "Node.js was not found. Please install Node.js LTS." }
    if (!$NpmCmd) { Write-Fail "npm.cmd was not found. Please reinstall Node.js." }
    Run-Cmd -WorkingDirectory $WebDir -FilePath "node" -Arguments @("--version")
    Run-Cmd -WorkingDirectory $WebDir -FilePath "npm.cmd" -Arguments @("--version")

    Write-Step "[6/7] Installing frontend dependencies..."
    Run-Cmd -WorkingDirectory $WebDir -FilePath "npm.cmd" -Arguments @("install")

    Write-Step "[7/7] Building frontend..."
    Run-Cmd -WorkingDirectory $WebDir -FilePath "npm.cmd" -Arguments @("run", "build")

    $IndexHtml = Join-Path $WebDir "dist\index.html"
    if (!(Test-Path $IndexHtml)) {
        Write-Fail "Frontend build did not create apps\web\dist\index.html."
    }

    Write-Step "Creating local folders..."
    New-Item -ItemType Directory -Force -Path (Join-Path $ApiDir "local") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $ApiDir "data\projects") | Out-Null

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Setup completed successfully." -ForegroundColor Green
    Write-Host "You can now run start-novelforge.bat." -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Add-Content -Path $Log -Value "Setup completed successfully."
    Read-Host "Press Enter to exit"
}
catch {
    Write-Host ""
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    Add-Content -Path $Log -Value "[ERROR] $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Setup failed. Please copy the last lines of setup.log to ChatGPT." -ForegroundColor Yellow
    Write-Host "Log file: $Log"
    Read-Host "Press Enter to exit"
    exit 1
}
