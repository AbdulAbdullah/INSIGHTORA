#!/bin/bash
# Development environment setup script for Rust
# Installs Rust toolchain and required dependencies

set -e  # Exit on error

echo "========================================="
echo "Rust Development Environment Setup"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Rust is already installed
if command -v cargo &> /dev/null; then
    echo -e "${YELLOW}Rust is already installed:${NC}"
    rustc --version
    cargo --version
    echo ""
    read -p "Do you want to update Rust? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Updating Rust...${NC}"
        rustup update
        echo -e "${GREEN}Rust updated successfully!${NC}"
    fi
else
    # Install Rust using rustup
    echo -e "${YELLOW}Installing Rust...${NC}"
    echo "This will download and install the official Rust toolchain."
    echo ""
    
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    
    # Source cargo environment
    source "$HOME/.cargo/env"
    
    echo -e "${GREEN}Rust installed successfully!${NC}"
    rustc --version
    cargo --version
fi

echo ""
echo -e "${YELLOW}Installing system dependencies...${NC}"

# Detect OS and install dependencies
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "Detected Linux system"
    
    # Check for package manager
    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        echo "Installing build dependencies (requires sudo)..."
        sudo apt-get update
        sudo apt-get install -y \
            build-essential \
            libssl-dev \
            pkg-config \
            python3-dev
        
    elif command -v yum &> /dev/null; then
        # RHEL/CentOS/Fedora
        echo "Installing build dependencies (requires sudo)..."
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y \
            openssl-devel \
            pkg-config \
            python3-devel
        
    elif command -v pacman &> /dev/null; then
        # Arch Linux
        echo "Installing build dependencies (requires sudo)..."
        sudo pacman -S --noconfirm \
            base-devel \
            openssl \
            pkg-config \
            python
    else
        echo -e "${YELLOW}Warning: Unknown package manager. Please install build-essential, libssl-dev, and pkg-config manually.${NC}"
    fi
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Detected macOS system"
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}Homebrew not found. Installing Homebrew...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    echo "Installing build dependencies..."
    brew install openssl pkg-config
    
else
    echo -e "${YELLOW}Warning: Unsupported OS: $OSTYPE${NC}"
    echo "Please install build dependencies manually."
fi

echo ""
echo -e "${YELLOW}Configuring Rust for PyO3...${NC}"

# Ensure we have the stable toolchain
rustup default stable

# Add useful components
rustup component add rustfmt clippy

echo -e "${GREEN}Rust components installed:${NC}"
rustup component list --installed

echo ""
echo -e "${YELLOW}Verifying Python development environment...${NC}"

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}$PYTHON_VERSION${NC}"
    
    # Check if pip is available
    if command -v pip3 &> /dev/null; then
        echo -e "${GREEN}pip3 is available${NC}"
    else
        echo -e "${YELLOW}Warning: pip3 not found. You may need to install it.${NC}"
    fi
else
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Restart your terminal or run: source \$HOME/.cargo/env"
echo "  2. Build the Rust modules: ./scripts/build_rust.sh"
echo "  3. Run tests: cd insightora_core && cargo test"
echo ""
echo "Useful commands:"
echo "  cargo build --release    # Build optimized release version"
echo "  cargo test               # Run Rust tests"
echo "  cargo clippy             # Run linter"
echo "  cargo fmt                # Format code"
echo ""
