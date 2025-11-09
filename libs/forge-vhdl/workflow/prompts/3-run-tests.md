# Agent 3: Test Implementation & Execution Prompt

**Copy-paste this into Claude Code to implement and run tests:**

---

Read the test strategy at `workflow/artifacts/tests/test_strategy.md` and implement CocoTB progressive tests:

**Requirements:**
- Implement Python test code from designer's architecture
- Create constants file (`[component]_constants.py`)
- Create P1 test module (`P1_[component]_basic.py`)
- Create test orchestrator (`test_[component]_progressive.py`)
- Follow CocoTB progressive testing pattern
- Use TestBase class for verbosity control

**File Structure:**
```
workflow/artifacts/tests/[component]_tests/
├── __init__.py
├── [component]_constants.py
├── P1_[component]_basic.py
└── test_[component]_progressive.py (orchestrator)
```

**Test Execution:**
After implementation, run P1 tests:
```bash
cd workflow/artifacts/tests
uv run python -m pytest test_[component]_progressive.py::test_p1
```

**Expected Output:**
- <20 lines (GHDL filter applied)
- All tests PASS
- Verify expected values match VHDL behavior

**Output:**
Save test files to: `workflow/artifacts/tests/[component]_tests/`

**Debugging:**
If tests fail:
1. Check GHDL output for errors
2. Verify expected value calculations
3. Check signal access patterns (`.signed_integer` for signed types)
4. Verify 2-cycle waits for registered outputs

---

**Note:** Replace `[component]` with actual component name.

**Example usage:**
```
Read workflow/artifacts/tests/test_strategy.md and implement CocoTB
progressive tests as described above. Then run P1 tests and report results.
```
