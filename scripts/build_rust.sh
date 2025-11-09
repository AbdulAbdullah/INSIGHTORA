#!/bin/bash
# Build script for Rust performance modules (Linux/Mac)
# This script compiles the Rust library and copies it to the Python backend

set -e  # Exit on error

echo "========================================="
echo "Building Rust Performance Modules"
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RUST_DIR="$PROJECT_ROOT/insightora_core"
BACKEND_DIR="$PROJECT_ROOT/backend/app/core"

# Check if Rust is installed
if ! command -v cargo &> /dev/null; then
    echo -e "${RED}Error: Rust is not installed${NC}"
    echo "Please run: ./scripts/install_rust.sh"
    exit 1
fi

echo -e "${YELLOW}Rust version:${NC}"
rustc --version
cargo --version
echo ""

# Navigate to Rust directory
cd "$RUST_DIR"

# Clean previous builds (optional, comment out for faster incremental builds)
# echo -e "${YELLOW}Cleaning previous builds...${NC}"
# cargo clean

# Build in release mode with optimizations
echo -e "${YELLOW}Building Rust modules in release mode...${NC}"
cargo build --release

if [ $? -ne 0 ]; then
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi

echo -e "${GREEN}Build successful!${NC}"
echo ""

# Create backend core directory if it doesn't exist
mkdir -p "$BACKEND_DIR"

# Determine OS and copy the appropriate library file
echo -e "${YELLOW}Copying compiled library to Python backend...${NC}"

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    LIB_FILE="$RUST_DIR/target/release/libinsightora_core.so"
    DEST_FILE="$BACKEND_DIR/insightora_core.so"
    
    if [ -f "$LIB_FILE" ]; then
        cp "$LIB_FILE" "$DEST_FILE"
        echo -e "${GREEN}Copied: $LIB_FILE -> $DEST_FILE${NC}"
    else
        echo -e "${RED}Error: Library file not found: $LIB_FILE${NC}"
        exit 1
    fi
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    LIB_FILE="$RUST_DIR/target/release/libinsightora_core.dylib"
    DEST_FILE="$BACKEND_DIR/insightora_core.so"
    
    if [ -f "$LIB_FILE" ]; then
        cp "$LIB_FILE" "$DEST_FILE"
        echo -e "${GREEN}Copied: $LIB_FILE -> $DEST_FILE${NC}"
    else
        echo -e "${RED}Error: Library file not found: $LIB_FILE${NC}"
        exit 1
    fi
    
else
    echo -e "${RED}Error: Unsupported OS: $OSTYPE${NC}"
    echo "This script supports Linux and macOS. For Windows, use build_rust.ps1"
    exit 1
fi

# Verify the file was copied
if [ -f "$DEST_FILE" ]; then
    FILE_SIZE=$(du -h "$DEST_FILE" | cut -f1)
    echo -e "${GREEN}Library size: $FILE_SIZE${NC}"
else
    echo -e "${RED}Error: Failed to copy library file${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Rust modules built successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Library location: $DEST_FILE"
echo ""
echo "To test the build, run:"
echo "  python -c 'import insightora_core; print(insightora_core.__doc__)'"
echo ""
