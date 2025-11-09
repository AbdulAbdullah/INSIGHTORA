# Makefile for INSIGHTORA BI Platform
# Provides convenient commands for building, testing, and running the application

.PHONY: help install build-rust clean-rust test-rust run-backend setup-dev all

# Default target
help:
	@echo "INSIGHTORA BI Platform - Available Commands"
	@echo "==========================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup-dev      - Set up complete development environment"
	@echo "  make install        - Install Python dependencies"
	@echo "  make install-rust   - Install Rust toolchain and dependencies"
	@echo ""
	@echo "Rust Build Commands:"
	@echo "  make build-rust     - Build Rust performance modules"
	@echo "  make clean-rust     - Clean Rust build artifacts"
	@echo "  make test-rust      - Run Rust unit tests"
	@echo "  make bench-rust     - Run Rust benchmarks"
	@echo "  make lint-rust      - Run Rust linter (clippy)"
	@echo "  make format-rust    - Format Rust code"
	@echo ""
	@echo "Python Backend Commands:"
	@echo "  make run-backend    - Start FastAPI development server"
	@echo "  make test-backend   - Run Python tests"
	@echo ""
	@echo "Combined Commands:"
	@echo "  make all            - Build everything (Rust + Python setup)"
	@echo "  make clean          - Clean all build artifacts"
	@echo ""

# Complete development environment setup
setup-dev:
	@echo "Setting up development environment..."
	@chmod +x scripts/*.sh
	@./scripts/install_rust.sh
	@$(MAKE) install
	@$(MAKE) build-rust
	@echo ""
	@echo "Development environment ready!"

# Install Python dependencies
install:
	@echo "Installing Python dependencies..."
	@pip install -r backend/requirements/base.txt
	@pip install -r backend/requirements/dev.txt || true

# Install Rust toolchain
install-rust:
	@echo "Installing Rust toolchain..."
	@chmod +x scripts/install_rust.sh
	@./scripts/install_rust.sh

# Build Rust modules
build-rust:
	@echo "Building Rust performance modules..."
ifeq ($(OS),Windows_NT)
	@powershell -ExecutionPolicy Bypass -File scripts/build_rust.ps1
else
	@chmod +x scripts/build_rust.sh
	@./scripts/build_rust.sh
endif

# Clean Rust build artifacts
clean-rust:
	@echo "Cleaning Rust build artifacts..."
	@cd insightora_core && cargo clean
	@rm -f backend/app/core/insightora_core.so
	@rm -f backend/app/core/insightora_core.pyd
	@echo "Rust artifacts cleaned"

# Run Rust unit tests
test-rust:
	@echo "Running Rust unit tests..."
	@cd insightora_core && cargo test --release

# Run Rust benchmarks
bench-rust:
	@echo "Running Rust benchmarks..."
	@cd insightora_core && cargo bench

# Run Rust linter
lint-rust:
	@echo "Running Rust linter (clippy)..."
	@cd insightora_core && cargo clippy -- -D warnings

# Format Rust code
format-rust:
	@echo "Formatting Rust code..."
	@cd insightora_core && cargo fmt

# Check Rust code formatting
check-format-rust:
	@echo "Checking Rust code formatting..."
	@cd insightora_core && cargo fmt -- --check

# Start FastAPI development server
run-backend:
	@echo "Starting FastAPI development server..."
	@cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run Python tests
test-backend:
	@echo "Running Python tests..."
	@cd backend && pytest tests/ -v

# Build everything
all: install build-rust
	@echo ""
	@echo "All components built successfully!"

# Clean all build artifacts
clean: clean-rust
	@echo "Cleaning Python cache..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "All artifacts cleaned"

# Verify Rust installation
verify-rust:
	@echo "Verifying Rust installation..."
	@cd insightora_core && cargo build --release
	@python -c "import sys; sys.path.insert(0, 'backend/app/core'); import insightora_core; print('✓ Rust module imported successfully'); print(insightora_core.__doc__)"

# Development workflow - rebuild and test
dev: build-rust verify-rust
	@echo ""
	@echo "Development build complete and verified!"
