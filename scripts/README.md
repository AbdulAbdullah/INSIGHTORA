# Build Automation Scripts

This directory contains build automation scripts for the INSIGHTORA BI Platform's Rust performance modules.

## Overview

The Rust integration provides significant performance improvements for data-intensive operations. These scripts automate the build process across different platforms.

## Quick Start

### Windows

```powershell
# View all available commands
.\scripts\tasks.ps1 help

# Build Rust modules
.\scripts\tasks.ps1 build-rust

# Or use the direct build script
.\scripts\build_rust.ps1

# Verify installation
.\scripts\tasks.ps1 verify-rust
```

### Linux/Mac

```bash
# Make scripts executable (first time only)
chmod +x scripts/*.sh

# View all available commands
make help

# Build Rust modules
make build-rust

# Or use the direct build script
./scripts/build_rust.sh

# Verify installation
make verify-rust
```

## Available Scripts

### Build Scripts

#### `build_rust.sh` (Linux/Mac)
Compiles the Rust library and copies it to the Python backend directory.

**Usage:**
```bash
./scripts/build_rust.sh
```

**What it does:**
- Checks for Rust installation
- Builds Rust modules in release mode with optimizations
- Copies the compiled library to `backend/app/core/`
- Verifies the build was successful

#### `build_rust.ps1` (Windows)
Windows PowerShell version of the build script.

**Usage:**
```powershell
.\scripts\build_rust.ps1
```

### Installation Scripts

#### `install_rust.sh` (Linux/Mac)
Sets up the complete Rust development environment.

**Usage:**
```bash
./scripts/install_rust.sh
```

**What it does:**
- Installs Rust toolchain via rustup
- Installs system dependencies (build-essential, libssl-dev, etc.)
- Configures Rust for PyO3 development
- Installs rustfmt and clippy

### Task Runners

#### `tasks.ps1` (Windows)
PowerShell-based task runner providing convenient commands for common operations.

**Usage:**
```powershell
.\scripts\tasks.ps1 <command>
```

**Available commands:**
- `help` - Show all available commands
- `setup-dev` - Complete development environment setup
- `install` - Install Python dependencies
- `build-rust` - Build Rust modules
- `clean-rust` - Clean Rust build artifacts
- `test-rust` - Run Rust unit tests
- `bench-rust` - Run Rust benchmarks
- `lint-rust` - Run Rust linter (clippy)
- `format-rust` - Format Rust code
- `verify-rust` - Verify Rust module installation
- `all` - Build everything
- `clean` - Clean all artifacts

#### `Makefile` (Linux/Mac)
GNU Make-based task runner for Unix-like systems.

**Usage:**
```bash
make <target>
```

**Available targets:**
- `help` - Show all available targets
- `setup-dev` - Complete development environment setup
- `install` - Install Python dependencies
- `build-rust` - Build Rust modules
- `clean-rust` - Clean Rust build artifacts
- `test-rust` - Run Rust unit tests
- `bench-rust` - Run Rust benchmarks
- `lint-rust` - Run Rust linter
- `format-rust` - Format Rust code
- `verify-rust` - Verify Rust module installation
- `all` - Build everything
- `clean` - Clean all artifacts

## Development Workflow

### Initial Setup

**Windows:**
```powershell
# 1. Install Rust (if not already installed)
# Visit https://rustup.rs/ or run:
Invoke-WebRequest -Uri https://win.rustup.rs/x86_64 -OutFile rustup-init.exe
.\rustup-init.exe

# 2. Set up development environment
.\scripts\tasks.ps1 setup-dev
```

**Linux/Mac:**
```bash
# 1. Install Rust and dependencies
./scripts/install_rust.sh

# 2. Set up development environment
make setup-dev
```

### Regular Development

**Build after making changes:**
```bash
# Windows
.\scripts\tasks.ps1 build-rust

# Linux/Mac
make build-rust
```

**Run tests:**
```bash
# Windows
.\scripts\tasks.ps1 test-rust

# Linux/Mac
make test-rust
```

**Format code:**
```bash
# Windows
.\scripts\tasks.ps1 format-rust

# Linux/Mac
make format-rust
```

**Lint code:**
```bash
# Windows
.\scripts\tasks.ps1 lint-rust

# Linux/Mac
make lint-rust
```

## Build Output

After a successful build, the compiled library will be located at:
- **Windows:** `backend/app/core/insightora_core.pyd`
- **Linux:** `backend/app/core/insightora_core.so`
- **macOS:** `backend/app/core/insightora_core.so`

## Troubleshooting

### Rust not found

**Error:** `cargo: command not found` or `The term 'cargo' is not recognized`

**Solution:**
- Install Rust from https://rustup.rs/
- Restart your terminal after installation
- On Windows, you may need to restart your computer

### Build fails with linker errors

**Error:** Linker errors during build

**Solution (Linux):**
```bash
sudo apt-get install build-essential libssl-dev pkg-config
```

**Solution (macOS):**
```bash
brew install openssl pkg-config
```

**Solution (Windows):**
- Install Visual Studio Build Tools
- Or install Visual Studio Community with C++ development tools

### Python can't import the module

**Error:** `ModuleNotFoundError: No module named 'insightora_core'`

**Solution:**
1. Verify the build was successful
2. Check that the library file exists in `backend/app/core/`
3. Ensure you're running Python from the correct directory
4. Try: `python -c "import sys; sys.path.insert(0, 'backend/app/core'); import insightora_core"`

### Permission denied on Linux/Mac

**Error:** `Permission denied` when running scripts

**Solution:**
```bash
chmod +x scripts/*.sh
```

## Performance Optimization

The build scripts use the following optimizations:

- **Release mode:** `cargo build --release`
- **Link-time optimization (LTO):** Enabled in `Cargo.toml`
- **Single codegen unit:** For maximum optimization
- **Optimization level 3:** Maximum performance

These settings are configured in `insightora_core/Cargo.toml`:

```toml
[profile.release]
opt-level = 3
lto = true
codegen-units = 1
```

## CI/CD Integration

For automated builds in CI/CD pipelines, use:

```bash
# Install Rust (CI environment)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env

# Build
./scripts/build_rust.sh

# Test
cd insightora_core && cargo test --release
```

## Additional Resources

- [Rust Installation Guide](https://www.rust-lang.org/tools/install)
- [PyO3 Documentation](https://pyo3.rs/)
- [Cargo Book](https://doc.rust-lang.org/cargo/)
- [Project Design Document](../.kiro/specs/rust-performance-optimization/design.md)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the design document in `.kiro/specs/rust-performance-optimization/`
3. Check Rust compiler output for specific error messages
