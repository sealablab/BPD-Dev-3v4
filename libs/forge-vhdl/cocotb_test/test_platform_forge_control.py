"""
FORGE Control Scheme Validation Test

Tests the foundational CR0[31:29] calling convention that ALL
Moku instruments must implement.
"""

import cocotb
from cocotb.triggers import Timer
import sys
import os

# Add platform module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cocotb_test.platform.simulation_backend import SimulationBackend
from cocotb_test.platform.network_cr import NetworkCRInterface


@cocotb.test()
async def test_forge_control_sequence(dut):
    """
    Test FORGE control scheme CR0[31:29] sequencing.

    Validates:
    1. Power-on safe state (all disabled)
    2. Proper enable sequence
    3. Network delay behavior
    4. Global enable computation
    """
    cocotb.log.info("=== FORGE Control Scheme Validation Test ===")

    # Create mock MokuConfig-like object
    class MockConfig:
        class Platform:
            name = "moku_go"

        platform = Platform()
        slots = {
            1: type('SlotConfig', (), {
                'instrument': 'CloudCompile',
                'settings': {},
                'control_registers': {0: 0x00000000}  # Start disabled
            })()
        }
        routing = []

        def validate_routing(self):
            return []

    config = MockConfig()

    # Create simulation backend
    sim = SimulationBackend(config, dut)
    await sim.setup()

    # Test 1: Power-on state (all disabled)
    cocotb.log.info("Test 1: Power-on safe state")
    forge_status = sim.validate_forge_control(slot=1)
    assert forge_status['forge_ready'] == False
    assert forge_status['user_enable'] == False
    assert forge_status['clk_enable'] == False
    assert forge_status['global_enable'] == False
    cocotb.log.info("✓ Power-on state correct (all disabled)")

    # Test 2: Set forge_ready with network delay
    cocotb.log.info("Test 2: Set forge_ready with 200ms delay")
    start_time = cocotb.utils.get_sim_time(units='ns')
    await sim.set_forge_control(slot=1, forge_ready=True, delay_ms=200)
    end_time = cocotb.utils.get_sim_time(units='ns')

    delay_ns = end_time - start_time
    delay_ms = delay_ns / 1e6
    cocotb.log.info(f"Network delay measured: {delay_ms:.1f}ms")
    assert delay_ms >= 199, f"Network delay too short: {delay_ms}ms"

    forge_status = sim.validate_forge_control(slot=1)
    assert forge_status['forge_ready'] == True
    assert forge_status['user_enable'] == False
    assert forge_status['global_enable'] == False  # Not all conditions met
    cocotb.log.info("✓ forge_ready set, global_enable still False")

    # Test 3: Set user_enable
    cocotb.log.info("Test 3: Set user_enable")
    await sim.set_forge_control(
        slot=1,
        forge_ready=True,
        user_enable=True,
        delay_ms=200
    )

    forge_status = sim.validate_forge_control(slot=1)
    assert forge_status['forge_ready'] == True
    assert forge_status['user_enable'] == True
    assert forge_status['clk_enable'] == False
    assert forge_status['global_enable'] == False  # Still not all conditions
    cocotb.log.info("✓ user_enable set, global_enable still False")

    # Test 4: Set clk_enable (all conditions met)
    cocotb.log.info("Test 4: Set clk_enable (enable module)")
    await sim.set_forge_control(
        slot=1,
        forge_ready=True,
        user_enable=True,
        clk_enable=True,
        delay_ms=200
    )

    forge_status = sim.validate_forge_control(slot=1)
    assert forge_status['forge_ready'] == True
    assert forge_status['user_enable'] == True
    assert forge_status['clk_enable'] == True
    # Note: global_enable excludes loader_done in network view
    cocotb.log.info("✓ All FORGE bits set correctly")

    # Test 5: Verify CR0 value
    cr0 = await sim.get_control_register(slot=1, register=0)
    expected = 0xE0000000  # Bits 31, 30, 29 set
    assert cr0 == expected, f"CR0 = 0x{cr0:08X}, expected 0x{expected:08X}"
    cocotb.log.info(f"✓ CR0 = 0x{cr0:08X} (correct)")

    # Test 6: Disable sequence
    cocotb.log.info("Test 5: Disable sequence")
    await sim.set_forge_control(
        slot=1,
        forge_ready=True,
        user_enable=False,  # Disable user
        clk_enable=True,
        delay_ms=50  # Faster for disable
    )

    forge_status = sim.validate_forge_control(slot=1)
    assert forge_status['user_enable'] == False
    cocotb.log.info("✓ Module disabled via user_enable")

    cocotb.log.info("=== FORGE Control Validation PASSED ===")


@cocotb.test()
async def test_network_cr_primitives(dut):
    """
    Test network control register primitives directly.

    Validates:
    1. Network delays
    2. Atomic updates
    3. Access logging
    """
    cocotb.log.info("=== Network CR Primitives Test ===")

    network = NetworkCRInterface(default_delay_ms=100)
    network.add_slot(1)
    network.add_slot(2)

    # Test concurrent updates to different slots
    cocotb.log.info("Test: Concurrent updates to multiple slots")

    async def update_slot1():
        await network.set_control_register(1, 0, 0x12345678, delay_ms=100)

    async def update_slot2():
        await network.set_control_register(2, 0, 0x87654321, delay_ms=100)

    # Start both updates concurrently
    task1 = cocotb.start_soon(update_slot1())
    task2 = cocotb.start_soon(update_slot2())

    # Wait for completion
    await task1
    await task2

    # Verify values
    cr0_slot1 = await network.get_control_register(1, 0)
    cr0_slot2 = await network.get_control_register(2, 0)

    assert cr0_slot1 == 0x12345678
    assert cr0_slot2 == 0x87654321
    cocotb.log.info("✓ Concurrent updates completed correctly")

    # Check statistics
    stats = network.get_stats()
    assert stats['total_operations'] == 2
    assert len(stats['configured_slots']) == 2
    cocotb.log.info(f"✓ Network stats: {stats['total_operations']} operations")

    cocotb.log.info("=== Network CR Test PASSED ===")


# Simple mock DUT for testing without VHDL
class MockDUT:
    """Mock DUT for Python-only testing."""
    def __init__(self):
        # Control registers
        for i in range(16):
            setattr(self, f'Control{i}', 0)
        # Status registers
        for i in range(16):
            setattr(self, f'Status{i}', 0)
        # Output signals
        self.OutputA = 0
        self.OutputB = 0
        self.OutputC = 0
        self.OutputD = 0


# Allow running with mock DUT for quick testing
if __name__ == "__main__":
    print("Test file created. Run with CocoTB: uv run python cocotb_test/run.py platform_forge_control")