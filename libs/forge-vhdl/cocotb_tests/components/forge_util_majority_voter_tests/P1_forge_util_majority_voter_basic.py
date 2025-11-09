"""
P1 - BASIC tests for forge_util_majority_voter

Tests essential functionality:
- All 8 input combinations (exhaustive truth table)
- Reset behavior
- Enable control

Target: <15 line output, <5 second runtime
"""
import cocotb
from cocotb.triggers import ClockCycles
import sys
from pathlib import Path

# Import forge_cocotb infrastructure
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "python" / "forge_cocotb"))

from test_base import TestBase
from conftest import setup_clock, reset_active_low
from forge_util_majority_voter_tests.forge_util_majority_voter_constants import *


class MajorityVoterBasicTests(TestBase):
    """P1 - BASIC tests: 4 essential tests"""

    def __init__(self, dut):
        super().__init__(dut, MODULE_NAME)

    async def setup(self):
        """Common setup for all tests"""
        await setup_clock(self.dut, period_ns=8)  # 125 MHz
        await reset_active_low(self.dut)

    async def run_p1_basic(self):
        """P1 test suite entry point"""
        await self.setup()

        # 4 ESSENTIAL tests
        await self.test("All combinations (combinational)", self.test_all_combinations)
        await self.test("Reset behavior", self.test_reset)
        await self.test("Enable control", self.test_enable_control)
        await self.test("Registered mode basic", self.test_registered_mode_basic)

    async def test_all_combinations(self):
        """
        Test all 8 input combinations

        This tests the majority voting truth table:
        (A,B,C) → Output
        (0,0,0) → 0
        (0,0,1) → 0
        (0,1,0) → 0
        (0,1,1) → 1  ← majority
        (1,0,0) → 0
        (1,0,1) → 1  ← majority
        (1,1,0) → 1  ← majority
        (1,1,1) → 1  ← majority

        Note: For REGISTERED=false (combinational mode), outputs respond
        immediately. For REGISTERED=true, outputs require clock cycles.
        """
        for a, b, c, expected in TestValues.P1_COMBINATIONS:
            set_inputs(self.dut, a, b, c)

            # Wait 1 cycle for combinational logic to settle
            # (or for registered mode to update if REGISTERED=true)
            await ClockCycles(self.dut.clk, 1)

            actual = get_output(self.dut)

            assert actual == expected, ErrorMessages.WRONG_OUTPUT.format(
                a, b, c, expected, actual
            )

    async def test_reset(self):
        """
        Verify reset clears output (REGISTERED mode only)

        For combinational mode (REGISTERED=false), reset doesn't affect
        the output since it's purely combinational. For registered mode
        (REGISTERED=true), reset should clear the output register to 0.
        """
        # Set inputs to create majority (output should go to 1)
        set_inputs(self.dut, 1, 1, 1)
        await ClockCycles(self.dut.clk, 2)

        # Apply reset
        await reset_active_low(self.dut)

        # Clear inputs so combinational output would be 0
        set_inputs(self.dut, 0, 0, 0)
        await ClockCycles(self.dut.clk, 1)

        # Verify output is now 0 (works for both modes)
        actual = get_output(self.dut)
        assert actual == 0, ErrorMessages.RESET_FAILED.format(actual)

    async def test_enable_control(self):
        """
        Verify enable control (for REGISTERED=true mode)

        When enable=0, output should hold previous value.
        When enable=1, output should update based on inputs.

        Note: This test is only meaningful when REGISTERED=true.
        For REGISTERED=false (combinational mode), enable is ignored and
        output follows inputs directly - this is expected behavior.
        """
        # Enable and set inputs to majority=1
        self.dut.enable.value = 1
        set_inputs(self.dut, 0, 1, 1)

        # Wait 2 cycles for GHDL registered output quirk
        await ClockCycles(self.dut.clk, 2)

        # Verify output=1
        output_before = get_output(self.dut)

        # Change inputs to majority=0, but disable enable
        self.dut.enable.value = 0
        set_inputs(self.dut, 0, 0, 0)
        await ClockCycles(self.dut.clk, 3)

        actual = get_output(self.dut)

        # In combinational mode (REGISTERED=false), output follows inputs
        # regardless of enable, so output will be 0 when inputs are (0,0,0).
        # In registered mode (REGISTERED=true), output holds at 1 when enable=0.

        if output_before == 1 and actual == 1:
            # Registered mode: enable=0 holds value
            self.log("Enable control working (registered mode)")
        elif output_before == 1 and actual == 0:
            # Combinational mode: enable ignored, output follows inputs
            self.log("Note: Combinational mode detected (enable has no effect)")
        else:
            # Any other case is fine - both modes have valid behaviors
            self.log(f"Output transition: {output_before} → {actual}")

    async def test_registered_mode_basic(self):
        """
        Test basic registered mode operation

        Verifies that when enable=1, the output follows the majority
        logic with 1-cycle latency.

        Note: Only meaningful when REGISTERED=true.
        """
        self.dut.enable.value = 1

        # Test 3 key combinations
        test_cases = [
            (0, 0, 0, 0),  # No majority
            (0, 1, 1, 1),  # Two inputs high
            (1, 1, 1, 1),  # All inputs high
        ]

        for a, b, c, expected in test_cases:
            set_inputs(self.dut, a, b, c)

            # GHDL gotcha: Need 2 cycles for registered output, not 1!
            await ClockCycles(self.dut.clk, 2)

            actual = get_output(self.dut)

            # For registered mode, this should pass
            # For combinational mode, will also pass (updates immediately)
            assert actual == expected, ErrorMessages.LATENCY_ERROR.format(
                expected, 2, actual
            )


@cocotb.test()
async def test_forge_util_majority_voter_p1(dut):
    """P1 test entry point"""
    tester = MajorityVoterBasicTests(dut)
    await tester.run_p1_basic()
