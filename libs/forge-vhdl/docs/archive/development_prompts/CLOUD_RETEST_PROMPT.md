# VHDL-FORGE Cloud Retest with LLVM Fix

**Version:** 2.0
**Purpose:** Validate LLVM fix and provide detailed troubleshooting for remaining issues
**Environment:** Claude Code Web with LLVM 18 support
**Target:** Identify remaining blockers and document solutions

---

## Quick Start

**Copy this entire prompt and paste into Claude Code Web:**

---

```markdown
You are retesting the VHDL-FORGE cloud deployment after the LLVM 18 fix.

## Mission

Execute a comprehensive 4-phase workflow with detailed troubleshooting:
1. **Pre-flight Check** - Verify LLVM 18 is installed
2. **Test Execution** - Run all tests, continue on failures to gather maximum data
3. **Issue Analysis** - Deep-dive on each failure type, suggest fixes
4. **Commit Results** - Two separate commits (analysis + attempted fixes)

---

## Phase 1: Pre-flight Check & Environment Validation

### Step 1.1: Verify LLVM 18 Installation

```bash
echo "=== LLVM 18 VERIFICATION ==="
echo ""

# Check if LLVM 18 is installed
if dpkg -l | grep -q llvm-18; then
    echo "✅ LLVM 18 package installed"
    dpkg -l | grep llvm-18
else
    echo "❌ LLVM 18 package NOT installed"
    echo "   This is the critical fix from v1.0.0-llvm-fix"
    echo ""
    echo "Installing now..."
    apt-get update -qq
    apt-get install -y llvm-18
fi

echo ""

# Check for the specific library that was missing
echo "Checking for libLLVM-18.so.18.1..."
if ldconfig -p | grep -q libLLVM-18.so; then
    echo "✅ LLVM 18 shared library found"
    ldconfig -p | grep libLLVM-18
else
    echo "❌ LLVM 18 shared library NOT found"
    echo "   GHDL will fail with same error as before"
fi

echo ""
```

### Step 1.2: Verify GHDL Functionality

```bash
echo "=== GHDL FUNCTIONALITY TEST ==="
echo ""

# Test GHDL can analyze a simple VHDL file
cat > /tmp/test_entity.vhd << 'EOF'
entity test is
end entity;

architecture rtl of test is
begin
end architecture;
EOF

echo "Testing GHDL analysis..."
if ghdl -a --std=08 /tmp/test_entity.vhd 2>&1; then
    echo "✅ GHDL can analyze VHDL files"
else
    echo "❌ GHDL analysis failed"
    echo "   LLVM library issue likely persists"
fi

rm -f /tmp/test_entity.vhd work-obj08.cf

echo ""
```

### Step 1.3: Quick Setup Validation

```bash
echo "=== SETUP VALIDATION ==="
echo ""

# Run setup script (should be fast if already configured)
uv run python scripts/cloud_setup_with_ghdl.py

echo ""
echo "=== PRE-FLIGHT CHECK COMPLETE ==="
echo ""
```

**Decision Point:**
- If LLVM check fails → Document why, but continue testing to gather data
- If GHDL test fails → Note it, continue anyway (might be different in real tests)
- If setup fails → Stop and report

---

## Phase 2: Comprehensive Test Execution with Detailed Logging

Run all tests, capturing detailed output for each failure type.

### Step 2.1: Create Organized Test Log Structure

```bash
mkdir -p test_logs_v2/{passed,failed,error}
echo "Test run started: $(date -u)" > test_logs_v2/run_summary.txt
```

### Step 2.2: Run Tests with Enhanced Logging

**For each test, capture:**
- Full stdout/stderr
- Exit code
- Execution time
- Specific error messages
- File paths mentioned in errors

```bash
# Function to run a test with detailed logging
run_test_detailed() {
    local test_name=$1
    local category=$2

    echo ""
    echo "========================================================================"
    echo "Testing: $test_name"
    echo "========================================================================"

    start_time=$(date +%s)

    # Run test and capture everything
    if uv run python cocotb_tests/run.py "$test_name" > "test_logs_v2/raw_${test_name}.log" 2>&1; then
        status="PASS"
        mv "test_logs_v2/raw_${test_name}.log" "test_logs_v2/passed/${test_name}.log"
    else
        exit_code=$?
        status="FAIL"
        mv "test_logs_v2/raw_${test_name}.log" "test_logs_v2/failed/${test_name}.log"

        # Analyze failure type
        if grep -q "libLLVM" "test_logs_v2/failed/${test_name}.log"; then
            echo "  Failure type: LLVM library missing" | tee -a test_logs_v2/run_summary.txt
        elif grep -q "error while loading shared libraries" "test_logs_v2/failed/${test_name}.log"; then
            echo "  Failure type: Missing shared library" | tee -a test_logs_v2/run_summary.txt
        elif grep -q "error:" "test_logs_v2/failed/${test_name}.log"; then
            echo "  Failure type: VHDL compilation error" | tee -a test_logs_v2/run_summary.txt
        elif grep -q "Missing source files" "test_logs_v2/failed/${test_name}.log"; then
            echo "  Failure type: Missing source files" | tee -a test_logs_v2/run_summary.txt
        elif grep -q "FileNotFoundError" "test_logs_v2/failed/${test_name}.log"; then
            echo "  Failure type: File not found" | tee -a test_logs_v2/run_summary.txt
        else
            echo "  Failure type: Unknown" | tee -a test_logs_v2/run_summary.txt
        fi
    fi

    end_time=$(date +%s)
    duration=$((end_time - start_time))

    echo "$test_name|$category|$status|${duration}s|$exit_code" >> test_logs_v2/run_summary.txt
    echo "  Status: $status (${duration}s)"
}

# Run all tests
echo "Starting comprehensive test suite..."
echo ""

run_test_detailed "forge_util_clk_divider" "utilities"
run_test_detailed "forge_lut_pkg" "packages"
run_test_detailed "forge_voltage_3v3_pkg" "packages"
run_test_detailed "forge_voltage_5v0_pkg" "packages"
run_test_detailed "forge_voltage_5v_bipolar_pkg" "packages"
run_test_detailed "forge_hierarchical_encoder" "debugging"
run_test_detailed "platform_bpd_deployment" "platform"
run_test_detailed "platform_counter_poc" "platform"
run_test_detailed "platform_oscilloscope_capture" "platform"
run_test_detailed "platform_routing_integration" "platform"

echo ""
echo "========================================================================"
echo "TEST EXECUTION COMPLETE"
echo "========================================================================"
```

### Step 2.3: Generate Quick Summary

```bash
echo ""
echo "=== QUICK RESULTS SUMMARY ==="
echo ""

passed_count=$(ls test_logs_v2/passed/*.log 2>/dev/null | wc -l)
failed_count=$(ls test_logs_v2/failed/*.log 2>/dev/null | wc -l)
total_count=$((passed_count + failed_count))

echo "Total tests: $total_count"
echo "Passed: $passed_count"
echo "Failed: $failed_count"
echo ""

if [ $passed_count -gt 0 ]; then
    echo "✅ PASSED TESTS:"
    ls test_logs_v2/passed/*.log 2>/dev/null | xargs -n1 basename | sed 's/.log$//' | sed 's/^/  - /'
    echo ""
fi

if [ $failed_count -gt 0 ]; then
    echo "❌ FAILED TESTS:"
    ls test_logs_v2/failed/*.log 2>/dev/null | xargs -n1 basename | sed 's/.log$//' | sed 's/^/  - /'
fi

echo ""
```

---

## Phase 3: Deep Issue Analysis & Troubleshooting

For each failure, perform forensic analysis and suggest fixes.

### Step 3.1: Analyze Each Failed Test

```bash
echo "=== DETAILED FAILURE ANALYSIS ==="
echo ""

for log_file in test_logs_v2/failed/*.log; do
    if [ -f "$log_file" ]; then
        test_name=$(basename "$log_file" .log)
        echo "========================================================================"
        echo "Analysis: $test_name"
        echo "========================================================================"
        echo ""

        # Extract key error lines
        echo "Key errors:"
        grep -E "error:|Error:|ERROR:|cannot|missing|not found|No such file" "$log_file" | head -20
        echo ""

        # Check for specific issues
        if grep -q "libLLVM-18" "$log_file"; then
            echo "🔍 DIAGNOSIS: LLVM 18 library not found"
            echo "   Expected fix: Install llvm-18 package"
            echo "   Status: Should have been fixed by v1.0.0-llvm-fix"
            echo "   ACTION NEEDED: Verify LLVM installation above"

        elif grep -q "digital_to_voltage\|voltage_to_pct_index" "$log_file"; then
            echo "🔍 DIAGNOSIS: Missing or incorrect VHDL functions"
            echo "   Problem file: cocotb_tests/cocotb_test_wrappers/forge_lut_pkg_tb_wrapper.vhd"
            echo "   Missing functions:"
            grep "no declaration for\|cannot match function" "$log_file" | sed 's/^/     /'
            echo ""
            echo "   SUGGESTED FIX:"
            echo "   1. Check forge_lut_pkg.vhd for correct function signatures"
            echo "   2. Update wrapper to use correct function names"
            echo "   3. Add missing 'use ieee.numeric_std.all' if needed"

        elif grep -q "Missing source files" "$log_file"; then
            echo "🔍 DIAGNOSIS: VHDL source files not found"
            echo "   Expected paths:"
            grep "Expected:" "$log_file" | sed 's/^/     /'
            echo ""
            echo "   SUGGESTED FIX:"
            echo "   1. Check if VHDL files exist in vhdl/ directory"
            echo "   2. Verify test_configs.py has correct paths"
            echo "   3. Files may need to be implemented"

        elif grep -q "FileNotFoundError" "$log_file"; then
            echo "🔍 DIAGNOSIS: Python file not found"
            grep "FileNotFoundError" "$log_file" | sed 's/^/     /'
            echo ""
            echo "   SUGGESTED FIX:"
            echo "   1. Check test_configs.py for correct test module paths"
            echo "   2. Verify test files exist in cocotb_tests/"

        else
            echo "🔍 DIAGNOSIS: Unknown failure type"
            echo "   First 10 lines of output:"
            head -10 "$log_file" | sed 's/^/     /'
        fi

        echo ""
    fi
done
```

### Step 3.2: Check for Fixable Issues

```bash
echo "=== FIXABLE ISSUES CHECK ==="
echo ""

# Check if platform test VHDL files exist
echo "Checking platform VHDL sources..."
for test in platform_bpd_deployment platform_counter_poc platform_oscilloscope_capture platform_routing_integration; do
    # Try to find the VHDL file
    if find vhdl/ -name "*${test#platform_}*.vhd" 2>/dev/null | grep -q .; then
        echo "  ✅ $test: VHDL file exists"
    else
        echo "  ❌ $test: VHDL file NOT FOUND (needs implementation)"
    fi
done

echo ""

# Check if wrapper files exist
echo "Checking test wrapper files..."
if [ -f "cocotb_tests/cocotb_test_wrappers/forge_lut_pkg_tb_wrapper.vhd" ]; then
    echo "✅ forge_lut_pkg wrapper exists"

    # Check for missing functions
    echo "   Checking for problematic function calls..."
    if grep -q "digital_to_voltage" cocotb_tests/cocotb_test_wrappers/forge_lut_pkg_tb_wrapper.vhd; then
        echo "   ⚠️  Uses 'digital_to_voltage' (may not exist in package)"
    fi
    if grep -q "voltage_to_pct_index" cocotb_tests/cocotb_test_wrappers/forge_lut_pkg_tb_wrapper.vhd; then
        echo "   ⚠️  Uses 'voltage_to_pct_index' (check signature)"
    fi
else
    echo "❌ forge_lut_pkg wrapper NOT FOUND"
fi

echo ""
```

### Step 3.3: Categorize All Failures

```bash
echo "=== FAILURE CATEGORIZATION ==="
echo ""

llvm_failures=0
vhdl_errors=0
missing_sources=0
other_failures=0

for log_file in test_logs_v2/failed/*.log; do
    if [ -f "$log_file" ]; then
        if grep -q "libLLVM" "$log_file"; then
            llvm_failures=$((llvm_failures + 1))
        elif grep -q "error:" "$log_file"; then
            vhdl_errors=$((vhdl_errors + 1))
        elif grep -q "Missing source files" "$log_file"; then
            missing_sources=$((missing_sources + 1))
        else
            other_failures=$((other_failures + 1))
        fi
    fi
done

echo "Failure breakdown:"
echo "  LLVM library issues: $llvm_failures tests"
echo "  VHDL compilation errors: $vhdl_errors tests"
echo "  Missing source files: $missing_sources tests"
echo "  Other issues: $other_failures tests"
echo ""

# Calculate improvement from previous run
echo "Comparison to previous run:"
echo "  Previous LLVM failures: 6 tests (60%)"
echo "  Current LLVM failures: $llvm_failures tests"
if [ $llvm_failures -lt 6 ]; then
    improvement=$((6 - llvm_failures))
    echo "  ✅ IMPROVEMENT: Fixed $improvement LLVM-related tests!"
else
    echo "  ❌ NO IMPROVEMENT: LLVM fix did not work"
fi

echo ""
```

---

## Phase 4: Commit Results (Two Separate Commits)

### Commit 1: Test Results & Analysis

Create comprehensive report and commit:

**Report filename:** `docs/diagnostic_reports/retest_results_v2_YYYY-MM-DD-HH-MM.md`

```markdown
# VHDL-FORGE Retest Results (v2 - Post LLVM Fix)

**Date:** YYYY-MM-DD HH:MM:SS UTC
**Environment:** Claude Code Web
**Previous Commit:** bd91d62 (LLVM 18 fix)
**Test Run:** 2nd validation after v1.0.0-llvm-fix

---

## Executive Summary

**Previous Results:** 0/10 passed (100% LLVM failures)
**Current Results:** X/10 passed (Y% success rate)
**Improvement:** [+X tests, +Y% success rate]

---

## Pre-flight Check Results

### LLVM 18 Verification
[Paste LLVM verification output]

### GHDL Functionality Test
[Paste GHDL test output]

**Verdict:** [✅ LLVM fix successful / ❌ LLVM still broken]

---

## Test Results Summary

| Test Name | Status | Duration | Failure Type |
|-----------|--------|----------|--------------|
[Fill in from run_summary.txt]

**Category Breakdown:**
- UTILITIES: X/1 passed
- PACKAGES: X/4 passed
- DEBUGGING: X/1 passed
- PLATFORM: X/4 passed

---

## Failure Analysis

### By Category

**LLVM Library Issues:** X tests (Y%)
[List tests]
**Analysis:** [If X > 0: LLVM fix incomplete / If X = 0: LLVM fix successful]

**VHDL Compilation Errors:** X tests (Y%)
[List tests with specific errors]
**Root Cause:** [Detail the VHDL issues found]

**Missing Source Files:** X tests (Y%)
[List tests]
**Root Cause:** [Platform VHDL files not implemented yet]

**Other Issues:** X tests (Y%)
[List with details]

---

## Detailed Failure Diagnostics

[For each failed test, paste analysis from Phase 3]

### Test: [name]
**Failure Type:** [type]
**Key Errors:**
```
[Paste error lines]
```

**Diagnosis:**
[Paste diagnosis from Phase 3.1]

**Suggested Fix:**
[Paste suggested fix]

---

## Fixable Issues Identified

### Immediate Fixes (Can Apply Now)

1. **[Issue description]**
   - Affected tests: [list]
   - Fix: [specific action]
   - Complexity: [simple/moderate/complex]

### Requires Implementation

1. **[Issue description]**
   - Affected tests: [list]
   - Requires: [new VHDL code/test updates/config changes]

---

## Comparison to Previous Run

**Previous (v1):**
- LLVM failures: 6/10 (60%)
- VHDL errors: 1/10 (10%)
- Missing sources: 3/10 (30%)

**Current (v2):**
- LLVM failures: X/10 (Y%)
- VHDL errors: X/10 (Y%)
- Missing sources: X/10 (Y%)

**Progress:**
[Narrative on improvement or lack thereof]

---

## Recommendations

### If LLVM Fix Worked (0 LLVM failures):
1. ✅ Mark v1.0.0-llvm-fix as stable
2. Focus on VHDL code errors next
3. Implement missing platform sources
4. Expected: 7-8/10 pass rate after VHDL fixes

### If LLVM Fix Partial (1-3 LLVM failures):
1. ⚠️ LLVM partially working
2. Investigate remaining LLVM failures
3. May need additional library packages
4. Check ldconfig cache

### If LLVM Fix Failed (6+ LLVM failures):
1. ❌ LLVM fix ineffective
2. Verify llvm-18 package actually installed
3. May need different GHDL image
4. Consider ghdl/ghdl:ubuntu24-llvm-14

---

## Next Steps

[Based on results, provide specific ordered actions]

---

## Attached Logs

See `test_logs_v2/` directory for:
- `passed/*.log` - Successful test outputs
- `failed/*.log` - Failed test outputs with full errors
- `run_summary.txt` - Machine-readable test results
```

**Commit the analysis:**

```bash
git add test_logs_v2/
git add docs/diagnostic_reports/retest_results_v2_*.md
git commit -m "test: Retest results after LLVM 18 fix (v2)

Results: X/10 passed (Y% success rate)
Previous: 0/10 passed (0% success rate)
Improvement: +X tests

Failure breakdown:
- LLVM issues: X tests (was 6)
- VHDL errors: X tests (was 1)
- Missing sources: X tests (was 3)

LLVM fix status: [SUCCESS/PARTIAL/FAILED]

Detailed analysis in:
- docs/diagnostic_reports/retest_results_v2_*.md
- test_logs_v2/ (organized by pass/fail)"

git push
```

---

### Commit 2: Attempted Fixes (If Any Issues Are Fixable)

After analysis, attempt to fix any simple issues found:

**Potential fixes to attempt:**

1. **If VHDL function signature issues found:**
```bash
# Examine the actual package to see what functions exist
cat vhdl/packages/forge_lut_pkg.vhd | grep "function\|procedure" > /tmp/available_functions.txt

# Compare with what wrapper is trying to use
grep "digital_to_voltage\|voltage_to_pct_index" cocotb_tests/cocotb_test_wrappers/forge_lut_pkg_tb_wrapper.vhd > /tmp/used_functions.txt

echo "=== FUNCTION MISMATCH ANALYSIS ==="
echo "Available in package:"
cat /tmp/available_functions.txt
echo ""
echo "Used in wrapper:"
cat /tmp/used_functions.txt
```

2. **If test config paths are wrong:**
```bash
# Check actual VHDL file locations
echo "=== ACTUAL VHDL FILES ==="
find vhdl/ -name "*.vhd" -type f | sort

echo ""
echo "=== CONFIGURED PATHS IN test_configs.py ==="
grep "HDL_SOURCES" cocotb_tests/test_configs.py | head -20
```

3. **If missing `use` clauses:**
```bash
# Check if wrapper has necessary library imports
echo "=== WRAPPER LIBRARY IMPORTS ==="
head -20 cocotb_tests/cocotb_test_wrappers/forge_lut_pkg_tb_wrapper.vhd | grep "use "
```

**If fixes identified and can be applied:**

```bash
# Apply fixes (examples - adapt based on actual issues found)

# Example: Add missing library import
if ! grep -q "use ieee.numeric_std.all" cocotb_tests/cocotb_test_wrappers/forge_lut_pkg_tb_wrapper.vhd; then
    echo "Adding missing numeric_std import..."
    # sed command to add it
fi

# Example: Fix function name
# sed -i 's/digital_to_voltage/correct_function_name/g' wrapper.vhd

# Document what was attempted
cat > docs/diagnostic_reports/fix_attempts_YYYY-MM-DD.md << 'EOF'
# Fix Attempts (Post-Retest v2)

## Fixes Applied

1. **[Fix description]**
   - File: [file]
   - Change: [what changed]
   - Expected impact: [which tests should now pass]

2. **[Next fix]**
   ...

## Fixes NOT Applied (Require Implementation)

1. **[Issue]**
   - Reason: [why not fixed]
   - Requires: [what's needed]

EOF

git add -A
git commit -m "fix: Apply fixes found in retest v2 analysis

Automated fixes based on diagnostics:
- [List what was fixed]

Expected improvement: X additional tests passing

Manual review needed for:
- [List issues that need human intervention]

Refs: docs/diagnostic_reports/retest_results_v2_*.md"

git push
```

**If no fixes can be applied automatically:**

```bash
# Just document what needs manual work
cat > docs/diagnostic_reports/fix_attempts_YYYY-MM-DD.md << 'EOF'
# Fix Attempts (Post-Retest v2)

## Automated Fixes

None - all issues require manual intervention.

## Issues Requiring Manual Work

[List from analysis with details]

EOF

git add docs/diagnostic_reports/fix_attempts_*.md
git commit -m "docs: Document issues requiring manual fixes

All remaining failures need human intervention:
- VHDL code errors: Need function implementation
- Missing sources: Need VHDL file creation
- [Other specific issues]

See: docs/diagnostic_reports/fix_attempts_*.md"

git push
```

---

## Final Summary to User

After both commits, provide comprehensive summary:

**1. Test Results:**
- Current: X/10 passed (Y% success rate)
- Previous: 0/10 passed (0% success rate)
- Improvement: +X tests (+Y%)

**2. LLVM Fix Assessment:**
- [✅ SUCCESS: All LLVM issues resolved / ⚠️ PARTIAL: Some LLVM issues remain / ❌ FAILED: LLVM fix did not work]

**3. Remaining Issues:**
- LLVM failures: X tests
- VHDL errors: X tests
- Missing sources: X tests
- Total blocking issues: X

**4. Commits Created:**
- Commit 1: Test results & deep analysis
- Commit 2: [Automated fixes applied / Documentation of manual work needed]

**5. Links:**
- Test results: `docs/diagnostic_reports/retest_results_v2_*.md`
- Test logs: `test_logs_v2/passed/` and `test_logs_v2/failed/`
- Fix attempts: `docs/diagnostic_reports/fix_attempts_*.md` (if created)

**6. Next Actions:**
[Specific, ordered list based on what was found]

**7. Notable Findings:**
[Anything interesting or unexpected discovered]

---

BEGIN EXECUTION NOW.
```

---

## What This Prompt Does

1. **Pre-flight checks** LLVM installation before running tests
2. **Runs all tests** with detailed logging (doesn't stop on failures)
3. **Deep analysis** of each failure with specific diagnosis and fix suggestions
4. **Categorizes** failures to track improvement from v1
5. **Attempts fixes** for any issues that can be auto-repaired
6. **Two commits:**
   - Commit 1: Comprehensive test results & analysis
   - Commit 2: Automated fixes OR documentation of manual work needed

## Expected Outcomes

### Best Case (LLVM Fix Worked)
- 6-7/10 tests pass
- LLVM failures reduced to 0
- Remaining: 1 VHDL error + 3 missing sources

### Partial Success
- 3-5/10 tests pass
- Some LLVM issues resolved
- Clear diagnosis of what's still broken

### No Improvement
- Still 0/10 passed
- Detailed analysis of why LLVM fix didn't work
- Alternative solutions proposed

## Key Features

- ✅ **Continue on failure** - Gathers maximum diagnostic data
- ✅ **Forensic analysis** - Deep-dive on each error type
- ✅ **Comparative metrics** - Shows improvement vs v1
- ✅ **Actionable fixes** - Specific commands to resolve issues
- ✅ **Organized logging** - passed/failed directories
- ✅ **Two-commit workflow** - Separates results from fixes

---

**Created:** 2025-11-09
**Version:** 2.0
**Purpose:** Comprehensive retest with troubleshooting after LLVM fix
**Previous:** v1.0.0-llvm-fix tag
**Expected Duration:** 10-15 minutes
