#!/bin/bash
# VHDL-FORGE Setup Validation Script
# Version: 1.0
# Purpose: Verify that VHDL-FORGE development environment is correctly configured

# Note: Not using 'set -e' because we want to continue checking even if some tests fail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

# Helper functions
print_header() {
    echo -e "${BLUE}======================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================================================${NC}"
}

check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((CHECKS_PASSED++))
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
    ((CHECKS_FAILED++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((CHECKS_WARNING++))
}

print_info() {
    echo -e "${BLUE}   $1${NC}"
}

# Main validation
print_header "VHDL-FORGE Setup Validation"
echo ""
echo "Running comprehensive environment checks..."
echo ""

# Check 1: GHDL
echo -n "Checking GHDL... "
if command -v ghdl &> /dev/null; then
    GHDL_VERSION=$(ghdl --version | head -n1)
    check_pass "GHDL found: $GHDL_VERSION"
else
    check_fail "GHDL not found"
    print_info "Install: sudo apt-get install ghdl (Ubuntu) or brew install ghdl (macOS)"
fi

# Check 2: Python
echo -n "Checking Python... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)' 2>/dev/null || echo "0")

    if [ "$PYTHON_MINOR" -ge 10 ]; then
        check_pass "$PYTHON_VERSION"
    else
        check_warn "$PYTHON_VERSION (need 3.10+)"
    fi
else
    check_fail "Python 3 not found"
    print_info "Install: sudo apt-get install python3 (Ubuntu) or brew install python (macOS)"
fi

# Check 3: uv
echo -n "Checking uv... "
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    check_pass "$UV_VERSION"
else
    check_fail "uv not found"
    print_info "Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

# Check 4: Virtual environment
echo -n "Checking virtual environment... "
if [ -d ".venv" ]; then
    check_pass ".venv exists"
else
    check_fail ".venv not found"
    print_info "Run: uv sync"
fi

# Check 5: Package structure
echo -n "Checking package structure... "
STRUCTURE_OK=1

if [ ! -d "python/forge_cocotb/forge_cocotb" ]; then
    check_fail "forge_cocotb structure incorrect"
    print_info "Expected: python/forge_cocotb/forge_cocotb/__init__.py"
    STRUCTURE_OK=0
elif [ ! -d "python/forge_platform/forge_platform" ]; then
    check_fail "forge_platform structure incorrect"
    print_info "Expected: python/forge_platform/forge_platform/__init__.py"
    STRUCTURE_OK=0
elif [ ! -d "python/forge_tools/forge_tools" ]; then
    check_fail "forge_tools structure incorrect"
    print_info "Expected: python/forge_tools/forge_tools/__init__.py"
    STRUCTURE_OK=0
else
    check_pass "All packages have correct structure"
fi

# Check 6: pyproject.toml configs
echo -n "Checking pyproject.toml files... "
PYPROJECT_OK=1

if ! grep -q 'packages = \["forge_cocotb"\]' python/forge_cocotb/pyproject.toml 2>/dev/null; then
    check_fail "forge_cocotb/pyproject.toml incorrect"
    print_info "Should have: packages = [\"forge_cocotb\"]"
    PYPROJECT_OK=0
elif ! grep -q 'packages = \["forge_platform"\]' python/forge_platform/pyproject.toml 2>/dev/null; then
    check_fail "forge_platform/pyproject.toml incorrect"
    print_info "Should have: packages = [\"forge_platform\"]"
    PYPROJECT_OK=0
elif ! grep -q 'packages = \["forge_tools"\]' python/forge_tools/pyproject.toml 2>/dev/null; then
    check_fail "forge_tools/pyproject.toml incorrect"
    print_info "Should have: packages = [\"forge_tools\"]"
    PYPROJECT_OK=0
else
    check_pass "All pyproject.toml files correct"
fi

# Check 7-9: Package imports
if [ -d ".venv" ]; then
    echo -n "Checking forge_cocotb import... "
    if uv run python -c "import forge_cocotb" 2>/dev/null; then
        check_pass "forge_cocotb imports successfully"
    else
        check_fail "Cannot import forge_cocotb"
        print_info "Run: uv pip install -e python/forge_cocotb"
    fi

    echo -n "Checking forge_platform import... "
    if uv run python -c "import forge_platform" 2>/dev/null; then
        check_pass "forge_platform imports successfully"
    else
        check_fail "Cannot import forge_platform"
        print_info "Run: uv pip install -e python/forge_platform"
    fi

    echo -n "Checking forge_tools import... "
    if uv run python -c "import forge_tools" 2>/dev/null; then
        check_pass "forge_tools imports successfully"
    else
        check_fail "Cannot import forge_tools"
        print_info "Run: uv pip install -e python/forge_tools"
    fi
else
    check_warn "Skipping import tests (no .venv)"
    ((CHECKS_WARNING+=2))  # Account for skipped tests
fi

# Check 10: CocoTB
if [ -d ".venv" ]; then
    echo -n "Checking CocoTB... "
    if uv run python -c "import cocotb" 2>/dev/null; then
        COCOTB_VERSION=$(uv run python -c "import cocotb; print(cocotb.__version__)" 2>/dev/null)
        check_pass "CocoTB v$COCOTB_VERSION"
    else
        check_fail "CocoTB not found"
        print_info "Run: uv sync"
    fi
fi

# Check 11: Test runner
if [ -d ".venv" ]; then
    echo -n "Checking test runner... "
    if uv run python cocotb_tests/run.py --list > /dev/null 2>&1; then
        TEST_COUNT=$(uv run python cocotb_tests/run.py --list 2>/dev/null | grep -c "^  -" || echo "0")
        check_pass "Test runner works ($TEST_COUNT tests available)"
    else
        check_fail "Test runner failed"
        print_info "Try: uv run python cocotb_tests/run.py --list"
    fi
fi

# Check 12: Documentation
echo -n "Checking documentation... "
DOC_MISSING=0

[ -f "CLAUDE.md" ] || DOC_MISSING=1
[ -f "llms.txt" ] || DOC_MISSING=1
[ -f "SPEC.md" ] || DOC_MISSING=1
[ -f "workflow/README.md" ] || DOC_MISSING=1

if [ "$DOC_MISSING" -eq 0 ]; then
    check_pass "Core documentation present"
else
    check_warn "Some documentation files missing"
fi

# Check 13: Agent definitions
echo -n "Checking agent definitions... "
if [ -d ".claude/agents" ]; then
    AGENT_COUNT=$(find .claude/agents -name "agent.md" | wc -l)
    if [ "$AGENT_COUNT" -ge 3 ]; then
        check_pass "$AGENT_COUNT agent definitions found"
    else
        check_warn "Only $AGENT_COUNT agent definitions (expected 3+)"
    fi
else
    check_fail ".claude/agents directory missing"
fi

# Check 14: Slash commands
echo -n "Checking slash commands... "
if [ -f ".claude/commands/gather-requirements.md" ]; then
    check_pass "gather-requirements command present"
else
    check_warn "gather-requirements command missing"
fi

# Check 15: Workflow structure
echo -n "Checking workflow structure... "
if [ -d "workflow/specs/pending" ]; then
    SPEC_COUNT=$(find workflow/specs/pending -name "*.md" -not -name "README.md" | wc -l)
    check_pass "Workflow structure present ($SPEC_COUNT example specs)"
else
    check_warn "workflow/specs/pending missing"
fi

# Summary
echo ""
print_header "Validation Summary"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All critical checks passed!${NC}"
else
    echo -e "${RED}❌ $CHECKS_FAILED check(s) failed${NC}"
fi

if [ $CHECKS_WARNING -gt 0 ]; then
    echo -e "${YELLOW}⚠️  $CHECKS_WARNING warning(s)${NC}"
fi

echo -e "${BLUE}ℹ️  $CHECKS_PASSED check(s) passed${NC}"
echo ""

# Final verdict
if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}Environment is ready for development!${NC}"
    echo ""
    echo "Next steps:"
    echo "  - List tests: uv run python cocotb_tests/run.py --list"
    echo "  - Run a test: uv run python cocotb_tests/run.py <test_name>"
    echo "  - Read docs: cat CLAUDE.md"
    echo "  - Start coding: /gather-requirements (in Claude Code)"
    echo ""
    exit 0
else
    echo -e "${RED}Environment has issues - please fix errors above${NC}"
    echo ""
    echo "Common fixes:"
    echo "  - Missing GHDL: sudo apt-get install ghdl (Ubuntu) or brew install ghdl (macOS)"
    echo "  - Missing packages: ./scripts/setup.sh"
    echo "  - Import errors: uv pip install -e python/forge_cocotb -e python/forge_platform -e python/forge_tools"
    echo ""
    echo "For detailed diagnostics:"
    echo "  - See: docs/DIAGNOSTIC_SYSTEM_PROMPT.md"
    echo "  - See: docs/SETUP_IMPROVEMENTS.md"
    echo ""
    exit 1
fi
