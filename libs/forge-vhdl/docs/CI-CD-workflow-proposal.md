# CI/CD Workflow Proposal - VHDL-FORGE 3.0

**Target Audience:** Small development teams (1-3 developers)
**Philosophy:** Simple, fast, container-based
**Platform:** GitHub Actions + Linux only

---

## Why CI/CD for Small Teams?

Even with 1-3 developers, automated testing catches issues before merge:

- ✅ **Catch GHDL simulation errors** before they reach `main`
- ✅ **Verify P1 tests pass** in clean environment (not just "works on my machine")
- ✅ **Green checkmark on PRs** - Quick confidence signal
- ✅ **Email on failure** - Know immediately when something breaks

**Cost:** $0 (GitHub Actions free tier: 2,000 min/month for public repos, 500 min/month for private)

---

## Proposed Strategy

### Simple 2-Tier Approach

**Tier 1: Pull Requests**
```
Trigger: Every PR commit
Tests: P1 only (all components)
Runtime: ~2 minutes
Goal: Fast feedback, catch obvious breaks
```

**Tier 2: Main Branch**
```
Trigger: Merge to main
Tests: P1 only (all components)
Runtime: ~2 minutes
Goal: Verify main stays healthy
```

**No Tier 3:** For a small team, manual testing before releases is fine. Run P2/P3 locally when needed.

---

## What Gets Tested

### P1 Tests (Fast, LLM-Optimized)

All component tests at P1 level:
- `forge_util_clk_divider` - Clock divider tests
- `forge_lut_pkg` - LUT package tests
- `forge_voltage_3v3_pkg` - 3.3V voltage utilities
- `forge_voltage_5v0_pkg` - 5.0V voltage utilities
- `forge_voltage_5v_bipolar_pkg` - ±5V voltage utilities
- `forge_hierarchical_encoder` - HVS encoder tests
- `platform_counter_poc` - Counter example integration
- `platform_forge_control` - FORGE control scheme

**Plus:** Python unit tests via `pytest tests/`

**Total Runtime:** ~2 minutes (P1 tests are designed to be fast)

---

## GitHub Actions Workflow

### Ready-to-Use Configuration

Save as `.github/workflows/test.yml`:

```yaml
name: VHDL Tests

on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]

jobs:
  test:
    name: P1 Tests (GHDL 5.0.1)
    runs-on: ubuntu-latest

    container:
      image: ghdl/ghdl:ubuntu22-llvm-5.0

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.cargo/bin" >> $GITHUB_PATH

      - name: Install Python dependencies
        run: uv sync

      - name: Verify GHDL installation
        run: ghdl --version

      - name: Run P1 CocoTB tests
        run: uv run python cocotb_tests/run.py --all

      - name: Run Python unit tests
        run: uv run pytest tests/
```

**That's it.** Simple, fast, effective.

---

## Setup Instructions

### Step 1: Create Workflow File

```bash
mkdir -p .github/workflows
# Copy the YAML above to .github/workflows/test.yml
```

### Step 2: Commit and Push

```bash
git add .github/workflows/test.yml
git commit -m "ci: Add GitHub Actions for P1 tests"
git push origin main
```

### Step 3: Verify

1. Go to your GitHub repo → **Actions** tab
2. You should see "VHDL Tests" workflow
3. Create a test PR to trigger it
4. Watch the green checkmark appear! ✅

---

## What You Get

### On Every Pull Request

1. **Automated Tests** - P1 tests run automatically
2. **Status Badge** - Green ✅ or red ❌ on PR
3. **Quick Feedback** - Know in 2 minutes if PR is safe to merge
4. **Clean Environment** - Tests run in fresh GHDL 5.0.1 container (no local quirks)

### On Every Main Commit

1. **Regression Detection** - Catch if `main` breaks
2. **Email Notification** - GitHub emails you if tests fail
3. **History** - See all test runs in Actions tab

---

## Interpreting Results

### ✅ Success (What You Want)

```
✓ Verify GHDL installation
✓ Run P1 CocoTB tests
✓ Run Python unit tests

All checks passed
```

**Action:** Safe to merge!

### ❌ Failure (What to Do)

```
✗ Run P1 CocoTB tests
  FAILED: test_forge_util_clk_divider::test_reset
```

**Action:**
1. Click "Details" to see logs
2. Fix the issue locally
3. Push new commit (re-triggers tests)
4. Repeat until green

---

## Cost Analysis

### GitHub Actions Free Tier

**Public repos:** 2,000 minutes/month free
**Private repos:** 500 minutes/month free

**Usage per test run:** ~2 minutes
**Tests per month (example):** 100 commits × 2 min = 200 min/month

**Verdict:** Well within free tier for small teams.

---

## Future Enhancements (Optional)

If your team grows or needs change, consider:

### Enhancement 1: P2 Tests on Main

Run comprehensive P2 tests only on `main` branch (not PRs):

```yaml
- name: Run P2 tests on main
  if: github.ref == 'refs/heads/main'
  run: TEST_LEVEL=P2_INTERMEDIATE uv run python cocotb_tests/run.py --all
```

**Cost:** +5 minutes per main commit

### Enhancement 2: Test Coverage

Add Python coverage reporting:

```yaml
- name: Run tests with coverage
  run: uv run pytest tests/ --cov=python --cov-report=term
```

**Benefit:** Know which code is tested

### Enhancement 3: Branch Protection

Require tests to pass before merging:

1. GitHub repo → Settings → Branches
2. Add rule for `main`
3. Enable "Require status checks to pass"
4. Select "P1 Tests (GHDL 5.0.1)"

**Benefit:** Can't accidentally merge broken code

---

## When NOT to Use CI/CD

For a small team, skip CI/CD if:

- ❌ You're the only developer (just run tests locally)
- ❌ Project is experimental/prototype (tests change too often)
- ❌ Tests take >10 minutes (P1 tests are fast, but if you add heavy P3 tests, reconsider)

**Current State:** Your P1 tests are ~2 minutes, perfect for CI/CD.

---

## Recommended Starting Point

**Week 1:** Add the workflow, observe
- See how often tests catch issues
- Adjust if too noisy or too slow

**Week 2:** Decide on branch protection
- If tests are stable, enable required checks
- If tests are flaky, fix them first

**Month 1:** Evaluate
- Are tests catching real issues? → Keep it
- Are tests always green? → Consider adding P2 to main
- Are tests slow? → Optimize or reduce scope

---

## Summary

**What:** Run P1 tests on every PR and main commit
**Why:** Catch bugs early, minimal overhead
**How:** One YAML file, 3 steps to setup
**Cost:** Free (within GitHub Actions limits)
**Maintenance:** Zero (unless tests break)

**Philosophy:** Keep it simple. P1 tests are fast (<20 lines output, <2 min runtime) and designed for this exact use case.

---

## Quick Start Checklist

```bash
# 1. Create workflow file
mkdir -p .github/workflows
cat > .github/workflows/test.yml << 'EOF'
# Paste YAML from above
EOF

# 2. Commit
git add .github/workflows/test.yml
git commit -m "ci: Add P1 test automation"

# 3. Push
git push origin main

# 4. Check GitHub Actions tab
# You should see the workflow running!
```

---

**Author:** VHDL-FORGE Team
**Version:** 1.0
**Last Updated:** 2025-11-08
**Status:** Proposed (ready to implement)
