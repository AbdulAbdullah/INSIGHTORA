# Build script for Rust performance modules (Windows PowerShell)
# This script compiles the Rust library and copies it to the Python backend

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Building Rust Performance Modules" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory and project paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$RustDir = Join-Path $ProjectRoot "insightora_core"
$BackendDir = Join-Path $ProjectRoot "backend\app\core"

# Check if Rust is installed
try {
    $null = Get-Command cargo -ErrorAction Stop
} catch {
    Write-Host "Error: Rust is not installed" -ForegroundColor Red
    Write-Host "Please install Rust from: https://rustup.rs/" -ForegroundColor Yellow
    Write-Host "Or run: .\scripts\install_rust.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "Rust version:" -ForegroundColor Yellow
rustc --version
cargo --version
Write-Host ""

# Navigate to Rust directory
Push-Location $RustDir

try {
    # Clean previous builds (optional, comment out for faster incremental builds)
    # Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
    # cargo clean

    # Build in release mode with optimizations
    Write-Host "Building Rust modules in release mode..." -ForegroundColor Yellow
    cargo build --release

    if ($LASTEXITCODE -ne 0) {
        throw "Build failed with exit code $LASTEXITCODE"
    }

    Write-Host "Build successful!" -ForegroundColor Green
    Write-Host ""

    # Create backend core directory if it doesn't exist
    if (-not (Test-Path $BackendDir)) {
        New-Item -ItemType Directory -Path $BackendDir -Force | Out-Null
    }

    # Copy the compiled library
    Write-Host "Copying compiled library to Python backend..." -ForegroundColor Yellow

    $LibFile = Join-Path $RustDir "target\release\insightora_core.dll"
    $DestFile = Join-Path $BackendDir "insightora_core.pyd"

    if (Test-Path $LibFile) {
        Copy-Item $LibFile $DestFile -Force
        Write-Host "Copied: $LibFile -> $DestFile" -ForegroundColor Green
    } else {
        throw "Error: Library file not found: $LibFile"
    }

    # Verify the file was copied
    if (Test-Path $DestFile) {
        $FileSize = (Get-Item $DestFile).Length / 1MB
        Write-Host ("Library size: {0:N2} MB" -f $FileSize) -ForegroundColor Green
    } else {
        throw "Error: Failed to copy library file"
    }

    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host "Rust modules built successfully!" -ForegroundColor Green
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Library location: $DestFile"
    Write-Host ""
    Write-Host "To test the build, run:"
    Write-Host "  python -c 'import insightora_core; print(insightora_core.__doc__)'"
    Write-Host ""

} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}

# Return to original directory
Pop-Location
