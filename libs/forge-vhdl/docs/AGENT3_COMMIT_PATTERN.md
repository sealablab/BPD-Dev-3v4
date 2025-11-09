# Agent 3: "Commit Often" Pattern Walkthrough

**Purpose:** Demonstrate the incremental git commit workflow for cocotb-progressive-test-runner agent
**Audience:** Users reviewing agent work, developers understanding agent behavior
**Version:** 1.0.0 (2025-11-09)

---

## Overview

Agent 3 (cocotb-progressive-test-runner) uses **"commit often, use update as message"** pattern to create a granular audit trail of test implementation work.

**Key principle:** Each meaningful step gets its own commit with a descriptive message.

---

## Why This Pattern?

### Traditional Approach (Single Commit)

```bash
# All work done, then one commit at end
git commit -m "Add tests for edge_detector"

# Git log shows:
c8a3f2b Add tests for edge_detector (157 files changed, 3421 insertions)
```

**Problems:**
- ❌ Can't see what the agent did step-by-step
- ❌ Hard to debug if something broke
- ❌ No visibility into agent's problem-solving process
- ❌ All-or-nothing rollback (can't cherry-pick fixes)

### "Commit Often" Pattern (Incremental Commits)

```bash
# Each step gets a commit
git commit -m "test(edge_detector): Add constants file with test values and helpers"
git commit -m "test(edge_detector): Add P1 basic tests (4 tests)"
git commit -m "test(edge_detector): Add progressive test orchestrator"
git commit -m "test(edge_detector): Register in test_configs.py"
git commit -m "test(edge_detector): Initial test run (2/4 passing)"
git commit -m "test(edge_detector): Fix timing model - edge detection on same cycle"
git commit -m "test(edge_detector): All P1 tests passing (4/4) ✅"

# Git log shows:
a7e3f1c test(edge_detector): All P1 tests passing (4/4) ✅
d9b2c4a test(edge_detector): Fix timing model - edge detection on same cycle
f3a8e5b test(edge_detector): Initial test run (2/4 passing)
b1c9d7e test(edge_detector): Register in test_configs.py
e4f2a8c test(edge_detector): Add progressive test orchestrator
c5d1b3e test(edge_detector): Add P1 basic tests (4 tests)
a2b7f9d test(edge_detector): Add constants file with test values and helpers
```

**Benefits:**
- ✅ **Progress visibility** - See exactly what agent did and when
- ✅ **Easy debugging** - Pinpoint the exact commit where something broke
- ✅ **Selective rollback** - Cherry-pick or revert specific changes
- ✅ **Audit trail** - Git log tells the story of agent's work
- ✅ **Review-friendly** - Understand agent decisions at each step

---

## Commit Pattern Template

### Step 1: Constants File Created

**When:** After implementing `<component>_constants.py`

```bash
git add cocotb_tests/components/<component>_tests/<component>_constants.py
git commit -m "test(<component>): Add constants file with test values and helpers"
```

**Example:**
```bash
git add cocotb_tests/components/forge_util_edge_detector_tests/forge_util_edge_detector_constants.py
git commit -m "test(edge_detector): Add constants file with test values and helpers"
```

**What's included:**
- `MODULE_NAME`, `HDL_SOURCES`, `HDL_TOPLEVEL` constants
- `TestValues` class with P1/P2/P3 test data
- Helper functions (`get_output`, `calculate_expected`, etc.)
- `ErrorMessages` class with formatted error strings

---

### Step 2: P1 Test Module Created

**When:** After implementing `P1_<component>_basic.py`

```bash
git add cocotb_tests/components/<component>_tests/P1_<component>_basic.py
git commit -m "test(<component>): Add P1 basic tests (X tests)"
```

**Example:**
```bash
git add cocotb_tests/components/forge_util_edge_detector_tests/P1_forge_util_edge_detector_basic.py
git commit -m "test(edge_detector): Add P1 basic tests (4 tests)"
```

**What's included:**
- `ComponentBasicTests` class inheriting from `TestBase`
- `setup()` method (clock, reset)
- `run_p1_basic()` method (test suite entry point)
- All P1 test methods (`test_reset`, `test_basic_op`, etc.)
- CocoTB test decorator entry point

---

### Step 3: Progressive Orchestrator Created

**When:** After implementing `test_<component>_progressive.py`

```bash
git add cocotb_tests/components/test_<component>_progressive.py
git commit -m "test(<component>): Add progressive test orchestrator"
```

**Example:**
```bash
git add cocotb_tests/components/test_forge_util_edge_detector_progressive.py
git commit -m "test(edge_detector): Add progressive test orchestrator"
```

**What's included:**
- `get_test_level()` function (reads TEST_LEVEL env var)
- `test_<component>_progressive()` CocoTB test
- TEST_LEVEL routing (P1_BASIC, P2_INTERMEDIATE, P3_COMPREHENSIVE)
- Imports for all test level classes

---

### Step 4: test_configs.py Updated

**When:** After adding entry to `TESTS_CONFIG` dictionary

```bash
git add cocotb_tests/test_configs.py
git commit -m "test(<component>): Register in test_configs.py"
```

**Example:**
```bash
git add cocotb_tests/test_configs.py
git commit -m "test(edge_detector): Register in test_configs.py"
```

**What's included:**
- New `TestConfig` entry with:
  - `name` (component name)
  - `hdl_sources` (paths to VHDL files)
  - `hdl_toplevel` (entity name, lowercase!)
  - `test_module` (progressive orchestrator module name)

---

### Step 5: First Test Run Attempt

**When:** After first `uv run python cocotb_tests/run.py <component>` execution

```bash
git add cocotb_tests/components/<component>_tests/
git commit -m "test(<component>): Initial test run (X/Y passing)"
```

**Example:**
```bash
git add cocotb_tests/components/forge_util_edge_detector_tests/
git commit -m "test(edge_detector): Initial test run (2/4 passing)"
```

**What's included:**
- Any test modifications made during first run
- Possibly test wrapper VHDL (if created)
- Initial test results documented in commit message

**Note:** Include actual pass/fail counts in message (e.g., "2/4 passing", not "some passing")

---

### Step 6: Debug Iterations (One Commit Per Fix)

**When:** After fixing each distinct issue

```bash
git add <files changed>
git commit -m "test(<component>): <what was fixed>"
```

**Examples:**
```bash
# Timing issue
git add cocotb_tests/components/forge_util_edge_detector_tests/P1_forge_util_edge_detector_basic.py
git commit -m "test(edge_detector): Fix timing model - edge detection on same cycle"

# Signed integer access
git add cocotb_tests/components/voltage_converter_tests/voltage_converter_constants.py
git commit -m "test(voltage_converter): Fix signed integer access in get_output helper"

# Integer division mismatch
git add cocotb_tests/components/pwm_generator_tests/pwm_generator_constants.py
git commit -m "test(pwm_generator): Fix integer division (// vs /) in duty cycle calculation"

# GHDL generic syntax
git add cocotb_tests/test_configs.py
git commit -m "test(debouncer): Use VHDL default generic (GHDL syntax limitation)"

# Test wrapper creation
git add cocotb_tests/cocotb_test_wrappers/lut_pkg_tb_wrapper.vhd
git add cocotb_tests/test_configs.py
git commit -m "test(lut_pkg): Add test wrapper for real/boolean type workaround"
```

**Key principles:**
- One commit per issue fixed
- Describe **what** was fixed and **why** (if not obvious)
- Include context (e.g., "GHDL syntax limitation", "CocoTB workaround")

---

### Step 7: Final Passing State

**When:** All P1 tests passing, output meets <20 line target

```bash
git add cocotb_tests/components/<component>_tests/
git commit -m "test(<component>): All P1 tests passing (X/X) ✅

- Y lines output (Z% under target)
- Runtime <Ns
- GHDL filter enabled"
```

**Example:**
```bash
git add cocotb_tests/components/forge_util_edge_detector_tests/
git commit -m "test(edge_detector): All P1 tests passing (4/4) ✅

- 8 lines output (60% under target)
- Runtime <1s
- GHDL filter enabled"
```

**What's included:**
- Final test code (all passing)
- Metrics in commit body:
  - Line count (vs. <20 target)
  - Runtime (vs. <5s target)
  - GHDL filter status

**Note:** Use ✅ emoji in message to signal completion

---

## Commit Message Format

### Pattern

```
test(<component>): <what changed>

[optional body with details/metrics]
```

### Components

- **Prefix:** `test` (indicates test code, not VHDL component)
- **Scope:** `(<component>)` (short component name, not full forge_util_* name if obvious)
- **Description:** Concise present-tense action (e.g., "Add", "Fix", "Update")
- **Body:** (optional) Additional context, metrics, or multi-line details

### Examples

**Good:**
```
test(edge_detector): Add constants file with test values and helpers
test(edge_detector): Fix timing model - edge detection on same cycle
test(edge_detector): All P1 tests passing (4/4) ✅
```

**Bad:**
```
Added test files                           ❌ Too vague, no component
test(forge_util_edge_detector): ...        ❌ Scope too long
Fixed tests                                ❌ No component, no specifics
test(edge_detector): Tests work now        ❌ Unprofessional, no details
```

---

## Real-World Example: forge_util_edge_detector

**This was a successful test run that Agent 3 would have committed like this:**

```bash
# Step 1: Constants file
git add cocotb_tests/components/forge_util_edge_detector_tests/forge_util_edge_detector_constants.py
git commit -m "test(edge_detector): Add constants file with test values and helpers"

# Step 2: P1 tests
git add cocotb_tests/components/forge_util_edge_detector_tests/P1_forge_util_edge_detector_basic.py
git commit -m "test(edge_detector): Add P1 basic tests (4 tests)"

# Step 3: Orchestrator
git add cocotb_tests/components/test_forge_util_edge_detector_progressive.py
git commit -m "test(edge_detector): Add progressive test orchestrator"

# Step 4: Config registration
git add cocotb_tests/test_configs.py
git commit -m "test(edge_detector): Register in test_configs.py"

# Step 5: First run (hypothetical - some tests failing)
git add cocotb_tests/components/forge_util_edge_detector_tests/
git commit -m "test(edge_detector): Initial test run (2/4 passing)"

# Step 6: Debug - fix timing assumption
git add cocotb_tests/components/forge_util_edge_detector_tests/P1_forge_util_edge_detector_basic.py
git commit -m "test(edge_detector): Fix timing model - edge detection on same cycle

Was expecting edge_detected on cycle AFTER transition.
VHDL analysis shows edge_detected is combinational output.
Fixed: Read edge_detected immediately after rising clock edge."

# Step 7: All passing
git add cocotb_tests/components/forge_util_edge_detector_tests/
git commit -m "test(edge_detector): All P1 tests passing (4/4) ✅

- 8 lines output (60% under target)
- Runtime <1s
- GHDL filter enabled"
```

**Git log result:**
```
$ git log --oneline --author="Claude" --grep="test(edge_detector)"
a7e3f1c test(edge_detector): All P1 tests passing (4/4) ✅
d9b2c4a test(edge_detector): Fix timing model - edge detection on same cycle
f3a8e5b test(edge_detector): Initial test run (2/4 passing)
b1c9d7e test(edge_detector): Register in test_configs.py
e4f2a8c test(edge_detector): Add progressive test orchestrator
c5d1b3e test(edge_detector): Add P1 basic tests (4 tests)
a2b7f9d test(edge_detector): Add constants file with test values and helpers
```

**Benefits of this history:**
1. **Clear narrative** - Can see agent's thought process
2. **Debugging** - If timing issue came back, can find commit d9b2c4a easily
3. **Review** - Reviewer can see incremental progress, not one huge diff
4. **Rollback** - Can revert just the timing fix if it caused issues elsewhere
5. **Learning** - New developers see how to solve timing model bugs

---

## Viewing Agent Work

### See all commits for a component

```bash
git log --oneline --grep="test(edge_detector)"
```

### See what changed in each step

```bash
# Show full diff for constants file commit
git show a2b7f9d

# Show stats for all test commits
git log --stat --grep="test(edge_detector)"
```

### Review a specific fix

```bash
# See what the timing fix changed
git show d9b2c4a
```

### Compare first attempt vs final

```bash
# Diff between first run and final passing state
git diff f3a8e5b..a7e3f1c
```

---

## Anti-Patterns (What NOT to Do)

### ❌ Batching commits

```bash
# BAD: Grouping multiple steps into one commit
git add cocotb_tests/components/edge_detector_tests/
git add cocotb_tests/test_configs.py
git commit -m "test(edge_detector): Add tests and config"
```

**Why bad:** Can't see individual steps, loses audit trail

### ❌ Vague messages

```bash
# BAD: No details about what was fixed
git commit -m "test(edge_detector): Fix bug"
```

**Why bad:** Future developers (or yourself!) won't know what bug

### ❌ No component scope

```bash
# BAD: Missing component name
git commit -m "test: Add constants file"
```

**Why bad:** Hard to filter commits by component

### ❌ Unprofessional language

```bash
# BAD: Casual/emotional language
git commit -m "test(edge_detector): Finally works!!! 🎉🎉🎉"
```

**Why bad:** Unprofessional, no technical details (✅ emoji OK for final commit only)

### ❌ Future tense

```bash
# BAD: Future tense (sounds like a plan, not a done action)
git commit -m "test(edge_detector): Will add constants file"
```

**Why bad:** Commits describe what WAS done, not what WILL be done

---

## Integration with Agent Workflow

### Agent 3 Definition Reference

The full "commit often" pattern is documented in:
```
.claude/agents/cocotb-progressive-test-runner/agent.md
```

**Section:** "Git Workflow: Commit Often, Use Update as Message"

### When Agent 3 Runs

1. User invokes Agent 3 (either locally or in Claude Web)
2. Agent reads test strategy from Agent 2
3. Agent implements files **one at a time**
4. **After each file:** Agent commits with descriptive message
5. Agent runs tests
6. **After first run:** Agent commits with pass/fail status
7. **For each fix:** Agent commits with fix description
8. **Final state:** Agent commits with metrics (✅ emoji)

### User Benefits

- **Real-time progress** - Can watch git log to see agent progress
- **Early intervention** - Can stop agent if it goes wrong direction
- **Post-mortem analysis** - If final result has issues, can trace back to specific commit
- **Learning** - Can replay agent's problem-solving process

---

## Summary

**"Commit often, use update as message"** turns Agent 3's work into a **narrative git history**.

**Key benefits:**
1. ✅ Progress visibility
2. ✅ Easy debugging
3. ✅ Selective rollback
4. ✅ Audit trail
5. ✅ Review-friendly

**Pattern:**
- Constants file → Commit
- P1 tests → Commit
- Orchestrator → Commit
- Config → Commit
- First run → Commit
- Each fix → Commit
- Final passing → Commit (with ✅ and metrics)

**Result:** Git log becomes a **step-by-step record** of Agent 3's test implementation journey.

---

## See Also

- **Agent Definition:** `.claude/agents/cocotb-progressive-test-runner/agent.md`
- **Testing Standards:** `docs/PROGRESSIVE_TESTING_GUIDE.md`
- **CocoTB Infrastructure:** `python/forge_cocotb/test_base.py`
- **Hybrid Workflow:** `CLAUDE.md` (Hybrid Workflow section)

---

**Last Updated:** 2025-11-09
**Version:** 1.0.0
**Audience:** Users, reviewers, developers understanding agent behavior
