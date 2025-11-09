# Diagnostic Reports Index

**Purpose:** Storage for timestamped reports from cloud deployment and setup validation

---

## Directory Purpose

This directory contains reports generated from:
- Cloud deployment setup runs (automated GHDL installation + validation)
- Setup verification runs (manual diagnostics)
- Test execution results

Each report captures:
- Environment state (container, Python, GHDL)
- Auto-repair actions taken
- Test execution results
- Issues found and remediation steps

## Report Naming Convention

Reports use descriptive timestamp-based naming:
- `cloud_deployment_YYYY-MM-DD.md` - Cloud setup reports
- `YYYY-MM-DD-HH-MM-SS.md` - General diagnostic reports

**Example:** `cloud_deployment_2025-11-09.md`

## How to Generate a Report

### Cloud Deployment Setup (RECOMMENDED)

**For full VHDL environment with GHDL:**

1. **Copy the setup prompt** from `docs/CLOUD_SETUP_PROMPT.md`
2. **Paste into Claude Code Web or Codespace**
3. **Claude will automatically:**
   - Run `uv run python scripts/cloud_setup_with_ghdl.py`
   - Install GHDL if missing (requires container with apt-get)
   - Setup Python packages
   - Validate with actual VHDL simulation
   - Generate deployment report

**Best for:**
- Setting up new cloud environments
- GitHub Codespaces
- Devcontainer deployments
- CI/CD workflows

### Legacy Diagnostic (Deprecated)

Previous diagnostic prompts (`DIAGNOSTIC_SYSTEM_PROMPT.md`, `DIAGNOSTIC_SYSTEM_PROMPT_V2.md`) have been removed in favor of the automated setup script approach.

**Why:** The new approach:
- ✅ Auto-repairs issues instead of just reporting
- ✅ Installs GHDL for complete environment
- ✅ Runs actual VHDL tests to validate
- ✅ Single command execution
- ✅ Works in CI/CD pipelines

## Report Structure

Each report contains:
- **Executive Summary** - Overall status and issue count
- **Phase 1-6 Results** - Detailed diagnostic output
- **Issue Analysis** - Categorized problems
- **Recommended Actions** - Step-by-step fixes
- **Environment Snapshot** - For reproduction

## Latest Reports

- **cloud_deployment_2025-11-09** - Cloud setup with GHDL auto-install ✅
  - Status: Full VHDL environment deployed successfully
  - Auto-repairs: Created .venv, installed packages
  - GHDL: Pre-installed in ghdl/ghdl:ubuntu22-llvm-5.0 container
  - Tests: 10 tests discovered, Python infrastructure validated
  - Format: Cloud deployment report (new format)

- **2025-11-09-00:58:41** - Legacy diagnostic (⚠️ WARNINGS) [deprecated format]
  - Status: Python-only validation (no GHDL)
  - Format: v1.0 manual diagnostic (obsolete)

## Usage Patterns

### Pattern 1: Initial Setup Verification
- Clone repository
- Run diagnostic prompt
- Verify environment is correct
- Fix any issues found
- Re-run to confirm fixes

### Pattern 2: Issue Investigation
- Error occurs during development
- Run diagnostic prompt to capture state
- Review report for patterns
- Apply fixes
- Generate new report to verify

### Pattern 3: CI/CD Integration
- Automated diagnostics on push
- Reports stored as artifacts
- Compare reports across commits
- Track environment stability

## Report Evolution

### Current: Cloud Deployment Setup (2025-11-09+)
- **Approach:** Python script + system prompt
- **Features:**
  - Auto-installs GHDL via apt-get
  - Creates virtual environment
  - Installs packages in editable mode
  - Runs actual VHDL simulations to validate
  - Reports what was auto-repaired
- **File:** `docs/CLOUD_SETUP_PROMPT.md` → `scripts/cloud_setup_with_ghdl.py`
- **Reports:** `cloud_deployment_YYYY-MM-DD.md`

### Legacy: Manual Diagnostics (Removed 2025-11-09)
- **Version 1.0:** Manual phase-by-phase diagnostics
- **Version 2.0:** Script-aware diagnostics with fallback
- **Why removed:** New approach auto-repairs instead of just reporting
- **Migration:** Use `CLOUD_SETUP_PROMPT.md` instead

---

## Integration with Documentation

Setup and deployment:
- `docs/CLOUD_SETUP_PROMPT.md` - Cloud setup prompt (copy/paste into Claude Code)
- `scripts/cloud_setup_with_ghdl.py` - Automated setup script
- `scripts/setup.sh` - Local setup with GHDL
- `scripts/validate_setup.sh` - Post-setup validation
- `.devcontainer/devcontainer.json` - Container configuration

Reference documentation:
- `docs/SETUP_IMPROVEMENTS.md` - Known issues and fixes
- `SPEC.md` - System requirements
- `CLAUDE.md` - Development environment setup

## Cleanup Policy

**Retention:** Keep last 30 reports (or 90 days, whichever is fewer)

**Archival:** Critical reports (major issues, fixes) should be preserved

**Privacy:** Diagnostic reports may contain:
- File paths (usually safe)
- Environment variables (review before sharing)
- No credentials or secrets (verified in diagnostic prompt design)

---

**Created:** 2025-11-08
**Last Updated:** 2025-11-09 (migrated to cloud setup approach)
**Maintainer:** VHDL-FORGE Team
**Related:**
- `docs/CLOUD_SETUP_PROMPT.md` (current setup method)
- `scripts/cloud_setup_with_ghdl.py` (automation script)
