# PowerShell Task Runner for INSIGHTORA BI Platform
# Alternative to Makefile for Windows users

param(
    [Parameter(Position=0)]
    [string]$Task = "help"
)

$ErrorActionPreference = "Stop"

function Show-Help {
    Write-Host "INSIGHTORA BI Platform - Available Commands" -ForegroundColor Cyan
    Write-Host "===========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Setup & Installation:" -ForegroundColor Yellow
    Write-Host "  .\scripts\tasks.ps1 setup-dev      - Set up complete development environment"
    Write-Host "  .\scripts\tasks.ps1 install        - Install Python dependencies"
    Write-Host "  .\scripts\tasks.ps1 install-rust   - Install Rust toolchain and dependencies"
    Write-Host ""
    Write-Host "Rust Build Commands:" -ForegroundColor Yellow
    Write-Host "  .\scripts\tasks.ps1 build-rust     - Build Rust performance modules"
    Write-Host "  .\scripts\tasks.ps1 clean-rust     - Clean Rust build artifacts"
    Write-Host "  .\scripts\tasks.ps1 test-rust      - Run Rust unit tests"
    Write-Host "  .\scripts\tasks.ps1 bench-rust     - Run Rust benchmarks"
    Write-Host "  .\scripts\tasks.ps1 lint-rust      - Run Rust linter (clippy)"
    Write-Host "  .\scripts\tasks.ps1 format-rust    - Format Rust code"
    Write-Host ""
    Write-Host "Python Backend Commands:" -ForegroundColor Yellow
    Write-Host "  .\scripts\tasks.ps1 run-backend    - Start FastAPI development server"
    Write-Host "  .\scripts\tasks.ps1 test-backend   - Run Python tests"
    Write-Host ""
    Write-Host "Combined Commands:" -ForegroundColor Yellow
    Write-Host "  .\scripts\tasks.ps1 all            - Build everything (Rust + Python setup)"
    Write-Host "  .\scripts\tasks.ps1 clean          - Clean all build artifacts"
    Write-Host "  .\scripts\tasks.ps1 verify-rust    - Verify Rust module installation"
    Write-Host ""
}

function Install-Dependencies {
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    pip install -r backend/requirements/base.txt
    if (Test-Path "backend/requirements/dev.txt") {
        pip install -r backend/requirements/dev.txt
    }
    Write-Host "Python dependencies installed!" -ForegroundColor Green
}

function Install-RustToolchain {
    Write-Host "Installing Rust toolchain..." -ForegroundColor Yellow
    Write-Host "Please visit: https://rustup.rs/" -ForegroundColor Cyan
    Write-Host "Or run the installer directly:" -ForegroundColor Cyan
    Write-Host "  Invoke-WebRequest -Uri https://win.rustup.rs/x86_64 -OutFile rustup-init.exe" -ForegroundColor Gray
    Write-Host "  .\rustup-init.exe" -ForegroundColor Gray
}

function Build-RustModules {
    Write-Host "Building Rust performance modules..." -ForegroundColor Yellow
    & "$PSScriptRoot\build_rust.ps1"
}

function Clean-RustArtifacts {
    Write-Host "Cleaning Rust build artifacts..." -ForegroundColor Yellow
    Push-Location insightora_core
    cargo clean
    Pop-Location
    
    Remove-Item -Path "backend\app\core\insightora_core.pyd" -ErrorAction SilentlyContinue
    Remove-Item -Path "backend\app\core\insightora_core.so" -ErrorAction SilentlyContinue
    
    Write-Host "Rust artifacts cleaned!" -ForegroundColor Green
}

function Test-RustCode {
    Write-Host "Running Rust unit tests..." -ForegroundColor Yellow
    Push-Location insightora_core
    cargo test --release
    Pop-Location
}

function Bench-RustCode {
    Write-Host "Running Rust benchmarks..." -ForegroundColor Yellow
    Push-Location insightora_core
    cargo bench
    Pop-Location
}

function Lint-RustCode {
    Write-Host "Running Rust linter (clippy)..." -ForegroundColor Yellow
    Push-Location insightora_core
    cargo clippy -- -D warnings
    Pop-Location
}

function Format-RustCode {
    Write-Host "Formatting Rust code..." -ForegroundColor Yellow
    Push-Location insightora_core
    cargo fmt
    Pop-Location
    Write-Host "Rust code formatted!" -ForegroundColor Green
}

function Run-BackendServer {
    Write-Host "Starting FastAPI development server..." -ForegroundColor Yellow
    Push-Location backend
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    Pop-Location
}

function Test-BackendCode {
    Write-Host "Running Python tests..." -ForegroundColor Yellow
    Push-Location backend
    pytest tests/ -v
    Pop-Location
}

function Build-AllComponents {
    Install-Dependencies
    Build-RustModules
    Write-Host ""
    Write-Host "All components built successfully!" -ForegroundColor Green
}

function Clean-AllArtifacts {
    Clean-RustArtifacts
    Write-Host "Cleaning Python cache..." -ForegroundColor Yellow
    Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
    Get-ChildItem -Path . -Recurse -File -Filter "*.pyc" | Remove-Item -Force
    Get-ChildItem -Path . -Recurse -Directory -Filter "*.egg-info" | Remove-Item -Recurse -Force
    Write-Host "All artifacts cleaned!" -ForegroundColor Green
}

function Verify-RustInstallation {
    Write-Host "Verifying Rust installation..." -ForegroundColor Yellow
    Push-Location insightora_core
    cargo build --release
    Pop-Location
    
    $testScript = @"
import sys
sys.path.insert(0, 'backend/app/core')
import insightora_core
print('Rust module imported successfully')
print('Module:', insightora_core.__name__)
"@
    
    python -c $testScript
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "Rust module verified successfully!" -ForegroundColor Green
    }
}

function Setup-DevEnvironment {
    Write-Host "Setting up development environment..." -ForegroundColor Cyan
    
    # Check if Rust is installed
    try {
        $null = Get-Command cargo -ErrorAction Stop
        Write-Host "Rust is already installed" -ForegroundColor Green
    } catch {
        Write-Host "Rust is not installed" -ForegroundColor Red
        Install-RustToolchain
        Write-Host ""
        Write-Host "Please install Rust and run this command again." -ForegroundColor Yellow
        return
    }
    
    Install-Dependencies
    Build-RustModules
    
    Write-Host ""
    Write-Host "Development environment ready!" -ForegroundColor Green
}

# Execute the requested task
switch ($Task.ToLower()) {
    "help" { Show-Help }
    "setup-dev" { Setup-DevEnvironment }
    "install" { Install-Dependencies }
    "install-rust" { Install-RustToolchain }
    "build-rust" { Build-RustModules }
    "clean-rust" { Clean-RustArtifacts }
    "test-rust" { Test-RustCode }
    "bench-rust" { Bench-RustCode }
    "lint-rust" { Lint-RustCode }
    "format-rust" { Format-RustCode }
    "run-backend" { Run-BackendServer }
    "test-backend" { Test-BackendCode }
    "all" { Build-AllComponents }
    "clean" { Clean-AllArtifacts }
    "verify-rust" { Verify-RustInstallation }
    default {
        Write-Host "Unknown task: $Task" -ForegroundColor Red
        Write-Host ""
        Show-Help
        exit 1
    }
}
