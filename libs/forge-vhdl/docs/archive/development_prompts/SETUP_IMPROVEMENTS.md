# VHDL Forge Setup Improvements

**Date:** 2025-11-09
**Purpose:** Document issues discovered during initial setup and recommended fixes for template repository

---

## Executive Summary

During initial setup of the vhdl-forge-3v1-claude project, several structural issues were identified that prevent the project from working out-of-the-box. This document details these issues and provides actionable fixes to improve the developer experience.

---

## Critical Issues Discovered

### 1. Python Package Structure Incompatibility ⚠️ BLOCKING

**Issue:**
The Python workspace packages (`forge_cocotb`, `forge_platform`, `forge_tools`) have an incorrect directory structure that prevents Python from importing them.

**Current Structure (BROKEN):**
```
python/
├── forge_cocotb/
│   ├── __init__.py          # ❌ Files directly in package directory
│   ├── runner.py
│   ├── test_base.py
│   └── pyproject.toml
├── forge_platform/
│   ├── __init__.py          # ❌ Same issue
│   └── pyproject.toml
└── forge_tools/
    ├── __init__.py          # ❌ Same issue
    └── pyproject.toml
```

**Expected Structure (CORRECT):**
```
python/
├── forge_cocotb/
│   ├── forge_cocotb/        # ✅ Module directory with package name
│   │   ├── __init__.py
│   │   ├── runner.py
│   │   └── test_base.py
│   └── pyproject.toml
├── forge_platform/
│   ├── forge_platform/      # ✅ Module directory
│   │   └── __init__.py
│   └── pyproject.toml
└── forge_tools/
    ├── forge_tools/         # ✅ Module directory
    │   └── __init__.py
    └── pyproject.toml
```

**Impact:**
- `ModuleNotFoundError: No module named 'forge_cocotb'` when running tests
- Cannot execute `cocotb_tests/run.py --list`
- Blocks all CocoTB test execution
- Blocks all agent workflows that depend on testing

**Error Message:**
```
$ uv run python cocotb_tests/run.py --list
Traceback (most recent call last):
  File "/home/user/vhdl-forge-3v1-claude/cocotb_tests/run.py", line 24, in <module>
    from forge_cocotb.runner import main as runner_main
ModuleNotFoundError: No module named 'forge_cocotb'
```

**Fix:**
```bash
# For each package (forge_cocotb, forge_platform, forge_tools):
cd python/forge_cocotb
mkdir -p forge_cocotb
mv *.py forge_cocotb/
# Keep pyproject.toml and README.md in parent directory

# Update pyproject.toml [tool.hatch.build.targets.wheel] section:
[tool.hatch.build.targets.wheel]
packages = ["forge_cocotb"]  # Changed from ["."]
```

**Root Cause:**
The `pyproject.toml` files specify `packages = ["."]` which tells hatchling to treat the root directory as the package, but Python's import system requires a subdirectory matching the package name.

---

### 2. Missing GHDL Installation Instructions

**Issue:**
The repository README and setup documentation do not mention GHDL as a required dependency.

**Impact:**
- New contributors cannot run tests without discovering this requirement through trial and error
- CocoTB tests fail silently or with unclear error messages

**Current Documentation:**
- No mention of GHDL in README.md
- No installation instructions in CLAUDE.md

**Recommended Fix:**

Add to `README.md`:

```markdown
## Prerequisites

### System Dependencies

**GHDL (VHDL Simulator)**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y ghdl ghdl-llvm

# macOS
brew install ghdl

# Windows
# Download installer from: https://github.com/ghdl/ghdl/releases
```

**Python 3.10+**
```bash
python3 --version  # Should be 3.10 or higher
```

**uv (Python Package Manager)**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
```

Add to `CLAUDE.md` (Development Workflow section):

```markdown
## Environment Setup

Before running any agents or tests, ensure these dependencies are installed:

1. **GHDL** - VHDL simulator (required for CocoTB tests)
2. **Python 3.10+** - Language runtime
3. **uv** - Package manager (faster than pip)

See README.md for installation instructions.
```

---

### 3. UV Workspace Installation Not Automatic

**Issue:**
Running `uv sync` installs shared dependencies but does NOT install the workspace member packages in editable mode.

**Current Behavior:**
```bash
$ uv sync
# Installs cocotb, pytest, etc.
# Does NOT install forge_cocotb, forge_platform, forge_tools
```

**Expected Behavior:**
```bash
$ uv sync
# Should install everything including workspace members
```

**Workaround Required:**
```bash
uv sync
uv pip install -e python/forge_cocotb -e python/forge_platform -e python/forge_tools
```

**Recommended Fix:**

This may be a uv workspace configuration issue or a misunderstanding of how uv workspaces work. Research needed:

1. Check if `uv sync --all-packages` flag exists
2. Investigate if workspace members need `[build-system]` sections
3. Consider adding post-install script

Alternative: Add setup script:

```bash
#!/bin/bash
# scripts/setup.sh

set -e

echo "Installing VHDL Forge development environment..."

# Check GHDL
if ! command -v ghdl &> /dev/null; then
    echo "❌ GHDL not found. Please install GHDL first."
    exit 1
fi

# Sync dependencies
echo "📦 Installing dependencies..."
uv sync --all-extras

# Install workspace packages
echo "📦 Installing workspace packages in editable mode..."
uv pip install -e python/forge_cocotb
uv pip install -e python/forge_platform
uv pip install -e python/forge_tools

echo "✅ Setup complete!"
echo ""
echo "Run tests with:"
echo "  uv run python cocotb_tests/run.py --list"
```

---

### 4. Package Import Test Not in Setup Validation

**Issue:**
No automated check verifies the Python package structure is correct after installation.

**Recommended Fix:**

Add to `scripts/validate_setup.sh`:

```bash
#!/bin/bash
# scripts/validate_setup.sh

set -e

echo "Validating VHDL Forge setup..."

# Check GHDL
echo -n "Checking GHDL... "
if command -v ghdl &> /dev/null; then
    GHDL_VERSION=$(ghdl --version | head -n1)
    echo "✅ $GHDL_VERSION"
else
    echo "❌ Not found"
    exit 1
fi

# Check Python
echo -n "Checking Python... "
PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION"

# Check uv
echo -n "Checking uv... "
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    echo "✅ $UV_VERSION"
else
    echo "❌ Not found"
    exit 1
fi

# Check package imports
echo -n "Checking forge_cocotb import... "
if .venv/bin/python -c "import forge_cocotb" 2>/dev/null; then
    echo "✅"
else
    echo "❌ Cannot import forge_cocotb"
    exit 1
fi

echo -n "Checking forge_platform import... "
if .venv/bin/python -c "import forge_platform" 2>/dev/null; then
    echo "✅"
else
    echo "❌ Cannot import forge_platform"
    exit 1
fi

echo -n "Checking forge_tools import... "
if .venv/bin/python -c "import forge_tools" 2>/dev/null; then
    echo "✅"
else
    echo "❌ Cannot import forge_tools"
    exit 1
fi

# Check CocoTB
echo -n "Checking CocoTB... "
if .venv/bin/python -c "import cocotb" 2>/dev/null; then
    COCOTB_VERSION=$(.venv/bin/python -c "import cocotb; print(cocotb.__version__)")
    echo "✅ v$COCOTB_VERSION"
else
    echo "❌ Not found"
    exit 1
fi

echo ""
echo "✅ All checks passed! Environment is ready."
```

---

## Pre-Conditions Checklist

Based on the setup exploration, here are the verified pre-conditions for running the agents:

### System Requirements
- ✅ GHDL 4.1.0+ (installed via apt-get)
- ✅ Python 3.11.14 (verified)
- ✅ uv 0.8.17 (verified)

### Python Environment
- ✅ Virtual environment created (`.venv/`)
- ✅ Core dependencies installed (cocotb, pytest, pyyaml)
- ❌ **BLOCKING:** Workspace packages NOT importable due to structure issue

### Project Structure
- ✅ Agent definitions present in `.claude/agents/`:
  - `forge-new-component`
  - `forge-vhdl-component-generator`
  - `cocotb-progressive-test-designer`
  - `cocotb-progressive-test-runner`
- ✅ CocoTB test infrastructure present (`cocotb_tests/`)
- ✅ VHDL components present (`vhdl/`)

### Blocking Issues
1. **Python package structure** - Must be fixed before ANY tests can run
2. **Import failures** - Prevents `cocotb_tests/run.py` from executing

---

## Recommended Action Plan

### Phase 1: Fix Package Structure (CRITICAL)
1. Restructure `python/forge_cocotb/`, `python/forge_platform/`, `python/forge_tools/`
2. Update `pyproject.toml` files to match new structure
3. Test imports: `python -c "import forge_cocotb; import forge_platform; import forge_tools"`

### Phase 2: Document Setup (HIGH PRIORITY)
1. Add GHDL installation to README.md
2. Create `scripts/setup.sh` for one-command setup
3. Create `scripts/validate_setup.sh` for verification

### Phase 3: Validate Workflow (MEDIUM PRIORITY)
1. Run `cocotb_tests/run.py --list` successfully
2. Run a simple P1 test (e.g., clock divider)
3. Document expected output in README

### Phase 4: CI/CD Integration (OPTIONAL)
1. Add GitHub Actions workflow for setup validation
2. Test on Ubuntu, macOS, Windows (if applicable)
3. Cache dependencies for faster CI runs

---

## Testing the Fix

Once the package structure is corrected, verify with:

```bash
# 1. Clean install
rm -rf .venv
uv sync
uv pip install -e python/forge_cocotb -e python/forge_platform -e python/forge_tools

# 2. Verify imports
.venv/bin/python -c "import forge_cocotb; print('✅ forge_cocotb')"
.venv/bin/python -c "import forge_platform; print('✅ forge_platform')"
.venv/bin/python -c "import forge_tools; print('✅ forge_tools')"

# 3. List tests
uv run python cocotb_tests/run.py --list

# Expected output:
# Available test configurations:
# - clock_divider
# - hierarchical_encoder
# ... (full list of tests)
```

---

## Impact on Development Workflow

### Before Fix (BROKEN)
```
User clones repo
  ↓
Runs: uv sync
  ↓
❌ Tries: cocotb_tests/run.py --list
  ↓
❌ ERROR: ModuleNotFoundError
  ↓
Confused, gives up or wastes time debugging
```

### After Fix (WORKING)
```
User clones repo
  ↓
Runs: scripts/setup.sh
  ↓
Runs: scripts/validate_setup.sh
  ↓
✅ All checks pass
  ↓
Runs: cocotb_tests/run.py --list
  ↓
✅ See available tests
  ↓
Can immediately start development
```

---

## Additional Observations

### Positive Findings
1. **GHDL Installation**: Works perfectly via apt-get (no issues)
2. **uv Package Manager**: Fast and reliable
3. **Project Documentation**: Comprehensive and well-structured (CLAUDE.md, llms.txt)
4. **Agent Architecture**: Well-organized in `.claude/agents/`

### Minor Issues (Non-Blocking)
1. No `.gitignore` entry for `sim_build/` (GHDL simulation outputs)
2. No example "hello world" test to verify setup
3. `cocotb_tests/run.py --help` not documented

---

## References

### Related Files
- `pyproject.toml` - Workspace configuration
- `python/forge_cocotb/pyproject.toml` - Package configuration (needs fix)
- `cocotb_tests/run.py` - Test runner (fails due to import issues)
- `CLAUDE.md` - Main development guide (needs GHDL prerequisite section)

### Documentation to Update
1. `README.md` - Add prerequisites section
2. `CLAUDE.md` - Add environment setup section
3. Create: `docs/SETUP_GUIDE.md` (detailed walkthrough)
4. Create: `scripts/setup.sh` (automated setup)
5. Create: `scripts/validate_setup.sh` (health check)

---

## Version History

- **v1.0** (2025-11-09): Initial findings from setup exploration
  - Identified package structure issue
  - Documented GHDL installation gap
  - Created comprehensive action plan

---

**Maintainer Note:**
This document should be used to update the template repository to prevent future users from encountering these setup issues. Priority: **CRITICAL** - blocks all development workflows.
