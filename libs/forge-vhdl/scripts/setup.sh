#!/bin/bash
# VHDL-FORGE Development Environment Setup Script
# Version: 1.0
# Purpose: One-command setup for VHDL-FORGE development environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}======================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Main script
print_header "VHDL-FORGE Development Environment Setup"
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "python" ]; then
    print_error "This script must be run from the VHDL-FORGE root directory"
    print_info "Current directory: $(pwd)"
    exit 1
fi

print_success "Running from VHDL-FORGE root directory"
echo ""

# Step 1: Check GHDL
print_header "Step 1/5: Checking GHDL (VHDL Simulator)"
echo ""

if command -v ghdl &> /dev/null; then
    GHDL_VERSION=$(ghdl --version | head -n1)
    print_success "GHDL found: $GHDL_VERSION"

    # Check version (we need 4.0+)
    GHDL_MAJOR=$(ghdl --version | grep -oP 'GHDL \K[0-9]+' | head -n1)
    if [ "$GHDL_MAJOR" -ge 4 ]; then
        print_success "GHDL version is sufficient (>= 4.0)"
    else
        print_warning "GHDL version may be too old (need 4.0+)"
        print_info "Tests may fail with older GHDL versions"
    fi
else
    print_error "GHDL not found!"
    echo ""
    echo "GHDL is REQUIRED for VHDL simulation and CocoTB tests."
    echo ""
    echo "Installation instructions:"
    echo ""
    echo "  Ubuntu/Debian:"
    echo "    sudo apt-get update"
    echo "    sudo apt-get install -y ghdl ghdl-llvm"
    echo ""
    echo "  macOS:"
    echo "    brew install ghdl"
    echo ""
    echo "  Windows (WSL2):"
    echo "    Use Ubuntu instructions above"
    echo ""
    echo "After installing GHDL, re-run this script."
    exit 1
fi
echo ""

# Step 2: Check Python
print_header "Step 2/5: Checking Python"
echo ""

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python found: $PYTHON_VERSION"

    # Check version (we need 3.10+)
    PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
    if [ "$PYTHON_MINOR" -ge 10 ]; then
        print_success "Python version is sufficient (>= 3.10)"
    else
        print_warning "Python version may be too old (need 3.10+)"
        print_info "Some features may not work with older Python"
    fi
else
    print_error "Python 3 not found!"
    echo ""
    echo "Python 3.10+ is REQUIRED."
    echo ""
    echo "Installation instructions:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "  macOS: brew install python@3.11"
    echo ""
    exit 1
fi
echo ""

# Step 3: Check/Install uv
print_header "Step 3/5: Checking uv (Package Manager)"
echo ""

if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    print_success "uv found: $UV_VERSION"
else
    print_warning "uv not found - installing..."
    echo ""

    if command -v curl &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh

        # Source the new PATH
        export PATH="$HOME/.cargo/bin:$PATH"

        if command -v uv &> /dev/null; then
            UV_VERSION=$(uv --version)
            print_success "uv installed: $UV_VERSION"
        else
            print_error "uv installation failed"
            print_info "Manual installation: curl -LsSf https://astral.sh/uv/install.sh | sh"
            print_info "Then restart your shell and re-run this script"
            exit 1
        fi
    else
        print_error "curl not found - cannot install uv automatically"
        print_info "Install curl first: sudo apt-get install curl"
        exit 1
    fi
fi
echo ""

# Step 4: Install Python dependencies
print_header "Step 4/5: Installing Python Dependencies"
echo ""

print_info "Running: uv sync"
if uv sync; then
    print_success "Base dependencies installed"
else
    print_error "uv sync failed"
    print_info "Check error messages above"
    exit 1
fi
echo ""

print_info "Installing workspace packages in editable mode..."
if uv pip install -e python/forge_cocotb -e python/forge_platform -e python/forge_tools; then
    print_success "Workspace packages installed"
else
    print_error "Workspace package installation failed"
    print_info "Check error messages above"
    exit 1
fi
echo ""

# Step 5: Verify installation
print_header "Step 5/5: Verifying Installation"
echo ""

print_info "Testing package imports..."

# Test forge_cocotb
if uv run python -c "import forge_cocotb" 2>/dev/null; then
    print_success "forge_cocotb import successful"
else
    print_error "forge_cocotb import failed"
    INSTALL_FAILED=1
fi

# Test forge_platform
if uv run python -c "import forge_platform" 2>/dev/null; then
    print_success "forge_platform import successful"
else
    print_error "forge_platform import failed"
    INSTALL_FAILED=1
fi

# Test forge_tools
if uv run python -c "import forge_tools" 2>/dev/null; then
    print_success "forge_tools import successful"
else
    print_error "forge_tools import failed"
    INSTALL_FAILED=1
fi

if [ -n "$INSTALL_FAILED" ]; then
    echo ""
    print_error "Some imports failed - setup incomplete"
    print_info "Try running: uv pip install -e python/forge_cocotb -e python/forge_platform -e python/forge_tools"
    exit 1
fi

echo ""
print_info "Testing CocoTB test runner..."
if uv run python cocotb_tests/run.py --list > /dev/null 2>&1; then
    print_success "CocoTB test runner working"

    # Show test count
    TEST_COUNT=$(uv run python cocotb_tests/run.py --list 2>/dev/null | grep -c "^  -" || echo "unknown")
    print_info "Found $TEST_COUNT available tests"
else
    print_warning "CocoTB test runner check failed (may be normal if VHDL files missing)"
    print_info "This is expected for fresh clones without VHDL files"
fi

echo ""
print_header "Setup Complete!"
echo ""
print_success "VHDL-FORGE development environment is ready!"
echo ""
echo "Next steps:"
echo ""
echo "  1. Verify setup:"
echo "     ./scripts/validate_setup.sh"
echo ""
echo "  2. List available tests:"
echo "     uv run python cocotb_tests/run.py --list"
echo ""
echo "  3. Run a test (if VHDL files exist):"
echo "     uv run python cocotb_tests/run.py forge_util_clk_divider"
echo ""
echo "  4. Start gathering requirements for a new component:"
echo "     Type: /gather-requirements"
echo "     (in Claude Code)"
echo ""
echo "  5. Read the documentation:"
echo "     - Quick start: cat llms.txt"
echo "     - Complete guide: cat CLAUDE.md"
echo "     - Setup guide: cat SPEC.md"
echo ""
print_info "For troubleshooting, see: docs/DIAGNOSTIC_SYSTEM_PROMPT.md"
echo ""
