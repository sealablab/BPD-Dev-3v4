"""
P1 - Basic Tests for forge_hierarchical_encoder

Minimal, fast tests with reduced verbosity for LLM-friendly output.
These tests verify core functionality with small values and minimal logging.

Test Coverage:
1. Reset behavior
2. State progression (0→1→2→3)
3. Status offset encoding
4. Fault detection (sign flip)

Author: Moku Instrument Forge Team
Date: 2025-11-07
"""

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import setup_clock, reset_active_high
from test_base import TestBase, TestLevel, VerbosityLevel
from forge_hierarchical_encoder_tests.forge_hierarchical_encoder_constants import *


class ForgeHierarchicalEncoderBasicTests(TestBase):
    """P1 - Basic tests for forge_hierarchical_encoder module"""

    def __init__(self, dut):
        super().__init__(dut, MODULE_NAME)

    async def setup(self):
        """Common setup for all tests"""
        await setup_clock(self.dut)
        self.dut.state_vector.value = 0
        self.dut.status_vector.value = 0x00

    async def run_p1_basic(self):
        """Run all P1 basic tests"""
        await self.setup()

        # Test 1: Reset behavior
        await self.test("Reset behavior", self.test_reset)

        # Test 2: State progression
        await self.test("State progression", self.test_state_progression)

        # Test 3: Status offset encoding
        await self.test("Status offset encoding", self.test_status_offset)

        # Test 4: Fault detection (sign flip)
        await self.test("Fault detection (sign flip)", self.test_fault_sign_flip)

    async def test_reset(self):
        """Test reset drives output to 0."""
        await reset_active_high(self.dut, rst_signal="reset")
        await ClockCycles(self.dut.clk, 2)  # GHDL needs 2 cycles for registered outputs

        actual = int(self.dut.voltage_out.value.signed_integer)
        assert actual == 0, ErrorMessages.RESET_OUTPUT.format(actual)

        self.log("Reset: voltage_out=0", VerbosityLevel.VERBOSE)

    async def test_state_progression(self):
        """Test state 0→1→2→3 produces 0→200→400→600 digital units."""
        await reset_active_high(self.dut, rst_signal="reset")

        for state in TestValues.P1_STATES:
            self.dut.state_vector.value = state
            self.dut.status_vector.value = 0x00
            await ClockCycles(self.dut.clk, 2)  # GHDL needs 2 cycles for registered outputs

            expected = TestValues.calculate_expected_digital(state, 0x00)
            actual = int(self.dut.voltage_out.value.signed_integer)

            assert actual == expected, ErrorMessages.STATE_PROGRESSION.format(
                state, expected, actual
            )

        self.log(f"State progression: 0→200→400→600 digital units", VerbosityLevel.VERBOSE)

    async def test_status_offset(self):
        """Test status encoding (state=2, status 0x00 vs 0x7F)."""
        await reset_active_high(self.dut, rst_signal="reset")

        state = 2

        # Test status=0x00 (no offset)
        self.dut.state_vector.value = state
        self.dut.status_vector.value = 0x00
        await ClockCycles(self.dut.clk, 2)  # GHDL needs 2 cycles for registered outputs

        expected_no_offset = TestValues.calculate_expected_digital(state, 0x00)
        actual_no_offset = int(self.dut.voltage_out.value.signed_integer)
        assert actual_no_offset == expected_no_offset, ErrorMessages.STATUS_OFFSET_NO_OFFSET.format(
            state, expected_no_offset, actual_no_offset
        )

        # Test status=0x7F (max offset)
        self.dut.status_vector.value = 0x7F
        await ClockCycles(self.dut.clk, 2)  # GHDL needs 2 cycles for registered outputs

        expected_max_offset = TestValues.calculate_expected_digital(state, 0x7F)
        actual_max_offset = int(self.dut.voltage_out.value.signed_integer)
        assert actual_max_offset == expected_max_offset, ErrorMessages.STATUS_OFFSET_MAX_OFFSET.format(
            state, expected_max_offset, actual_max_offset
        )

        # Verify offset is positive (status adds to base)
        assert actual_max_offset > actual_no_offset, ErrorMessages.STATUS_OFFSET_DIRECTION.format(
            actual_no_offset, actual_max_offset
        )

        self.log(f"Status offset: {actual_no_offset} → {actual_max_offset}", VerbosityLevel.VERBOSE)

    async def test_fault_sign_flip(self):
        """Test fault flag (status[7]) flips sign."""
        await reset_active_high(self.dut, rst_signal="reset")

        state = 2

        # Normal (status[7]=0)
        self.dut.state_vector.value = state
        self.dut.status_vector.value = 0x00
        await ClockCycles(self.dut.clk, 2)  # GHDL needs 2 cycles for registered outputs

        normal_output = int(self.dut.voltage_out.value.signed_integer)
        assert normal_output > 0, ErrorMessages.FAULT_NORMAL_SIGN.format(normal_output)

        # Fault (status[7]=1)
        self.dut.status_vector.value = 0x80
        await ClockCycles(self.dut.clk, 2)  # GHDL needs 2 cycles for registered outputs

        fault_output = int(self.dut.voltage_out.value.signed_integer)
        assert fault_output < 0, ErrorMessages.FAULT_FLAG_SIGN.format(fault_output)

        # Magnitude should be preserved
        assert abs(fault_output) == abs(normal_output), ErrorMessages.FAULT_MAGNITUDE.format(
            normal_output, fault_output
        )

        self.log(f"Fault sign flip: {normal_output} → {fault_output}", VerbosityLevel.VERBOSE)


# CocotB test entry point
@cocotb.test()
async def test_forge_hierarchical_encoder_p1(dut):
    """P1 - Basic forge_hierarchical_encoder tests"""
    tester = ForgeHierarchicalEncoderBasicTests(dut)
    await tester.run_all_tests()
