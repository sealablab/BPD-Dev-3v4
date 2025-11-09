# VHDL-FORGE Final Validation with Complete LLVM Fix

**Version:** 3.0
**Purpose:** Validate v1.1.0-llvm-complete with full symlink fix and comprehensive analysis
**Environment:** Claude Code Web with complete GHDL + LLVM 18 setup
**Expected:** 5/10 tests passing (50% success rate)

---

## Quick Start

**Copy this entire prompt and paste into Claude Code Web:**

---

```markdown
You are performing final validation of VHDL-FORGE after the complete LLVM fix (v1.1.0-llvm-complete).

## Mission

Execute comprehensive 5-phase validation with detailed troubleshooting:
1. **Pre-flight Verification** - Confirm LLVM symlink exists before testing
2. **Full Test Suite** - Run all tests, document every result in detail
3. **Success Analysis** - Deep-dive on passing tests (prove they work)
4. **Failure Analysis** - Forensic analysis of remaining failures
5. **Dual Commit** - Results report + actionable fixes/documentation

**Key Difference from v2:** Focus on proving what WORKS, not just diagnosing failures.

---

## Phase 1: Pre-flight Verification (Critical Infrastructure Check)

### Step 1.1: Verify Complete LLVM Setup

```bash
echo "=========================================================================="
echo "PRE-FLIGHT: LLVM 18 Complete Setup Verification"
echo "=========================================================================="
echo ""

# Check 1: LLVM 18 package installed
echo "Check 1: LLVM 18 package installation"
if dpkg -l | grep -q "ii  llvm-18 "; then
    echo "✅ LLVM 18 package installed"
    dpkg -l | grep llvm-18 | head -3
else
    echo "❌ LLVM 18 NOT installed - running setup..."
    apt-get update -qq
    apt-get install -y llvm-18
fi
echo ""

# Check 2: Critical symlink exists (the v1.1.0 fix)
echo "Check 2: LLVM library symlink (v1.1.0-llvm-complete fix)"
if [ -L "/usr/lib/x86_64-linux-gnu/libLLVM-18.so.18.1" ]; then
    echo "✅ Symlink exists"
    ls -lh /usr/lib/x86_64-linux-gnu/libLLVM-18.so.18.1

    # Verify it points to the right place
    target=$(readlink -f /usr/lib/x86_64-linux-gnu/libLLVM-18.so.18.1)
    if [ -f "$target" ]; then
        echo "✅ Symlink target exists: $target"
    else
        echo "❌ Symlink is broken! Target doesn't exist: $target"
    fi
else
    echo "❌ CRITICAL: Symlink missing - creating now..."
    ln -sf /usr/lib/llvm-18/lib/libLLVM.so.1 /usr/lib/x86_64-linux-gnu/libLLVM-18.so.18.1
    echo "✅ Symlink created"
fi
echo ""

# Check 3: GHDL can find LLVM library
echo "Check 3: GHDL-LLVM library resolution"
if ldd /usr/lib/ghdl/llvm/ghdl1-llvm 2>/dev/null | grep -q "libLLVM-18.so.18.1 =>"; then
    echo "✅ GHDL can find LLVM library"
    ldd /usr/lib/ghdl/llvm/ghdl1-llvm | grep LLVM
else
    echo "❌ GHDL cannot find LLVM library"
    echo "Running ldconfig to update cache..."
    ldconfig
fi
echo ""

# Check 4: GHDL functional test
echo "Check 4: GHDL analysis capability test"
cat > /tmp/preflight_test.vhd << 'EOF'
library ieee;
use ieee.std_logic_1164.all;

entity preflight_test is
end entity;

architecture rtl of preflight_test is
    signal test_signal : std_logic := '0';
begin
    test_signal <= '1';
end architecture;
EOF

if ghdl -a --std=08 /tmp/preflight_test.vhd 2>&1; then
    echo "✅ GHDL can analyze VHDL (LLVM backend working)"
    ghdl -e --std=08 preflight_test 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ GHDL can elaborate design (full toolchain working)"
    fi
else
    echo "❌ GHDL analysis FAILED - LLVM issue persists"
    echo "This is a BLOCKING issue - tests will fail"
fi

rm -f /tmp/preflight_test.vhd work-obj08.cf preflight_test
echo ""

echo "=========================================================================="
echo "PRE-FLIGHT COMPLETE"
echo "=========================================================================="
echo ""
```

**Decision Point:**
- If all checks pass → Continue with confidence
- If GHDL test fails → Continue anyway to document what breaks
- If setup script available → Run it for baseline

### Step 1.2: Run Setup Script (Baseline)

```bash
echo "Running setup script for baseline configuration..."
uv run python scripts/cloud_setup_with_ghdl.py
echo ""
```

---

## Phase 2: Full Test Suite Execution (Detailed Logging)

### Step 2.1: Create Enhanced Logging Structure

```bash
mkdir -p test_logs_v3/{passed,failed,analysis}
echo "Test run started: $(date -u '+%Y-%m-%d %H:%M:%S UTC')" > test_logs_v3/session_info.txt
echo "Expected results: 5/10 passing (v1.1.0-llvm-complete)" >> test_logs_v3/session_info.txt
echo "" >> test_logs_v3/session_info.txt
```

### Step 2.2: Enhanced Test Runner with Success Metrics

```bash
run_test_v3() {
    local test_name=$1
    local category=$2
    local expected_result=$3  # "PASS" or "FAIL"

    echo ""
    echo "=========================================================================="
    echo "TEST: $test_name"
    echo "Category: $category | Expected: $expected_result"
    echo "=========================================================================="

    start_time=$(date +%s)

    # Run test with full output capture
    if uv run python cocotb_tests/run.py "$test_name" > "test_logs_v3/raw_${test_name}.log" 2>&1; then
        status="PASS"
        end_time=$(date +%s)
        duration=$((end_time - start_time))

        # Move to passed directory
        mv "test_logs_v3/raw_${test_name}.log" "test_logs_v3/passed/${test_name}.log"

        # Extract success metrics
        echo "  ✅ PASSED (${duration}s)"

        # Analyze what the test actually validated
        echo "  Extracting test assertions..."
        if grep -q "PASS" "test_logs_v3/passed/${test_name}.log"; then
            pass_count=$(grep -c "PASS" "test_logs_v3/passed/${test_name}.log")
            echo "  Found $pass_count passing assertions"
        fi

        # Check if expected
        if [ "$expected_result" = "PASS" ]; then
            echo "  ✅ Result matches expectation"
        else
            echo "  ⚠️  UNEXPECTED PASS! (Expected to fail)"
        fi

    else
        status="FAIL"
        exit_code=$?
        end_time=$(date +%s)
        duration=$((end_time - start_time))

        # Move to failed directory
        mv "test_logs_v3/raw_${test_name}.log" "test_logs_v3/failed/${test_name}.log"

        echo "  ❌ FAILED (${duration}s, exit code: $exit_code)"

        # Quick failure categorization
        if grep -q "libLLVM" "test_logs_v3/failed/${test_name}.log"; then
            failure_type="LLVM_LIBRARY"
            echo "  Failure: LLVM library issue (should be fixed!)"
        elif grep -q "error:" "test_logs_v3/failed/${test_name}.log"; then
            failure_type="VHDL_ERROR"
            echo "  Failure: VHDL compilation error"
        elif grep -q "Missing source" "test_logs_v3/failed/${test_name}.log"; then
            failure_type="MISSING_SOURCE"
            echo "  Failure: Missing VHDL source file"
        else
            failure_type="UNKNOWN"
            echo "  Failure: Unknown cause"
        fi

        # Check if expected
        if [ "$expected_result" = "FAIL" ]; then
            echo "  ✅ Result matches expectation ($failure_type)"
        else
            echo "  ⚠️  UNEXPECTED FAILURE! (Expected to pass)"
        fi
    fi

    # Log to summary
    echo "$test_name|$category|$status|${duration}s|$expected_result|$failure_type" >> test_logs_v3/results_summary.csv
}

# Initialize CSV header
echo "test_name|category|status|duration|expected|failure_type" > test_logs_v3/results_summary.csv

echo ""
echo "=========================================================================="
echo "COMPREHENSIVE TEST SUITE - 10 TESTS"
echo "=========================================================================="
echo ""

# Run tests with expectations based on v1.1.0-llvm-complete
echo "UTILITIES (1 test) - Expected: 1 pass"
run_test_v3 "forge_util_clk_divider" "utilities" "PASS"

echo ""
echo "PACKAGES (4 tests) - Expected: 3 pass, 1 fail"
run_test_v3 "forge_lut_pkg" "packages" "FAIL"  # Known VHDL error
run_test_v3 "forge_voltage_3v3_pkg" "packages" "PASS"
run_test_v3 "forge_voltage_5v0_pkg" "packages" "PASS"
run_test_v3 "forge_voltage_5v_bipolar_pkg" "packages" "PASS"

echo ""
echo "DEBUGGING (1 test) - Expected: 1 pass"
run_test_v3 "forge_hierarchical_encoder" "debugging" "PASS"

echo ""
echo "PLATFORM (4 tests) - Expected: 4 fail (not implemented)"
run_test_v3 "platform_bpd_deployment" "platform" "FAIL"
run_test_v3 "platform_counter_poc" "platform" "FAIL"
run_test_v3 "platform_oscilloscope_capture" "platform" "FAIL"
run_test_v3 "platform_routing_integration" "platform" "FAIL"

echo ""
echo "=========================================================================="
echo "TEST SUITE COMPLETE"
echo "=========================================================================="
```

### Step 2.3: Generate Immediate Summary

```bash
echo ""
echo "=========================================================================="
echo "IMMEDIATE RESULTS SUMMARY"
echo "=========================================================================="
echo ""

passed=$(grep "|PASS|" test_logs_v3/results_summary.csv | wc -l)
failed=$(grep "|FAIL|" test_logs_v3/results_summary.csv | wc -l)
total=$((passed + failed))

echo "Total tests run: $total"
echo "Passed: $passed"
echo "Failed: $failed"
echo "Success rate: $(awk "BEGIN {printf \"%.1f\", ($passed/$total)*100}")%"
echo ""

echo "Expected results (v1.1.0-llvm-complete): 5/10 passed (50%)"
if [ $passed -eq 5 ]; then
    echo "✅ PERFECT MATCH - Results exactly as expected!"
elif [ $passed -gt 5 ]; then
    echo "✅ BETTER THAN EXPECTED - Bonus passes: $((passed - 5))"
elif [ $passed -lt 5 ]; then
    echo "⚠️  BELOW EXPECTATION - Missing passes: $((5 - passed))"
fi
echo ""

# Check for unexpected results
unexpected=$(grep -c "UNEXPECTED" test_logs_v3/raw_*.log 2>/dev/null || echo "0")
if [ $unexpected -gt 0 ]; then
    echo "⚠️  $unexpected unexpected result(s) - investigating..."
fi

echo ""
```

---

## Phase 3: Success Analysis (Prove What Works)

Analyze passing tests in detail - often overlooked but critical for confidence.

```bash
echo "=========================================================================="
echo "PHASE 3: SUCCESS ANALYSIS"
echo "=========================================================================="
echo ""

if [ $passed -eq 0 ]; then
    echo "❌ NO TESTS PASSED - Success analysis skipped"
    echo "   This indicates the LLVM fix did NOT work"
    echo ""
else
    echo "Analyzing $passed passing test(s) in detail..."
    echo ""

    for log in test_logs_v3/passed/*.log; do
        if [ -f "$log" ]; then
            test_name=$(basename "$log" .log)

            echo "----------------------------------------------------------------------"
            echo "SUCCESS ANALYSIS: $test_name"
            echo "----------------------------------------------------------------------"
            echo ""

            # Extract what was tested
            echo "What was validated:"
            if grep -q "GHDL" "$log"; then
                echo "  ✅ GHDL compilation successful"
            fi
            if grep -q "simulation" "$log"; then
                echo "  ✅ VHDL simulation executed"
            fi
            if grep -q "PASS" "$log"; then
                echo "  ✅ Test assertions passed"
                grep "PASS" "$log" | head -5 | sed 's/^/    /'
            fi

            # Check for any warnings (passing but with issues)
            if grep -qi "warning" "$log"; then
                warning_count=$(grep -ci "warning" "$log")
                echo "  ⚠️  $warning_count warning(s) found (not critical)"
            else
                echo "  ✅ No warnings - clean pass"
            fi

            # Execution time
            if grep -q "seconds" "$log"; then
                exec_time=$(grep "seconds" "$log" | head -1)
                echo "  ⏱️  Execution: $exec_time"
            fi

            # VHDL source analyzed
            echo ""
            echo "VHDL files tested:"
            grep "analyze.*\.vhd" "$log" | sed 's/^/  /' | head -5

            echo ""

            # Create detailed analysis file
            cat > "test_logs_v3/analysis/${test_name}_success.md" << EOF
# Success Analysis: $test_name

**Status:** ✅ PASSED
**Date:** $(date -u)

## What This Test Validates

$(grep -A5 "Building\|Running\|Testing" "$log" | head -20)

## Assertions Passed

$(grep "PASS" "$log" | head -10)

## VHDL Components Tested

$(grep "analyze.*\.vhd" "$log")

## Warnings (if any)

$(grep -i "warning" "$log" || echo "None - clean pass")

## Full Log

See: test_logs_v3/passed/${test_name}.log
EOF

            echo "  📄 Detailed analysis: test_logs_v3/analysis/${test_name}_success.md"
            echo ""
        fi
    done

    echo "----------------------------------------------------------------------"
    echo "SUCCESS SUMMARY"
    echo "----------------------------------------------------------------------"
    echo ""
    echo "Proven capabilities:"
    echo "  ✅ GHDL + LLVM 18 integration working"
    echo "  ✅ VHDL compilation successful"
    echo "  ✅ CocoTB test framework functional"
    echo "  ✅ Passing tests cover:"
    ls test_logs_v3/passed/*.log 2>/dev/null | xargs -n1 basename | sed 's/.log$//' | sed 's/^/       - /'
    echo ""
fi
```

---

## Phase 4: Failure Analysis (Forensic Deep-Dive)

```bash
echo "=========================================================================="
echo "PHASE 4: FAILURE ANALYSIS"
echo "=========================================================================="
echo ""

if [ $failed -eq 0 ]; then
    echo "🎉 NO FAILURES - All tests passed!"
    echo ""
else
    echo "Analyzing $failed failure(s) in detail..."
    echo ""

    # Categorize all failures
    llvm_fails=0
    vhdl_fails=0
    missing_fails=0
    unknown_fails=0

    for log in test_logs_v3/failed/*.log; do
        if [ -f "$log" ]; then
            test_name=$(basename "$log" .log)

            echo "----------------------------------------------------------------------"
            echo "FAILURE ANALYSIS: $test_name"
            echo "----------------------------------------------------------------------"
            echo ""

            # Determine failure category
            if grep -q "libLLVM" "$log"; then
                category="LLVM_LIBRARY"
                llvm_fails=$((llvm_fails + 1))
                echo "❌ Category: LLVM library issue"
                echo ""
                echo "Critical error:"
                grep "libLLVM\|error while loading" "$log" | head -5 | sed 's/^/  /'
                echo ""
                echo "🔍 DIAGNOSIS:"
                echo "  This should have been fixed by v1.1.0-llvm-complete!"
                echo "  Verify symlink exists: ls -lh /usr/lib/x86_64-linux-gnu/libLLVM-18.so.18.1"
                echo "  Possible causes:"
                echo "    - Setup script wasn't run"
                echo "    - Symlink creation failed"
                echo "    - Different architecture (not x86_64)"

            elif grep -q "no declaration for\|cannot match function" "$log"; then
                category="VHDL_FUNCTION_ERROR"
                vhdl_fails=$((vhdl_fails + 1))
                echo "❌ Category: VHDL function signature mismatch"
                echo ""
                echo "Specific errors:"
                grep "error:" "$log" | head -10 | sed 's/^/  /'
                echo ""
                echo "🔍 DIAGNOSIS:"
                echo "  Test wrapper uses functions that don't exist or have wrong signatures"
                echo ""
                echo "  Missing/incorrect functions:"
                grep "no declaration for\|cannot match" "$log" | sed 's/^/    /' | head -5
                echo ""
                echo "  SOLUTION:"
                echo "    1. Check vhdl/packages/forge_lut_pkg.vhd for available functions"
                echo "    2. Update test wrapper to use correct function names/signatures"
                echo "    3. Add missing 'use' clauses if needed"

            elif grep -q "Missing source" "$log"; then
                category="MISSING_SOURCE"
                missing_fails=$((missing_fails + 1))
                echo "❌ Category: Missing VHDL source files"
                echo ""
                echo "Expected files:"
                grep "Expected:" "$log" | sed 's/^/  /'
                echo ""
                echo "🔍 DIAGNOSIS:"
                echo "  Platform integration components not yet implemented"
                echo "  This is EXPECTED and documented as future work"
                echo ""
                echo "  SOLUTION:"
                echo "    - Design and implement platform VHDL components"
                echo "    - Or disable these tests until implemented"
                echo "    - Priority: LOW (deferred)"

            else
                category="UNKNOWN"
                unknown_fails=$((unknown_fails + 1))
                echo "❌ Category: Unknown failure"
                echo ""
                echo "Error output (first 20 lines):"
                head -20 "$log" | sed 's/^/  /'
                echo ""
                echo "🔍 DIAGNOSIS: Needs manual investigation"
            fi

            # Create detailed failure report
            cat > "test_logs_v3/analysis/${test_name}_failure.md" << EOF
# Failure Analysis: $test_name

**Status:** ❌ FAILED
**Category:** $category
**Date:** $(date -u)

## Error Summary

$(grep "error:\|Error:\|ERROR:" "$log" | head -10)

## Full Error Context

$(head -50 "$log")

## Diagnosis

[See above in terminal output]

## Recommended Fix

[See above in terminal output]

## Full Log

See: test_logs_v3/failed/${test_name}.log
EOF

            echo "  📄 Detailed report: test_logs_v3/analysis/${test_name}_failure.md"
            echo ""
        fi
    done

    echo "----------------------------------------------------------------------"
    echo "FAILURE BREAKDOWN"
    echo "----------------------------------------------------------------------"
    echo ""
    echo "Total failures: $failed"
    echo "  - LLVM library issues: $llvm_fails (should be 0 with v1.1.0!)"
    echo "  - VHDL function errors: $vhdl_fails (expected: 1 - forge_lut_pkg)"
    echo "  - Missing sources: $missing_fails (expected: 4 - platform)"
    echo "  - Unknown failures: $unknown_fails"
    echo ""

    # Alert if LLVM failures exist
    if [ $llvm_fails -gt 0 ]; then
        echo "🚨 ALERT: LLVM failures detected!"
        echo "   The v1.1.0-llvm-complete fix did NOT work properly"
        echo "   This requires immediate investigation"
        echo ""
    fi
fi
```

---

## Phase 5: Dual Commit Workflow

### Commit 1: Comprehensive Results Report

```bash
cat > "docs/diagnostic_reports/final_validation_v3_$(date -u '+%Y-%m-%d-%H-%M').md" << 'EOF'
# VHDL-FORGE Final Validation (v3 - Complete LLVM Fix)

**Date:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')
**Tag:** v1.1.0-llvm-complete
**Environment:** Claude Code Web
**Expected:** 5/10 passing (50% success rate)

---

## Executive Summary

**Actual Results:** X/10 passed (Y% success rate)
**Expected Results:** 5/10 passed (50% success rate)
**Outcome:** [MATCHES EXPECTATION / EXCEEDS EXPECTATION / BELOW EXPECTATION]

**Infrastructure Status:**
- LLVM 18 installation: [✅/❌]
- LLVM symlink (v1.1.0 fix): [✅/❌]
- GHDL functionality: [✅/❌]

---

## Pre-flight Verification

[Paste pre-flight check results]

**Verdict:** [Environment ready / Issues found]

---

## Test Results Summary

| Test Name | Status | Duration | Expected | Match |
|-----------|--------|----------|----------|-------|
[Paste from results_summary.csv]

**Passing Tests:** [X]
[List]

**Failing Tests:** [Y]
[List]

---

## Success Analysis

### Tests Passing (Proven Capabilities)

[For each passing test, include:]

#### [Test Name]
**What was validated:**
- [Specific capabilities proven]

**Assertions passed:**
- [List key passing assertions]

**VHDL components tested:**
- [List files]

**Analysis:** [Link to detailed analysis file]

---

## Failure Analysis

### Tests Failing (Issues Found)

[For each failing test, include:]

#### [Test Name]
**Failure category:** [LLVM/VHDL/MISSING/UNKNOWN]

**Error summary:**
```
[Key error lines]
```

**Diagnosis:**
[Root cause]

**Recommended fix:**
[Specific actionable steps]

**Analysis:** [Link to detailed analysis file]

---

## Failure Breakdown

**By Category:**
- LLVM library issues: X tests
- VHDL errors: X tests
- Missing sources: X tests
- Unknown: X tests

**Comparison to Expected:**
- Expected LLVM failures: 0
- Actual LLVM failures: X
- Status: [✅ As expected / ❌ Unexpected failures]

---

## Conclusions

### If Results Match Expectations (5/10 passing):

✅ **v1.1.0-llvm-complete is VALIDATED**

Proven working:
- GHDL + LLVM 18 integration
- Utilities tests
- Voltage package tests (3/4)
- Debugging tests

Known issues (expected):
- forge_lut_pkg: VHDL wrapper needs fixes
- Platform tests: Not implemented yet

**Recommendation:** Tag as production-ready

### If Results Exceed Expectations (>5/10 passing):

🎉 **BETTER THAN EXPECTED**

Additional tests passing:
- [List bonuses]

Possible causes:
- forge_lut_pkg wrapper was fixed
- Platform files were implemented

**Recommendation:** Update expectations and documentation

### If Results Below Expectations (<5/10 passing):

⚠️ **INVESTIGATION REQUIRED**

Missing passes:
- [List which expected passes failed]

Likely causes:
- LLVM symlink not created
- Setup script not run
- New issues introduced

**Recommendation:** Fix issues before production use

---

## Next Steps

[Based on actual results, provide specific ordered actions]

---

## Attached Artifacts

- Test logs: `test_logs_v3/passed/` and `test_logs_v3/failed/`
- Success analyses: `test_logs_v3/analysis/*_success.md`
- Failure analyses: `test_logs_v3/analysis/*_failure.md`
- Results summary: `test_logs_v3/results_summary.csv`

EOF

# Commit results
git add test_logs_v3/
git add "docs/diagnostic_reports/final_validation_v3_*.md"
git commit -m "test: Final validation results (v3) - v1.1.0-llvm-complete

Results: X/10 passed (Y% success rate)
Expected: 5/10 passed (50% success rate)
Outcome: [MATCH/EXCEED/BELOW]

Infrastructure verified:
- LLVM 18: [✅/❌]
- LLVM symlink: [✅/❌]
- GHDL: [✅/❌]

Passing tests (X):
[List]

Failing tests (Y):
[List with categories]

LLVM fix status: [SUCCESS/PARTIAL/FAILED]

Detailed analysis:
- docs/diagnostic_reports/final_validation_v3_*.md
- test_logs_v3/analysis/ (per-test breakdowns)
- test_logs_v3/results_summary.csv (machine-readable)

[If matches expectations:]
v1.1.0-llvm-complete VALIDATED for production use

[If below expectations:]
Issues require investigation before production"

git push
```

### Commit 2: Fixes and Documentation Updates

```bash
# Check if any quick fixes can be applied
echo ""
echo "=========================================================================="
echo "IDENTIFYING FIXABLE ISSUES"
echo "=========================================================================="
echo ""

fixable_count=0

# Check if LLVM symlink needs fixing
if [ $llvm_fails -gt 0 ]; then
    echo "Fix 1: LLVM symlink missing or broken"
    if [ ! -L "/usr/lib/x86_64-linux-gnu/libLLVM-18.so.18.1" ]; then
        echo "  Creating symlink now..."
        ln -sf /usr/lib/llvm-18/lib/libLLVM.so.1 /usr/lib/x86_64-linux-gnu/libLLVM-18.so.18.1
        fixable_count=$((fixable_count + 1))
        echo "  ✅ Symlink created - retest recommended"
    fi
fi

# Document any manual fixes needed
cat > "docs/diagnostic_reports/required_fixes_v3_$(date -u '+%Y-%m-%d').md" << 'EOF'
# Required Fixes (v3 Final Validation)

**Date:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')
**Session:** Final validation of v1.1.0-llvm-complete

---

## Automated Fixes Applied

[If fixable_count > 0:]
X fix(es) applied automatically during this session:
[List what was fixed]

[If fixable_count = 0:]
No automated fixes needed - environment as expected.

---

## Manual Fixes Required

### 1. forge_lut_pkg Test Wrapper

**Status:** Still requires manual intervention
**Priority:** MEDIUM
**Complexity:** Moderate
**Estimated effort:** 20-30 minutes

**Issue:**
Test wrapper uses incorrect function signatures.

**Required actions:**
1. Examine `vhdl/packages/forge_lut_pkg.vhd`
2. Identify correct function signatures
3. Update `cocotb_tests/cocotb_test_wrappers/forge_lut_pkg_tb_wrapper.vhd`
4. Add missing library imports

**Blocking:** 1 test (10% of suite)

---

### 2. Platform VHDL Implementation

**Status:** Deferred to future work
**Priority:** LOW
**Complexity:** HIGH
**Estimated effort:** Multiple days

**Issue:**
Platform integration components not implemented.

**Required actions:**
1. Design platform VHDL architecture
2. Implement 4 platform components
3. Create corresponding test infrastructure

**Blocking:** 4 tests (40% of suite)

**Note:** This is expected and documented as future work.

---

## Summary

**Immediate fixes:** X
**Manual fixes needed:** Y
**Deferred work:** Z

**Production readiness:**
[If all LLVM tests pass:]
✅ Ready for production use (5/10 tests passing as expected)

[If LLVM issues remain:]
❌ Not ready - LLVM issues must be resolved first

EOF

# Commit documentation
git add "docs/diagnostic_reports/required_fixes_v3_*.md"

if [ $fixable_count -gt 0 ]; then
    git commit -m "fix: Apply automated fixes found in v3 validation

Fixes applied: $fixable_count
[List what was fixed]

Expected improvement: [estimate]

Manual work still required:
- forge_lut_pkg wrapper (VHDL fixes)
- Platform components (implementation)

See: docs/diagnostic_reports/required_fixes_v3_*.md"
else
    git commit -m "docs: Document required manual fixes (v3 validation)

No automated fixes needed - environment as expected.

Manual work required:
- forge_lut_pkg: VHDL wrapper function signatures
- Platform tests: Implementation (deferred)

Current state: [X/10 passing]
Expected state: [5/10 passing]
Status: [VALIDATED/NEEDS WORK]

See: docs/diagnostic_reports/required_fixes_v3_*.md"
fi

git push
```

---

## Final User Summary

After both commits complete:

```markdown
========================================================================
FINAL VALIDATION SUMMARY (v3)
========================================================================

**Test Results:**
- Passed: X/10 (Y%)
- Failed: Z/10 (W%)
- Expected: 5/10 (50%)

**Outcome:** [VALIDATION SUCCESS / NEEDS INVESTIGATION]

**Infrastructure Status:**
- LLVM 18: [✅ Working / ❌ Issues]
- LLVM symlink (v1.1.0 fix): [✅ Applied / ❌ Missing]
- GHDL: [✅ Functional / ❌ Broken]

**Commits Created:**
1. Test results with comprehensive analysis
2. [Automated fixes / Documentation of manual work]

**Key Findings:**
[List 3-5 most important discoveries]

**Production Readiness:**
[✅ READY / ⚠️ READY WITH NOTES / ❌ NOT READY]

**Next Actions:**
1. [Most important next step]
2. [Second priority]
3. [Third priority]

**Reports Generated:**
- docs/diagnostic_reports/final_validation_v3_*.md (comprehensive)
- docs/diagnostic_reports/required_fixes_v3_*.md (action items)
- test_logs_v3/analysis/*.md (per-test detailed analyses)
- test_logs_v3/results_summary.csv (machine-readable results)

**Notable Achievements:**
[List what's working well]

**Remaining Challenges:**
[List what still needs work]

========================================================================
```

---

BEGIN EXECUTION NOW.
```

---

## What This Prompt Does

1. **Pre-flight verification** - Proves LLVM fix is in place before testing
2. **Enhanced logging** - Separate directories for passed/failed/analysis
3. **Success analysis** - Deep-dive on what WORKS (often missed)
4. **Forensic failure analysis** - Root cause for each failure
5. **Expected vs actual** - Tracks if results match predictions
6. **Dual commits:**
   - Commit 1: Complete results + analysis
   - Commit 2: Automated fixes OR manual work documentation

## Key Improvements Over v2

- ✅ **Proves success** - Analyzes passing tests in detail
- ✅ **Expectation tracking** - Compares actual vs expected (5/10)
- ✅ **Per-test analysis files** - Markdown reports for each test
- ✅ **CSV results** - Machine-readable for tracking over time
- ✅ **Production readiness** - Clear verdict on deployment status

## Expected Outcomes

**Best case:** 5/10 passing (matches expectation)
**Better:** 6+/10 passing (something got fixed unexpectedly)
**Investigate:** <5/10 passing (LLVM fix didn't work)

---

**Created:** 2025-11-09
**Version:** 3.0
**Purpose:** Final validation with complete LLVM fix
**Tag:** v1.1.0-llvm-complete
**Expected:** 5/10 tests passing (50% success rate)
**Duration:** 12-18 minutes
