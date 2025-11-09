# CocoTB Tests Directory

**Where you are:** `/cocotb_tests/`
**Purpose:** Progressive test suite for VHDL components

## What Should Be Here

This directory contains the progressive testing framework (P1/P2/P3) for all VHDL components:

```
cocotb_tests/
├── run.py                      # Test runner with GHDL filtering
├── test_forge_util_*.py        # Component tests
├── test_forge_voltage_*.py     # Package tests
├── test_forge_lut_pkg.py       # LUT tests
└── README.md                   # This file
```

## Progressive Testing Levels

| Level | Tests | Output | Runtime | Purpose |
|-------|-------|--------|---------|---------|
| **P1** | 2-4 | <20 lines | <5 sec | Fast iteration (DEFAULT) |
| **P2** | 5-10 | <50 lines | <30 sec | Standard validation |
| **P3** | 15-25 | <100 lines | <2 min | Full coverage |
| **P4** | Unlimited | No limit | No limit | Debug mode |

## Running Tests

```bash
# Run P1 tests (default)
uv run python run.py forge_util_clk_divider

# Run P2 tests
TEST_LEVEL=P2_INTERMEDIATE uv run python run.py forge_util_clk_divider

# Run P3 tests
TEST_LEVEL=P3_COMPREHENSIVE uv run python run.py forge_util_clk_divider

# Debug mode (full output)
GHDL_FILTER_LEVEL=none uv run python run.py forge_util_clk_divider

# List all available tests
uv run python run.py --list

# Run all tests
uv run python run.py --all
```

## Key Innovation

**98% output reduction** via GHDL filtering:
- Raw GHDL output: 287 lines
- Filtered P1 output: <20 lines
- Optimized for AI token usage

## Test File Structure

Each test file follows this pattern:
```python
import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb.clock import Clock

@cocotb.test()
async def test_p1_reset(dut):
    """P1: Verify reset behavior"""
    # Minimal test - core functionality only

@cocotb.test()
async def test_p2_edge_case(dut):
    """P2: Test boundary conditions"""
    # Additional coverage
```

## Navigation

- **Up:** Go to repository root
- **VHDL:** See `/vhdl/` for components being tested
- **Docs:** See `/docs/PROGRESSIVE_TESTING_GUIDE.md` for patterns
- **Troubleshooting:** See `/docs/COCOTB_TROUBLESHOOTING.md`

## AI Agent Notes

When writing tests:
1. P1 tests must output <20 lines total
2. Use descriptive test names (test_p1_*, test_p2_*)
3. Check existing tests for patterns
4. Verify filtering with `wc -l` after running

## Common Issues

**Issue:** Test output >20 lines for P1
**Solution:** Check GHDL_FILTER_LEVEL=aggressive is set

**Issue:** 'HierarchyObject' has no attribute 'value'
**Solution:** VHDL types like `real` need wrapper - see troubleshooting guide

**Issue:** Tests not found
**Solution:** Ensure test file named `test_*.py` and contains `@cocotb.test()` decorators