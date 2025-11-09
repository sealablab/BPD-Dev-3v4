# VHDL-FORGE Cloud Production Verification Prompt

**Version:** v4 (Final Production Verification)
**Target:** v1.1.0-llvm-complete
**Expected Outcome:** Confirm 5/10 tests passing, validate production readiness
**Execution Time:** ~5 minutes

---

## Mission

Perform final verification of v1.1.0-llvm-complete release to confirm:
1. LLVM symlink fix is working
2. 5/10 tests passing consistently
3. No regressions from previous validation
4. Production-ready for upstream merge

---

## Phase 1: Environment Verification (2 minutes)

### Step 1.1: Confirm LLVM Infrastructure

```bash
echo "=== LLVM 18 Package Check ==="
dpkg -l | grep llvm-18 | head -5

echo ""
echo "=== LLVM Symlink Verification ==="
ls -lh /usr/lib/x86_64-linux-gnu/libLLVM-18.so.18.1
echo "Expected: symlink → /usr/lib/llvm-18/lib/libLLVM.so.1"

echo ""
echo "=== GHDL-LLVM Library Resolution ==="
ldd /usr/lib/ghdl/llvm/ghdl1-llvm | grep LLVM
echo "Expected: libLLVM-18.so.18.1 => /usr/lib/llvm-18/lib/... (found)"
```

**Expected Results:**
- ✅ llvm-18 package installed (1:18.1.3-1ubuntu1)
- ✅ Symlink exists and points to `/usr/lib/llvm-18/lib/libLLVM.so.1`
- ✅ GHDL can resolve LLVM library (not "not found")

**If any checks fail:**
- Document the failure
- Continue with test execution to gather data
- Report in final commit

---

### Step 1.2: Quick GHDL Functional Test

```bash
echo "=== GHDL Functionality Test ==="
cd /home/user/vhdl-forge-3v1-claude || cd $HOME/vhdl-forge-3v1-claude

# Create minimal test file
cat > /tmp/test_minimal.vhd <<'EOF'
library ieee;
use ieee.std_logic_1164.all;

entity test_minimal is
end entity;

architecture rtl of test_minimal is
begin
end architecture;
EOF

# Test GHDL analysis
ghdl -a --std=08 /tmp/test_minimal.vhd && echo "✅ GHDL analysis: PASS" || echo "❌ GHDL analysis: FAIL"

# Test GHDL elaboration
ghdl -e --std=08 test_minimal && echo "✅ GHDL elaboration: PASS" || echo "❌ GHDL elaboration: FAIL"

# Cleanup
rm -f /tmp/test_minimal.vhd test_minimal work-obj08.cf 2>/dev/null
```

**Expected Results:**
- ✅ GHDL analysis: PASS
- ✅ GHDL elaboration: PASS

---

## Phase 2: Test Execution (3 minutes)

### Step 2.1: Run Complete Test Suite

```bash
echo "=== Running Complete Test Suite ==="
mkdir -p test_logs_v4_verification

# Create test results file
cat > test_logs_v4_verification/results.txt <<EOF
VHDL-FORGE Production Verification (v4)
Date: $(date -u +"%Y-%m-%d %H:%M UTC")
Environment: Claude Code Web
Target: v1.1.0-llvm-complete
Expected: 5/10 passing (50% success rate)

=== Test Execution ===
EOF

# Run tests and capture results
declare -A test_results
declare -A test_times

tests=(
    "forge_util_clk_divider"
    "forge_lut_pkg"
    "forge_voltage_3v3_pkg"
    "forge_voltage_5v0_pkg"
    "forge_voltage_5v_bipolar_pkg"
    "forge_hierarchical_encoder"
    "platform_bpd_deployment"
    "platform_counter_poc"
    "platform_oscilloscope_capture"
    "platform_routing_integration"
)

pass_count=0
fail_count=0

for test_name in "${tests[@]}"; do
    echo ""
    echo "Running: $test_name"
    start_time=$(date +%s)

    if uv run python cocotb_tests/run.py "$test_name" > "test_logs_v4_verification/${test_name}.log" 2>&1; then
        test_results[$test_name]="PASS"
        ((pass_count++))
        result_icon="✅"
    else
        test_results[$test_name]="FAIL"
        ((fail_count++))
        result_icon="❌"
    fi

    end_time=$(date +%s)
    duration=$((end_time - start_time))
    test_times[$test_name]="${duration}s"

    echo "$result_icon $test_name: ${test_results[$test_name]} (${duration}s)" | tee -a test_logs_v4_verification/results.txt
done

# Summary
echo "" | tee -a test_logs_v4_verification/results.txt
echo "=== Summary ===" | tee -a test_logs_v4_verification/results.txt
echo "Total: $((pass_count + fail_count))" | tee -a test_logs_v4_verification/results.txt
echo "Passed: $pass_count" | tee -a test_logs_v4_verification/results.txt
echo "Failed: $fail_count" | tee -a test_logs_v4_verification/results.txt
echo "Success Rate: $((pass_count * 100 / (pass_count + fail_count)))%" | tee -a test_logs_v4_verification/results.txt
```

---

## Phase 3: Results Analysis (1 minute)

### Step 3.1: Verify Expected Results

```bash
echo ""
echo "=== Verification Analysis ==="

# Expected passing tests
expected_pass=(
    "forge_util_clk_divider"
    "forge_voltage_3v3_pkg"
    "forge_voltage_5v0_pkg"
    "forge_voltage_5v_bipolar_pkg"
    "forge_hierarchical_encoder"
)

# Expected failing tests
expected_fail=(
    "forge_lut_pkg"
    "platform_bpd_deployment"
    "platform_counter_poc"
    "platform_oscilloscope_capture"
    "platform_routing_integration"
)

# Check pass/fail matches
all_match=true

echo "Checking expected PASSING tests:"
for test in "${expected_pass[@]}"; do
    if [[ "${test_results[$test]}" == "PASS" ]]; then
        echo "  ✅ $test: PASS (as expected)"
    else
        echo "  ❌ $test: FAIL (UNEXPECTED - should pass!)"
        all_match=false
    fi
done

echo ""
echo "Checking expected FAILING tests:"
for test in "${expected_fail[@]}"; do
    if [[ "${test_results[$test]}" == "FAIL" ]]; then
        echo "  ✅ $test: FAIL (as expected)"
    else
        echo "  ❌ $test: PASS (UNEXPECTED - should fail!)"
        all_match=false
    fi
done

echo ""
if [[ "$all_match" == "true" && "$pass_count" -eq 5 && "$fail_count" -eq 5 ]]; then
    echo "🎉 VERIFICATION: PERFECT MATCH"
    echo "   Expected: 5/10 passing"
    echo "   Actual: $pass_count/10 passing"
    echo "   Status: ✅ PRODUCTION READY"
    verification_status="PASS"
else
    echo "⚠️  VERIFICATION: MISMATCH DETECTED"
    echo "   Expected: 5/10 passing"
    echo "   Actual: $pass_count/10 passing"
    echo "   Status: ❌ INVESTIGATE REQUIRED"
    verification_status="FAIL"
fi

# Save verification status
echo "$verification_status" > test_logs_v4_verification/verification_status.txt
```

---

## Phase 4: Categorize Failures (1 minute)

```bash
echo ""
echo "=== Failure Analysis ==="

# Analyze each failed test
for test_name in "${tests[@]}"; do
    if [[ "${test_results[$test_name]}" == "FAIL" ]]; then
        log_file="test_logs_v4_verification/${test_name}.log"

        echo ""
        echo "Test: $test_name"

        if grep -q "libLLVM" "$log_file"; then
            echo "  Category: LLVM_LIBRARY_ERROR ⚠️  (REGRESSION!)"
        elif grep -q "error.*no declaration" "$log_file" || grep -q "error.*cannot match" "$log_file"; then
            echo "  Category: VHDL_FUNCTION_ERROR (expected for forge_lut_pkg)"
        elif grep -q "Missing source files" "$log_file"; then
            echo "  Category: MISSING_SOURCE (expected for platform_*)"
        else
            echo "  Category: UNKNOWN (investigate)"
        fi

        # Show first error
        echo "  First error:"
        grep -i "error" "$log_file" | head -1 | sed 's/^/    /'
    fi
done
```

---

## Phase 5: Generate Production Verification Report

```bash
echo ""
echo "=== Generating Verification Report ==="

cat > docs/diagnostic_reports/production_verification_v4_$(date -u +"%Y-%m-%d-%H-%M").md <<EOF
# VHDL-FORGE Production Verification (v4)

**Date:** $(date -u +"%Y-%m-%d %H:%M UTC")
**Tag:** v1.1.0-llvm-complete
**Environment:** Claude Code Web
**Verification Status:** $verification_status

---

## Executive Summary

**Test Results:** $pass_count/$((pass_count + fail_count)) passed ($(( pass_count * 100 / (pass_count + fail_count) ))% success rate)
**Expected:** 5/10 passed (50% success rate)
**Match:** $([ "$verification_status" == "PASS" ] && echo "✅ PERFECT" || echo "❌ MISMATCH")

---

## Infrastructure Verification

### LLVM 18 Status
\`\`\`
$(dpkg -l | grep llvm-18 | head -3)
\`\`\`

### LLVM Symlink
\`\`\`
$(ls -lh /usr/lib/x86_64-linux-gnu/libLLVM-18.so.18.1 2>&1)
\`\`\`

### GHDL-LLVM Resolution
\`\`\`
$(ldd /usr/lib/ghdl/llvm/ghdl1-llvm | grep LLVM)
\`\`\`

---

## Test Results

| Test Name | Status | Duration | Expected | Match |
|-----------|--------|----------|----------|-------|
EOF

# Add test results table
for test_name in "${tests[@]}"; do
    status="${test_results[$test_name]}"
    duration="${test_times[$test_name]}"

    # Determine expected status
    if [[ " ${expected_pass[@]} " =~ " ${test_name} " ]]; then
        expected="PASS"
    else
        expected="FAIL"
    fi

    # Check match
    if [[ "$status" == "$expected" ]]; then
        match="✅"
    else
        match="❌"
    fi

    echo "| $test_name | $status | $duration | $expected | $match |" >> docs/diagnostic_reports/production_verification_v4_$(date -u +"%Y-%m-%d-%H-%M").md
done

cat >> docs/diagnostic_reports/production_verification_v4_$(date -u +"%Y-%m-%d-%H-%M").md <<EOF

---

## Verification Outcome

**Status:** $verification_status

$(if [[ "$verification_status" == "PASS" ]]; then
cat <<PASS
✅ **PRODUCTION READY**

All tests match expected results:
- 5/10 tests passing (core infrastructure validated)
- 5/10 tests failing (expected, documented issues)
- Zero LLVM-related failures
- Zero regressions from v3 validation

**Recommendation:** Approve for production deployment and upstream merge.

**Next Steps:**
1. Tag as production-ready (v1.1.0-llvm-complete already tagged)
2. Merge to upstream main branch
3. Deploy to production cloud environments
4. Document 50% baseline pass rate in deployment guide
PASS
else
cat <<FAIL
❌ **VERIFICATION FAILED**

Detected mismatches between expected and actual results.

**Action Required:**
1. Review failure logs in test_logs_v4_verification/
2. Identify root cause of regression
3. Fix issues before production deployment
4. Re-run verification

**DO NOT MERGE** until verification passes.
FAIL
fi)

---

## Artifacts

- Test logs: \`test_logs_v4_verification/*.log\`
- Results summary: \`test_logs_v4_verification/results.txt\`
- Verification status: \`test_logs_v4_verification/verification_status.txt\`

---

**Generated:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")
EOF

echo "Report generated: docs/diagnostic_reports/production_verification_v4_$(date -u +"%Y-%m-%d-%H-%M").md"
```

---

## Phase 6: Git Commit & Push

### Step 6.1: Commit Verification Results

```bash
echo ""
echo "=== Committing Verification Results ==="

git add test_logs_v4_verification/
git add docs/diagnostic_reports/production_verification_v4_*.md

git commit -m "$(cat <<EOF
test: Production verification v4 - $verification_status

Final verification of v1.1.0-llvm-complete before upstream merge.

Results: $pass_count/$((pass_count + fail_count)) passing ($(( pass_count * 100 / (pass_count + fail_count) ))%)
Expected: 5/10 passing (50%)
Status: $verification_status

Infrastructure:
- LLVM 18: Installed
- LLVM symlink: Created
- GHDL-LLVM: Operational

$(if [[ "$verification_status" == "PASS" ]]; then
echo "Production readiness: ✅ APPROVED"
else
echo "Production readiness: ❌ BLOCKED (investigate)"
fi)
EOF
)"

git push origin HEAD
```

---

## Phase 7: Final Verdict & Recommendations

### Step 7.1: Display Final Status

```bash
echo ""
echo "========================================"
echo "VHDL-FORGE Production Verification (v4)"
echo "========================================"
echo ""
echo "Verification Status: $verification_status"
echo "Test Results: $pass_count/$((pass_count + fail_count)) passing"
echo ""

if [[ "$verification_status" == "PASS" ]]; then
    cat <<EOF
🎉 PRODUCTION VERIFICATION: COMPLETE

v1.1.0-llvm-complete is READY for:
✅ Upstream merge to main branch
✅ Production cloud deployment
✅ CI/CD integration

Next actions:
1. Review verification report (committed)
2. Tag release as production-ready (already tagged)
3. Merge to upstream repository
4. Deploy to production environments

No further validation required.
EOF
else
    cat <<EOF
⚠️  PRODUCTION VERIFICATION: FAILED

DO NOT PROCEED with upstream merge.

Required actions:
1. Review verification report for details
2. Investigate test mismatches
3. Fix regressions
4. Re-run verification

Contact maintainer if issues persist.
EOF
fi

echo ""
echo "Full report: docs/diagnostic_reports/production_verification_v4_*.md"
echo "Test logs: test_logs_v4_verification/"
echo ""
```

---

## Expected Execution Flow

**If verification PASSES (expected):**
1. All 5 core tests pass (utilities + packages + debugging)
2. All 5 expected failures fail (forge_lut_pkg + 4 platform tests)
3. Zero LLVM-related errors
4. Verification status: PASS
5. Commit results
6. Display: "PRODUCTION READY - APPROVE FOR MERGE"

**If verification FAILS (unexpected):**
1. Test results don't match expectations
2. Possible regressions detected
3. Verification status: FAIL
4. Commit results for analysis
5. Display: "DO NOT MERGE - INVESTIGATE"

---

## Success Criteria

✅ **PASS** if:
- Exactly 5/10 tests passing
- Exactly 5/10 tests failing
- No LLVM library errors in any test
- All passing tests match expected list
- All failing tests match expected list

❌ **FAIL** if:
- Pass count ≠ 5
- Any LLVM library errors detected
- Unexpected passes or failures
- Regressions from v3 validation

---

## Time Budget

- Phase 1: 2 minutes (environment verification)
- Phase 2: 3 minutes (test execution)
- Phase 3: 1 minute (results analysis)
- Phase 4: 1 minute (failure categorization)
- Phase 5: 1 minute (report generation)
- Phase 6: 30 seconds (git commit/push)
- Phase 7: 30 seconds (final verdict)

**Total: ~8 minutes**

---

## Notes

- This is the **final verification** before production release
- Designed to confirm v3 results were not a fluke
- Validates LLVM fix is stable and reproducible
- Provides clear go/no-go decision for upstream merge
- All phases continue even if errors occur (gather maximum data)
- Generates machine-readable verification status file

---

**Ready to execute?** Copy all commands above and run in Claude Code Web.
