# CocoTB Progressive Test Runner

Quick reference for the test execution agent.

## Purpose

Implement and execute CocoTB tests for forge-vhdl components (utilities, packages, debugging modules).

## What This Agent Does

✅ **Implements** Python test code from design specs
✅ **Executes** tests via CocoTB + GHDL
✅ **Debugs** test failures (signal access, timing, GHDL errors)
✅ **Iterates** on implementation until tests pass
✅ **Validates** output quality (<20 lines P1)

## What This Agent Does NOT Do

❌ **Design test architecture** - Receive from cocotb-progressive-test-designer
❌ **Write production VHDL** - Only test wrappers
❌ **Integration testing** - Delegate to cocotb-integration-test
❌ **Redesign test strategy** - Follow designer's plan

## Usage

```bash
# Receive test design from designer agent
# Implement: Constants, P1 tests, orchestrator, test_configs.py entry
# Execute from monorepo root: uv run python libs/forge-vhdl/cocotb_test/run.py <component>
# Debug: Fix failures, iterate until all green
# Commit: After each fix/milestone (incremental commits, echo to files)
```

## Critical Constraints

**Python Environment:**
- ALWAYS use top-level `uv` workspace (from monorepo root)
- Never cd into submodules or use local python interpreters

**Git Strategy:**
- Commit after each test implementation, bug fix, or milestone
- Write commit messages to files, display to user (token-efficient)
- User likes watching git log for progress

**Execution Pattern:**
```bash
# From monorepo root only!
uv run python libs/forge-vhdl/cocotb_test/run.py <component>
```

## Key Responsibilities

1. **Constants file** - Implement from design spec
2. **P1 test module** - Implement test methods
3. **Progressive orchestrator** - Standard pattern
4. **test_configs.py entry** - Add component
5. **Test execution** - Run and debug
6. **Output validation** - Ensure <20 lines

## Common Debugging

**Signed integer access:**
```python
# ✅ CORRECT
output = int(dut.voltage_out.value.signed_integer)
```

**Integer division:**
```python
# ✅ CORRECT (match VHDL truncation)
offset = (value * 100) // 128
```

**Reset polarity:**
```python
# Check VHDL: reset='1' or rst_n='0'?
await reset_active_high(dut)  # or reset_active_low(dut)
```

## Exit Criteria

- [ ] All P1 tests pass (green)
- [ ] Output <20 lines
- [ ] Runtime <5 seconds
- [ ] No GHDL errors/warnings

## See Also

- `agent.md` - Full agent specification
- `libs/forge-vhdl/CLAUDE.md` - Testing standards
- `libs/forge-vhdl/docs/COCOTB_TROUBLESHOOTING.md` - Debugging guide
