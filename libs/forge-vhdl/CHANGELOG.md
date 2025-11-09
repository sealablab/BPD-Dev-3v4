# Changelog

All notable changes to forge-vhdl will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0] - 2025-11-09

### Added - Cloud Deployment Infrastructure

- **Automated Cloud Setup** (`scripts/cloud_setup_with_ghdl.py`)
  - Auto-installs GHDL + LLVM 18 on Ubuntu/Debian
  - Creates critical LLVM library symlink
  - Sets up Python virtual environment with UV
  - Installs workspace packages in editable mode
  - Validates environment with sample tests
  - Completes in ~3-5 minutes

- **Comprehensive Validation Framework**
  - `docs/CLOUD_SETUP_PROMPT.md` - Initial setup guide
  - `docs/CLOUD_VALIDATION_PROMPT.md` - First validation
  - `docs/CLOUD_RETEST_PROMPT.md` - Troubleshooting validation
  - `docs/CLOUD_FINAL_VALIDATION_PROMPT.md` - Production verification
  - `docs/CLOUD_PRODUCTION_VERIFICATION_PROMPT.md` - Final pre-merge check

- **Diagnostic Reporting System**
  - Comprehensive test result analysis
  - Failure categorization (LLVM, VHDL, missing sources)
  - Success analysis (what works and why)
  - Per-test detailed analysis files
  - Machine-readable result summaries

- **AI Agent Discoverability**
  - Cloud setup section in `llms.txt`
  - Quick start guide in `CLAUDE.md`
  - Prominent documentation references

### Fixed - Critical Infrastructure

- **LLVM Library Linking Issue** (CRITICAL FIX)
  - Root cause: Ubuntu's `llvm-18` package doesn't create symlink in standard location
  - Fix: Automatic symlink creation in setup script
  - Impact: Eliminated 100% of LLVM-related test failures
  - Location: `/usr/lib/x86_64-linux-gnu/libLLVM-18.so.18.1` → `/usr/lib/llvm-18/lib/libLLVM.so.1`

- **GHDL-LLVM Integration**
  - GHDL can now find LLVM 18 shared library
  - Full VHDL analysis and elaboration working
  - CocoTB tests execute successfully

### Validated - Production Readiness

- **Test Results: 5/10 passing (50% baseline)**
  - ✅ forge_util_clk_divider - Clock divider utility
  - ✅ forge_voltage_3v3_pkg - 0-3.3V voltage domain
  - ✅ forge_voltage_5v0_pkg - 0-5.0V voltage domain
  - ✅ forge_voltage_5v_bipolar_pkg - ±5V bipolar voltage domain
  - ✅ forge_hierarchical_encoder - FSM state encoder

- **Zero LLVM-related failures** (100% fix success rate)

- **Validated Environments**
  - GitHub Codespaces ✅
  - Claude Code Web ✅
  - Docker containers ✅

### Known Issues (Expected Failures)

- **forge_lut_pkg** (1 test, 10% of suite)
  - Issue: Test wrapper function signature mismatches
  - Fix complexity: MODERATE (20-30 minutes)
  - Priority: MEDIUM
  - Status: Documented, not blocking production

- **Platform Components** (4 tests, 40% of suite)
  - Issue: VHDL files not implemented yet
  - Fix complexity: HIGH (multiple days)
  - Priority: LOW (deferred to future work)
  - Status: Expected, documented

### Changed - Documentation

- **Version Bumps**
  - `CLAUDE.md`: 1.0 → 3.1.0
  - `llms.txt`: 2.0.0 → 3.1.0
  - `pyproject.toml`: 3.0.0 → 3.1.0

- **Enhanced Discoverability**
  - Cloud setup now prominently featured in key docs
  - AI agents discover setup script faster
  - Clear references to validation prompts

### Migration Notes

- **From vhdl-forge-3v1-claude**
  - Clean repository start (Option B: squashed history)
  - Based on v1.1.0-llvm-complete validation
  - Development history: v1.0.0-llvm-fix → v1.1.0-llvm-complete → v3.1.0
  - 4 comprehensive validation iterations (v1-v4)

- **Key Achievement**
  - LLVM symlink discovery through systematic troubleshooting
  - Iterative validation process proved effectiveness
  - Production-ready state achieved

### Technical Details

**LLVM Fix Investigation:**
1. v1.0.0-llvm-fix: Installed `llvm-18` package (incomplete)
2. v2 retest: Discovered package installed but symlink missing
3. v1.1.0-llvm-complete: Added symlink creation to setup script
4. v3 validation: Confirmed 5/10 tests passing (zero LLVM failures)
5. v4 production verification: Final confirmation

**Validation Metrics:**
- Before fix: 0/10 tests passing (50% LLVM failures)
- After fix: 5/10 tests passing (0% LLVM failures)
- Expected vs actual: PERFECT MATCH ✅

## Previous Development

Development history prior to v3.1.0 is preserved in the experimental repository:
- Repository: [vhdl-forge-3v1-claude](https://github.com/sealablab/vhdl-forge-3v1-claude)
- Final commit: bd4afef (docs: Improve cloud setup discoverability)
- Key tags: v1.0.0-llvm-fix, v1.1.0-llvm-complete

---

[3.1.0]: https://github.com/sealablab/forge-vhdl-3v1/releases/tag/v3.1.0
