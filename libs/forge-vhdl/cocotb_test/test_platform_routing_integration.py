"""
Platform Routing Integration - CocoTB Progressive Tests

Validates 2-slot signal routing with oscilloscope capture of externally routed signals.

Test Strategy:
- Slot 2: CloudCompile with forge_counter_with_encoder DUT (OutputD)
- Slot 1: Oscilloscope configured to capture InputA
- Routing: Slot2OutD → Slot1InA (BPD-Debug-Bus pattern)
- Oscilloscope captures routed signal (not direct DUT access)
- Decode hierarchical voltage from routed channel to verify state progression

Test Levels:
- P1: 2 essential tests (routing validation, capture verification)
- P2: 5-7 tests (P1 + edge cases, multi-channel routing)
- P3: 10+ tests (P1+P2 + stress, routing matrix edge cases)

Run from libs/forge-vhdl/:
    uv run python cocotb_test/run.py platform_routing_integration
"""

import cocotb
from cocotb.triggers import ClockCycles
import sys
from pathlib import Path

# Add forge_cocotb to path
FORGE_VHDL = Path(__file__).parent.parent
sys.path.insert(0, str(FORGE_VHDL))

from forge_cocotb.test_base import TestBase
from forge_cocotb.conftest import setup_clock, reset_active_low
from test_platform_routing_integration_constants import *

# Import platform infrastructure
from platform.simulation_backend import SimulationBackend
from moku_models import MokuConfig, SlotConfig, MokuConnection, MOKU_GO_PLATFORM


class PlatformRoutingIntegrationTests(TestBase):
    """P1 - BASIC tests: Validate 2-slot routing with oscilloscope capture"""

    def __init__(self, dut):
        super().__init__(dut, MODULE_NAME)
        self.backend = None
        self.oscilloscope = None

    async def setup(self):
        """Common setup for all tests"""
        await setup_clock(self.dut, period_ns=8)  # 125 MHz
        await reset_active_low(self.dut)

        # Create 2-slot MokuConfig with routing
        # Slot 2: CloudCompile with counter DUT
        # Slot 1: Oscilloscope capturing routed signal
        self.moku_config = MokuConfig(
            platform=MOKU_GO_PLATFORM,
            slots={
                2: SlotConfig(
                    instrument='CloudCompile',
                    control_registers={
                        0: ForgeControlBits.POWER_ON | (TestValues.P1_COUNTER_MAX & 0x3F)
                    }
                ),
                1: SlotConfig(
                    instrument='Oscilloscope',
                    settings={
                        'channels': ['InputA'],  # Capture routed signal
                        'sample_rate': TestValues.SAMPLE_RATE,
                        'decimation': TestValues.DECIMATION
                    }
                )
            },
            routing=[
                MokuConnection(source='Slot2OutD', destination='Slot1InA')
            ]
        )

        # Create simulation backend
        self.backend = SimulationBackend(self.moku_config, self.dut)
        await self.backend.setup()

        # Get oscilloscope reference
        self.oscilloscope = self.backend.get_instrument(1)

    # ========================================================================
    # P1 - BASIC Tests (2 tests, <20 lines)
    # ========================================================================

    async def run_p1_basic(self):
        """P1 test suite entry point"""
        await self.setup()

        # 2 ESSENTIAL tests
        await self.test("2-slot routing configuration", self.test_routing_configuration)
        await self.test("Routed signal capture and decode", self.test_routed_signal_capture)

    async def test_routing_configuration(self):
        """
        Test 1: Validate routing infrastructure configuration

        Verify:
        1. Routing matrix contains Slot2OutD->Slot1InA
        2. Oscilloscope has external channel 'InputA'
        3. External channel is wired to DUT.OutputD signal handle
        """
        # Verify routing matrix populated
        routing_key = 'Slot2OutD->Slot1InA'
        assert routing_key in self.backend.routing_matrix, \
            ErrorMessages.ROUTING_NOT_APPLIED.format(routing_key)

        # Verify oscilloscope has external channel
        assert 'InputA' in self.oscilloscope.external_channels, \
            ErrorMessages.EXTERNAL_CHANNEL_MISSING.format('InputA')

        # Verify external channel is wired to DUT signal handle (NOT value copy)
        external_signal = self.oscilloscope.external_channels['InputA']
        dut_signal = self.dut.OutputD

        # Both should be the same signal handle object
        assert external_signal is dut_signal, \
            ErrorMessages.SIGNAL_HANDLE_NOT_WIRED.format('InputA', 'OutputD')

        # Verify oscilloscope channels list includes InputA
        assert 'InputA' in self.oscilloscope.channels, \
            "InputA not in oscilloscope channels list"

    async def test_routed_signal_capture(self):
        """
        Test 2: Validate end-to-end routed signal capture and decoding

        Verify:
        1. Enable counter via FORGE control sequence
        2. Oscilloscope captures from routed InputA channel (not direct OutputD)
        3. Decode hierarchical voltage to extract state
        4. Verify state progression: 0→1→2→...→15
        """
        # Enable counter via backend (CloudCompile slot)
        await self.backend.set_forge_control(
            slot=2,
            forge_ready=True,
            user_enable=True,
            clk_enable=True,
            delay_ms=0  # No network delay in simulation
        )
        await ClockCycles(self.dut.clk, 2)  # Wait for enable to propagate

        # Run backend for capture duration (oscilloscope runs concurrently)
        duration_ms = TestValues.P1_CAPTURE_DURATION_NS / 1e6
        await self.backend.run(duration_ms=duration_ms)

        # Get captured data from oscilloscope (via InputA, not OutputD!)
        all_data = self.oscilloscope.get_data('InputA')
        data = all_data['InputA']  # Extract channel data from dict
        values = data['values']
        sample_count = data['sample_count']

        # Verify samples captured
        assert sample_count > 0, ErrorMessages.NO_SAMPLES_CAPTURED
        assert sample_count >= TestValues.MIN_SAMPLES, \
            ErrorMessages.INSUFFICIENT_SAMPLES.format(TestValues.MIN_SAMPLES, sample_count)

        # Decode hierarchical voltages to extract states
        states = []
        for voltage in values:
            state = decode_state_from_voltage(voltage)
            if 0 <= state <= TestValues.P1_COUNTER_MAX:  # Valid state range
                states.append(state)

        # Verify we captured multiple different states
        unique_states = set(states)
        assert len(unique_states) >= TestValues.MIN_UNIQUE_STATES, \
            ErrorMessages.INSUFFICIENT_STATE_PROGRESSION.format(
                TestValues.MIN_UNIQUE_STATES,
                len(unique_states)
            )

        # Verify states are in valid range
        for state in unique_states:
            assert 0 <= state <= TestValues.P1_COUNTER_MAX, \
                ErrorMessages.INVALID_STATE_RANGE.format(state, TestValues.P1_COUNTER_MAX)


# ============================================================================
# Helper Functions
# ============================================================================

def decode_state_from_voltage(voltage: int) -> int:
    """
    Decode state from hierarchical voltage encoding.

    Encoding: voltage = state × 200 + status_offset
    For state extraction, divide by 200 (ignoring status offset).

    Args:
        voltage: Signed 16-bit voltage value

    Returns:
        Decoded state (0-63)
    """
    # Handle negative voltages (fault condition)
    if voltage < 0:
        voltage = abs(voltage)

    # Extract base state (divide by DIGITAL_UNITS_PER_STATE)
    state = voltage // EncodingConstants.DIGITAL_UNITS_PER_STATE
    return max(0, min(state, 63))  # Clamp to valid range


@cocotb.test()
async def test_platform_routing_integration_p1(dut):
    """P1 test entry point (called by CocoTB)"""
    tester = PlatformRoutingIntegrationTests(dut)
    await tester.run_p1_basic()
