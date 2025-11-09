# VHDL-FORGE Cloud Validation & Test Execution Prompt

**Version:** 1.0
**Purpose:** Complete cloud environment validation with automated testing and result reporting
**Target:** Claude Code Web
**Duration:** 5-10 minutes (includes full test suite execution)

---

## Instructions

**Copy the entire prompt below and paste into Claude Code Web:**

---

```markdown
You are validating the VHDL-FORGE cloud deployment and running the complete test suite.

## Mission

Execute a 4-phase workflow:
1. **Setup & Validation** - Run automated environment setup
2. **Issue Reporting** - Commit and push any setup issues/fixes
3. **Test Execution** - Run complete VHDL test suite with GHDL
4. **Result Reporting** - Commit and push test results

---

## Phase 1: Environment Setup & Validation

Run the automated setup script:

```bash
uv run python scripts/cloud_setup_with_ghdl.py
```

**Analyze the output:**

- If setup completes successfully (exit code 0):
  - Note what was installed/configured
  - Proceed to Phase 2

- If setup fails (non-zero exit code):
  - Capture the full error output
  - Identify the failure point (GHDL, UV, packages, imports, tests)
  - Note what auto-repairs were attempted
  - Proceed to Phase 2 to report issues

**Expected output includes:**
- ✅ GHDL installation status
- ✅ Python package setup
- ✅ Import validation
- ✅ Test runner verification
- ✅ Sample VHDL simulation result

---

## Phase 2: Issue Reporting & Commit

Create a validation report and commit it:

**Report filename:** `docs/diagnostic_reports/cloud_validation_YYYY-MM-DD-HH-MM.md`

**Report template:**

```markdown
# Cloud Validation Report

**Date:** YYYY-MM-DD HH:MM:SS UTC
**Environment:** Claude Code Web
**Commit:** [git log -1 --oneline]
**Phase:** Setup & Validation

---

## Setup Results

[Paste full output from Phase 1]

---

## Summary

**Status:** [✅ SUCCESS / ❌ FAILED]

**GHDL:** [✅ Installed / ⚠️ Pre-installed / ❌ Failed]
**Python Packages:** [✅ Installed / ❌ Failed]
**Test Runner:** [✅ Working / ❌ Failed]
**Sample Test:** [✅ Passed / ❌ Failed]

**Issues Found:**
[List any issues, or "None"]

**Auto-Repairs Applied:**
[List what was auto-fixed, or "None"]

---

## Next Steps

[If successful: "Proceeding to Phase 3 - Test Execution"]
[If failed: "Setup failed at: [step]. Cannot proceed to testing."]
```

**Commit and push the report:**

```bash
git add docs/diagnostic_reports/cloud_validation_*.md
git commit -m "docs: Add cloud validation report (YYYY-MM-DD)

Setup status: [SUCCESS/FAILED]
Issues: [none/describe]
Auto-repairs: [list]"
git push
```

**Decision point:**
- If setup succeeded → Continue to Phase 3
- If setup failed → STOP and report to user what failed

---

## Phase 3: Test Execution (If Phase 1 Succeeded)

Run the complete test suite:

### 3.1: List All Available Tests

```bash
uv run python cocotb_tests/run.py --list
```

Capture the test count and categories.

### 3.2: Run All Tests Sequentially

**Note:** This will take several minutes. Each test runs VHDL simulation with GHDL.

```bash
# Create test results directory
mkdir -p test_results

# Run each test category and capture results
echo "Running UTILITIES tests..."
uv run python cocotb_tests/run.py forge_util_clk_divider 2>&1 | tee test_results/utilities.log

echo "Running PACKAGES tests..."
uv run python cocotb_tests/run.py forge_lut_pkg 2>&1 | tee test_results/packages_lut.log
uv run python cocotb_tests/run.py forge_voltage_3v3_pkg 2>&1 | tee test_results/packages_3v3.log
uv run python cocotb_tests/run.py forge_voltage_5v0_pkg 2>&1 | tee test_results/packages_5v0.log
uv run python cocotb_tests/run.py forge_voltage_5v_bipolar_pkg 2>&1 | tee test_results/packages_5v_bipolar.log

echo "Running DEBUGGING tests..."
uv run python cocotb_tests/run.py forge_hierarchical_encoder 2>&1 | tee test_results/debugging.log

echo "Running PLATFORM tests..."
uv run python cocotb_tests/run.py platform_bpd_deployment 2>&1 | tee test_results/platform_bpd.log
uv run python cocotb_tests/run.py platform_counter_poc 2>&1 | tee test_results/platform_counter.log
uv run python cocotb_tests/run.py platform_oscilloscope_capture 2>&1 | tee test_results/platform_osc.log
uv run python cocotb_tests/run.py platform_routing_integration 2>&1 | tee test_results/platform_routing.log
```

**Track results as tests run:**

For each test, note:
- Test name
- Status (PASS/FAIL/ERROR)
- Duration
- Any warnings or errors
- Key output lines (test assertions, GHDL output)

---

## Phase 4: Results Reporting & Commit

Create comprehensive test results report:

**Report filename:** `docs/diagnostic_reports/test_results_YYYY-MM-DD-HH-MM.md`

**Report template:**

```markdown
# VHDL-FORGE Test Results

**Date:** YYYY-MM-DD HH:MM:SS UTC
**Environment:** Claude Code Web (GHDL container)
**Commit:** [git log -1 --oneline]
**Total Tests:** 10

---

## Test Summary

| Category | Test Name | Status | Duration | Notes |
|----------|-----------|--------|----------|-------|
| UTILITIES | forge_util_clk_divider | [PASS/FAIL] | [time] | [notes] |
| PACKAGES | forge_lut_pkg | [PASS/FAIL] | [time] | [notes] |
| PACKAGES | forge_voltage_3v3_pkg | [PASS/FAIL] | [time] | [notes] |
| PACKAGES | forge_voltage_5v0_pkg | [PASS/FAIL] | [time] | [notes] |
| PACKAGES | forge_voltage_5v_bipolar_pkg | [PASS/FAIL] | [time] | [notes] |
| DEBUGGING | forge_hierarchical_encoder | [PASS/FAIL] | [time] | [notes] |
| PLATFORM | platform_bpd_deployment | [PASS/FAIL] | [time] | [notes] |
| PLATFORM | platform_counter_poc | [PASS/FAIL] | [time] | [notes] |
| PLATFORM | platform_oscilloscope_capture | [PASS/FAIL] | [time] | [notes] |
| PLATFORM | platform_routing_integration | [PASS/FAIL] | [time] | [notes] |

**Overall Status:** [X/10 PASSED, Y/10 FAILED]

---

## Detailed Results

### UTILITIES

#### forge_util_clk_divider
**Status:** [PASS/FAIL]
**Output:**
```
[Paste relevant output lines - test assertions, PASS/FAIL indicators]
```

### PACKAGES

#### forge_lut_pkg
**Status:** [PASS/FAIL]
**Output:**
```
[Paste relevant output]
```

[Continue for all tests...]

---

## Issues Found

[List any test failures, GHDL errors, or unexpected behavior]
[Or "None - all tests passed"]

---

## Environment Details

**GHDL Version:**
```
[ghdl --version output]
```

**Python Version:**
```
[python3 --version output]
```

**Installed Packages:**
```
[uv pip list | grep forge]
```

---

## Recommendations

[Based on test results, provide recommendations:]
- [If all passed: "All tests passing - environment is production-ready"]
- [If some failed: "Review failures above and check VHDL source files"]
- [If many failed: "Possible GHDL compatibility issue or missing dependencies"]
```

**Commit test logs and report:**

```bash
# Add all test results
git add test_results/
git add docs/diagnostic_reports/test_results_*.md

# Commit with summary
git commit -m "test: Add complete test suite results (YYYY-MM-DD)

Test summary: X/10 passed, Y/10 failed
Environment: Claude Code Web with GHDL
Duration: ~Z minutes

[If failures:]
Failed tests:
- test_name: reason

[If all passed:]
All tests passing in cloud environment"

# Push results
git push
```

---

## Final Summary to User

After completing all phases, provide the user with:

**1. Setup Summary:**
- Environment status (ready/failed)
- What was installed
- Any issues encountered

**2. Test Results:**
- Total tests run: 10
- Passed: X
- Failed: Y
- Duration: ~Z minutes

**3. Links to Reports:**
- Setup validation: `docs/diagnostic_reports/cloud_validation_*.md`
- Test results: `docs/diagnostic_reports/test_results_*.md`
- Test logs: `test_results/*.log`

**4. Next Steps:**
- If all passed: "Cloud environment is production-ready for VHDL development"
- If some failed: "Review failure reports and check specific test logs"
- If setup failed: "Fix setup issues before running tests"

**5. Notable Findings:**
- Any interesting test outputs
- GHDL warnings or performance notes
- Suggestions for improvements

---

## Error Handling

**If setup fails in Phase 1:**
- Still commit the validation report
- Do NOT proceed to Phase 3
- Report to user what failed and why

**If tests fail in Phase 3:**
- Continue running remaining tests (don't stop on first failure)
- Capture all output for debugging
- Note which specific assertions failed
- Commit all results even if some tests failed

**If git push fails:**
- Report the error
- Show git status
- Suggest manual push or check repository permissions

---

BEGIN EXECUTION NOW.
```

---

## What This Prompt Does

1. **Runs setup script** - Validates environment, installs GHDL if needed
2. **Creates validation report** - Documents setup results
3. **Commits setup report** - Pushes to main branch
4. **Runs all 10 tests** - Complete VHDL simulation suite with GHDL
5. **Captures all output** - Saves logs for each test
6. **Creates test report** - Comprehensive results with pass/fail
7. **Commits test results** - Pushes logs and report to main
8. **Summarizes for user** - Clear overview of what happened

## Expected Duration

- **Setup (Phase 1-2):** 1-2 minutes
- **Testing (Phase 3-4):** 5-10 minutes (GHDL simulations)
- **Total:** ~7-12 minutes

## Expected Commits

After execution, you'll see 2 new commits:

1. `docs: Add cloud validation report (YYYY-MM-DD)`
   - Setup results
   - Environment status

2. `test: Add complete test suite results (YYYY-MM-DD)`
   - 10 test results
   - Test logs in `test_results/`
   - Comprehensive report

## Success Criteria

✅ **Full Success:**
- Setup completes without errors
- 10/10 tests pass
- Both reports committed and pushed

⚠️ **Partial Success:**
- Setup succeeds
- Some tests pass, some fail
- All results documented and pushed

❌ **Setup Failure:**
- Setup script fails
- No tests run
- Validation report documents the issue

---

**Created:** 2025-11-09
**Version:** 1.0
**Purpose:** Complete cloud validation with automated testing
**Related:** `docs/CLOUD_SETUP_PROMPT.md`, `scripts/cloud_setup_with_ghdl.py`
