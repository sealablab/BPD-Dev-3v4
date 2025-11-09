# forge_cocotb - CocoTB Progressive Testing Framework

Python framework for LLM-friendly VHDL testing with token-efficient output.

## Key Innovation

**98% test output reduction** (287 lines → 8 lines)
- GHDL output filtering
- Progressive test levels (P1/P2/P3)
- Verbosity control

## Components

**test_base.py**
- `TestBase` class - Progressive test harness
- Automatic verbosity control based on test level
- Test result collection and formatting

**runner.py**
- CocoTB test runner with GHDL integration
- Automatic HDL source discovery
- Test configuration management

**ghdl_filter.py**
- GHDL output filtering (aggressive/normal/minimal/none)
- Filters metavalue warnings, duplicates, internal messages
- Preserves errors, failures, assertions

**mcc_utils.py**
- FORGE control scheme helpers
- Control Register bit manipulation
- `ForgeControlBits` constants (FORGE_READY, USER_ENABLED, FULLY_ENABLED)

**conftest.py**
- CocoTB fixtures: `setup_clock()`, `reset_active_low()`
- Common test utilities

## Usage

```python
from forge_cocotb.test_base import TestBase
from forge_cocotb.conftest import setup_clock, reset_active_low

class MyComponentTests(TestBase):
    def __init__(self, dut):
        super().__init__(dut, "my_component")

    async def run_p1_basic(self):
        await self.test("Reset", self.test_reset)
        await self.test("Basic operation", self.test_basic)

    async def test_reset(self):
        await reset_active_low(self.dut)
        assert int(self.dut.output.value) == 0
```

## Progressive Test Levels

**P1 - BASIC** (Default)
- 3-5 essential tests
- <20 line output, <100 tokens
- Fast iteration for LLM development

**P2 - INTERMEDIATE**
- 10-15 tests with edge cases
- <50 line output

**P3 - COMPREHENSIVE**
- 20-30 tests, full coverage
- Production readiness validation

See `docs/COCOTB_GUIDE.md` for complete testing patterns.
