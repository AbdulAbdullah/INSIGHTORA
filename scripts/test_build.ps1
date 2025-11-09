# Test script to verify build automation works correctly
# This script tests the build process without modifying the actual build

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Testing Build Automation Scripts" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$TestsPassed = 0
$TestsFailed = 0

function Test-Command {
    param(
        [string]$Name,
        [scriptblock]$Command
    )
    
    Write-Host "Testing: $Name..." -ForegroundColor Yellow
    try {
        & $Command
        Write-Host "  PASS" -ForegroundColor Green
        $script:TestsPassed++
        return $true
    } catch {
        Write-Host "  FAIL: $_" -ForegroundColor Red
        $script:TestsFailed++
        return $false
    }
}

# Test 1: Check if Rust is installed
Test-Command "Rust installation" {
    $null = Get-Command cargo -ErrorAction Stop
    $null = Get-Command rustc -ErrorAction Stop
}

# Test 2: Check if scripts exist
Test-Command "Build scripts exist" {
    if (-not (Test-Path "scripts\build_rust.ps1")) { throw "build_rust.ps1 not found" }
    if (-not (Test-Path "scripts\tasks.ps1")) { throw "tasks.ps1 not found" }
    if (-not (Test-Path "scripts\build_rust.sh")) { throw "build_rust.sh not found" }
    if (-not (Test-Path "scripts\install_rust.sh")) { throw "install_rust.sh not found" }
}

# Test 3: Check if Cargo.toml is valid
Test-Command "Cargo.toml validation" {
    Push-Location insightora_core
    cargo check --quiet 2>$null
    Pop-Location
}

# Test 4: Check if Makefile exists
Test-Command "Makefile exists" {
    if (-not (Test-Path "Makefile")) { throw "Makefile not found" }
}

# Test 5: Test tasks.ps1 help command
Test-Command "tasks.ps1 help command" {
    $output = & ".\scripts\tasks.ps1" help 2>&1
    if ($output -notmatch "INSIGHTORA") { throw "Help output invalid" }
}

# Test 6: Verify Rust project structure
Test-Command "Rust project structure" {
    if (-not (Test-Path "insightora_core\src\lib.rs")) { throw "lib.rs not found" }
    if (-not (Test-Path "insightora_core\Cargo.toml")) { throw "Cargo.toml not found" }
}

# Test 7: Check if Python can find the module (if built)
Test-Command "Python module import (if built)" {
    if (Test-Path "backend\app\core\insightora_core.pyd") {
        $testScript = @"
import sys
sys.path.insert(0, 'backend/app/core')
import insightora_core
assert hasattr(insightora_core, 'configure')
assert hasattr(insightora_core, 'get_config')
"@
        python -c $testScript
    } else {
        Write-Host "    (Module not built yet, skipping)" -ForegroundColor Gray
    }
}

# Test 8: Verify README documentation exists
Test-Command "Documentation exists" {
    if (-not (Test-Path "scripts\README.md")) { throw "scripts/README.md not found" }
    if (-not (Test-Path "README.md")) { throw "README.md not found" }
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Test Results" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Passed: $TestsPassed" -ForegroundColor Green
Write-Host "Failed: $TestsFailed" -ForegroundColor Red
Write-Host ""

if ($TestsFailed -eq 0) {
    Write-Host "All tests passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Build automation is ready to use." -ForegroundColor Cyan
    Write-Host "Run: .\scripts\tasks.ps1 build-rust" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "Some tests failed. Please review the errors above." -ForegroundColor Red
    exit 1
}
