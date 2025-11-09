# VHDL-FORGE Cloud Setup with GHDL

**Version:** 1.0
**Purpose:** One-command setup for cloud environments with full GHDL support
**Environment:** Claude Code Web, GitHub Codespaces, any containerized environment
**Target:** Complete VHDL development + testing environment in under 2 minutes

---

## Quick Start

**Copy this entire prompt and paste into Claude Code Web:**

```markdown
You are setting up the VHDL-FORGE development environment in a cloud container.

Run this single command to auto-install GHDL, setup Python packages, and validate the environment:

```bash
uv run python scripts/cloud_setup_with_ghdl.py
```

This script will:
1. ✅ Check/install GHDL (VHDL simulator)
2. ✅ Check/install UV (package manager)
3. ✅ Run uv sync (create .venv)
4. ✅ Install workspace packages (editable mode)
5. ✅ Verify all imports work
6. ✅ Test the test runner
7. ✅ Run a sample VHDL simulation

After running, provide a summary of:
- What was installed
- What tests are available
- Whether GHDL simulations work
- Next steps for the user
```

---

## What This Does

### Automated Actions

The setup script (`scripts/cloud_setup_with_ghdl.py`) will automatically:

1. **Detect Environment**
   - Check if GHDL is installed
   - Verify Python version (3.10+)
   - Confirm UV package manager available

2. **Install Missing Components**
   - Install GHDL via apt-get (if missing and has sudo)
   - Install UV via curl (if missing)
   - Create virtual environment
   - Install all Python packages in editable mode

3. **Validate Installation**
   - Test package imports
   - Verify test runner works
   - Run sample VHDL simulation
   - Report success/failure

### Expected Output

**Successful Setup:**
```
======================================================================
VHDL-FORGE Cloud Setup with GHDL
======================================================================

✅ Running from VHDL-FORGE root directory

======================================================================
Step 1/6: Checking GHDL Installation
======================================================================

✅ GHDL found: GHDL 4.0.0 (Ubuntu 22.04)
✅ GHDL version is sufficient (>= 4.0)

======================================================================
Step 2/6: Checking Python
======================================================================

✅ Python found: 3.11.14
✅ Python version is sufficient (>= 3.10)

======================================================================
Step 3/6: Checking UV Package Manager
======================================================================

✅ UV found: uv 0.8.17

======================================================================
Step 4/6: Setting Up Python Packages
======================================================================

ℹ️  Running: uv sync
[package installation output]
✅ Base dependencies installed

ℹ️  Installing workspace packages in editable mode...
[editable install output]
✅ Workspace packages installed

======================================================================
Step 5/6: Verifying Package Imports
======================================================================

✅ forge_cocotb imports successfully
✅ forge_platform imports successfully
✅ forge_tools imports successfully

======================================================================
Step 6/6: Verifying Test Infrastructure
======================================================================

ℹ️  Testing test discovery...
✅ Test runner working
ℹ️  Found 10 available tests

======================================================================
Running Sample Test (GHDL Validation)
======================================================================

ℹ️  Running test: forge_lut_pkg
ℹ️  This will verify GHDL can simulate VHDL code

✅ Test forge_lut_pkg PASSED

======================================================================
Setup Complete!
======================================================================

✅ VHDL-FORGE cloud environment is ready!

Next steps:
  1. Verify setup: ./scripts/validate_setup.sh
  2. List tests: uv run python cocotb_tests/run.py --list
  3. Run a test: uv run python cocotb_tests/run.py forge_util_clk_divider
  4. Start development: /gather-requirements (in Claude Code)
```

---

## When GHDL Installation Fails

If running in an environment **without sudo/root access**:

```
❌ GHDL installation failed - this is BLOCKING

Manual installation:
  Container: Use ghdl/ghdl:ubuntu22-llvm-5.0 image
  Ubuntu:    sudo apt-get install ghdl ghdl-llvm
  macOS:     brew install ghdl
```

**Solution:** Ensure your container uses a GHDL-enabled base image:
- **Recommended:** `ghdl/ghdl:ubuntu22-llvm-5.0`
- **Alternative:** Any Debian/Ubuntu image where you can `apt-get install ghdl`

---

## Container Configuration

### Option 1: Use Provided Devcontainer (Recommended)

The repository includes `.devcontainer/devcontainer.json` with GHDL pre-configured:

```json
{
  "name": "VHDL-FORGE 3.0",
  "image": "ghdl/ghdl:ubuntu22-llvm-5.0",
  "features": {
    "ghcr.io/devcontainers/features/python:1": {
      "version": "3.11"
    }
  },
  "postCreateCommand": "uv run python scripts/cloud_setup_with_ghdl.py"
}
```

**In GitHub Codespaces or VS Code:**
1. Open repository
2. Click "Reopen in Container"
3. Setup runs automatically via `postCreateCommand`

### Option 2: GitHub Actions Workflow

For CI/CD testing:

```yaml
name: VHDL Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    container:
      image: ghdl/ghdl:ubuntu22-llvm-5.0

    steps:
      - uses: actions/checkout@v3

      - name: Setup VHDL-FORGE
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          export PATH="$HOME/.cargo/bin:$PATH"
          uv run python scripts/cloud_setup_with_ghdl.py

      - name: Run Tests
        run: uv run python cocotb_tests/run.py --all
```

### Option 3: Docker Compose

```yaml
version: '3.8'
services:
  vhdl-forge:
    image: ghdl/ghdl:ubuntu22-llvm-5.0
    volumes:
      - .:/workspace
    working_dir: /workspace
    command: |
      bash -c "
        curl -LsSf https://astral.sh/uv/install.sh | sh &&
        export PATH=\"\$HOME/.cargo/bin:\$PATH\" &&
        uv run python scripts/cloud_setup_with_ghdl.py
      "
```

---

## Troubleshooting

### Issue: "uv: command not found"

**Solution:** Install UV first:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"
uv run python scripts/cloud_setup_with_ghdl.py
```

### Issue: "Package imports fail"

**Check package structure:**
```bash
ls python/forge_cocotb/forge_cocotb/__init__.py  # Should exist
```

**If missing:** Repository is outdated, check git history for commit `6069c49`

### Issue: "Test runner fails"

**Run validation script:**
```bash
./scripts/validate_setup.sh
```

This will show which specific checks are failing.

### Issue: "GHDL simulations fail"

**Verify GHDL works:**
```bash
ghdl --version
ghdl --help
```

**Test simple VHDL:**
```bash
echo 'entity test is end entity;' > test.vhd
ghdl -a test.vhd
rm test.vhd
```

If GHDL doesn't work, you're not in a GHDL-enabled container.

---

## Success Criteria

After running the setup script, you should be able to:

✅ **List all tests:**
```bash
uv run python cocotb_tests/run.py --list
# Shows 10 tests across 4 categories
```

✅ **Run a VHDL simulation:**
```bash
uv run python cocotb_tests/run.py forge_util_clk_divider
# Test passes with GHDL output
```

✅ **Import all packages:**
```bash
uv run python -c "import forge_cocotb, forge_platform, forge_tools; print('OK')"
# Prints: OK
```

✅ **Check GHDL:**
```bash
ghdl --version
# Shows: GHDL 4.x or 5.x
```

---

## Comparison with Previous Diagnostics

### CLOUD_DEPLOYMENT_DIAGNOSTIC.md (Removed)
- ❌ Assumed no GHDL available
- ❌ Only validated Python infrastructure
- ❌ Could not run actual VHDL tests
- ✅ Auto-repaired Python issues

### CLOUD_SETUP_PROMPT.md (This File)
- ✅ Installs GHDL automatically
- ✅ Validates complete VHDL + Python stack
- ✅ Runs actual VHDL simulations
- ✅ Auto-repairs everything
- ✅ Single command execution

**Key Difference:** This setup enables **full VHDL development and testing in the cloud**, not just Python validation.

---

## Next Steps After Setup

Once setup completes successfully:

1. **Explore available tests:**
   ```bash
   uv run python cocotb_tests/run.py --list
   ```

2. **Run all tests:**
   ```bash
   uv run python cocotb_tests/run.py --all
   ```

3. **Start new component development:**
   - Type `/gather-requirements` in Claude Code
   - Follow 7-phase requirements gathering
   - Use 4-agent workflow for implementation

4. **Edit existing VHDL:**
   - Files in `vhdl/components/`
   - Run tests after changes
   - Commit with test results

---

## Architecture

```
Cloud Container (ghdl/ghdl:ubuntu22-llvm-5.0)
├── GHDL 4.0+ (pre-installed in image)
├── Python 3.11+ (DevContainer feature)
├── UV package manager (installed by setup script)
├── Virtual environment (.venv)
│   ├── cocotb 2.0.0
│   ├── pytest 9.0.0
│   └── workspace packages (editable)
└── VHDL-FORGE repository
    ├── vhdl/components/ (VHDL source)
    ├── cocotb_tests/ (test suite)
    └── python/ (forge_cocotb, forge_platform, forge_tools)
```

---

**Created:** 2025-11-09
**Version:** 1.0
**Maintainer:** VHDL-FORGE Team
**Purpose:** One-command cloud setup with full GHDL support
**Prerequisites:** Container with GHDL or sudo access to install it
**Related Files:**
- `scripts/cloud_setup_with_ghdl.py` (setup automation)
- `.devcontainer/devcontainer.json` (container configuration)
- `scripts/validate_setup.sh` (post-setup validation)
